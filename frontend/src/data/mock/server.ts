// TEMPORARY STUB that plays the backend and Supabase for the design build.
// Replace it by pointing ../api.ts at the real FastAPI routes (docs/api/README.md).
// It answers with public shapes only; the answer and solution leave this
// module only through revealAnswer and revealSolution, as the API will.

import type {
  Account,
  CheckResult,
  Difficulty,
  ProfileCounts,
  PublicProblem,
  RevealedAnswer,
  RevealedSolution,
  TopicSlug,
} from '../types';
import { BANK, type MockTemplate } from './bank';
import { check } from './checker';

interface StoredProblem {
  problem: PublicProblem;
  templateId: string;
  attempts: number;
}

interface State {
  signedIn: boolean;
  problems: StoredProblem[];
  lastSelection: { topic: TopicSlug; difficulty: Difficulty };
  nextId: number;
}

const STORAGE_KEY = 'practiceloop.mock.v1';
const ACCOUNT: Account = { name: 'Alex Morgan', email: 'alex@example.com', provider: 'Google' };
const MINUTE = 60_000;

function seed(now: number): State {
  const make = (
    id: number,
    templateId: string,
    difficulty: Difficulty,
    minutesAgo: number,
    lastResult: PublicProblem['lastResult'],
    flags: { answer?: boolean; solution?: boolean; lastAnswer?: string } = {},
  ): StoredProblem => {
    const template = templateById(templateId);
    return {
      templateId,
      attempts: lastResult ? 1 : 0,
      problem: {
        id: String(id),
        topic: template.topic,
        difficulty,
        problemLatex: template.problemLatex,
        createdAt: new Date(now - minutesAgo * MINUTE).toISOString(),
        answerRevealed: flags.answer ?? false,
        solutionRevealed: flags.solution ?? false,
        lastResult,
        lastAnswer: flags.lastAnswer ?? null,
      },
    };
  };
  return {
    signedIn: false,
    nextId: 6,
    lastSelection: { topic: 'substitution', difficulty: 3 },
    problems: [
      make(5, 'sub-cos', 3, 25, 'correct', { lastAnswer: 'sin(x^2) + C' }),
      make(4, 'parts-exp', 4, 53, 'incorrect', { answer: true, lastAnswer: 'x e^x + C' }),
      make(3, 'rational-partial', 4, 26 * 60, 'correct', { solution: true, lastAnswer: '1/2 ln|(x-1)/(x+1)| + C' }),
      make(2, 'trig-sin2', 3, 27 * 60, null),
      make(1, 'basic-power', 1, 4 * 24 * 60, 'correct', { lastAnswer: 'x^3 + C' }),
    ],
  };
}

function templateById(id: string): MockTemplate {
  const template = BANK.find((t) => t.id === id);
  if (!template) throw new Error(`Unknown mock template ${id}`);
  return template;
}

let state: State | null = null;

function load(): State {
  if (state) return state;
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw) state = JSON.parse(raw) as State;
  } catch {
    state = null;
  }
  state ??= seed(Date.now());
  return state;
}

function save(): void {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Storage can be unavailable (private mode, tests); the session stays in memory.
  }
}

function find(id: string): StoredProblem {
  const stored = load().problems.find((p) => p.problem.id === id);
  if (!stored) throw new NotFoundError();
  return stored;
}

function copy<T>(value: T): T {
  return structuredClone(value);
}

export class NotFoundError extends Error {
  constructor() {
    super('Problem not found');
    this.name = 'NotFoundError';
  }
}

export async function getAccount(): Promise<Account | null> {
  return load().signedIn ? copy(ACCOUNT) : null;
}

export async function signIn(): Promise<Account> {
  load().signedIn = true;
  save();
  return copy(ACCOUNT);
}

export async function signOut(): Promise<void> {
  load().signedIn = false;
  save();
}

export async function getProfileCounts(): Promise<ProfileCounts> {
  const problems = load().problems;
  return {
    generated: problems.length,
    attempted: problems.filter((p) => p.attempts > 0).length,
    correct: problems.filter((p) => p.problem.lastResult === 'correct').length,
  };
}

export async function listProblems(): Promise<PublicProblem[]> {
  return copy(load().problems.map((p) => p.problem));
}

export async function getProblem(id: string): Promise<PublicProblem> {
  return copy(find(id).problem);
}

export async function getLastSelection(): Promise<State['lastSelection']> {
  return copy(load().lastSelection);
}

export async function generateProblem(topic: TopicSlug, difficulty: Difficulty): Promise<PublicProblem> {
  const current = load();
  const candidates = BANK.filter((t) => t.topic === topic);
  const previous = current.problems.find((p) => p.problem.topic === topic)?.templateId;
  const template = candidates.find((t) => t.id !== previous) ?? candidates[0];
  if (!template) throw new Error(`No mock template for ${topic}`);
  const stored: StoredProblem = {
    templateId: template.id,
    attempts: 0,
    problem: {
      id: String(current.nextId),
      topic,
      difficulty,
      problemLatex: template.problemLatex,
      createdAt: new Date().toISOString(),
      answerRevealed: false,
      solutionRevealed: false,
      lastResult: null,
      lastAnswer: null,
    },
  };
  current.nextId += 1;
  current.problems.unshift(stored);
  current.lastSelection = { topic, difficulty };
  save();
  return copy(stored.problem);
}

export async function submitAttempt(id: string, answer: string): Promise<CheckResult> {
  const stored = find(id);
  const result = check(answer, templateById(stored.templateId).accepted);
  if (result !== 'invalid') {
    stored.attempts += 1;
    stored.problem.lastResult = result;
    stored.problem.lastAnswer = answer;
    save();
  }
  return result;
}

export async function revealAnswer(id: string): Promise<RevealedAnswer> {
  const stored = find(id);
  stored.problem.answerRevealed = true;
  save();
  return { answerLatex: templateById(stored.templateId).answerLatex };
}

export async function revealSolution(id: string): Promise<RevealedSolution> {
  const stored = find(id);
  stored.problem.solutionRevealed = true;
  save();
  return { steps: copy(templateById(stored.templateId).steps) };
}

/** Test helper: forget the in-memory session. */
export function resetMockServer(): void {
  state = null;
  try {
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}
