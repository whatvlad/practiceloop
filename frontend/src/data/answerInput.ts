import text from '../../../backend/app/content/en.json';
import type { AnswerInputSpec, ComputationalInputSpec } from './types';

export const COMPUTATIONAL_KINDS = ['real_set', 'tuple', 'category', 'formula', 'limit_result', 'logic'] as const;
const SYMBOL_NAMES = ['x', 'y', 'z', 'r', 'theta', 'a', 'b', 'c', 'C', 'D', 'k', 'n', 't', 's'];

function computational(value: unknown, depth = 0, count = { value: 0 }): ComputationalInputSpec {
  count.value += 1;
  if (depth > 3 || count.value > 16 || !value || typeof value !== 'object' || Array.isArray(value)) throw new Error(text.service_error);
  const data = value as Record<string, unknown>;
  if (!(COMPUTATIONAL_KINDS as readonly unknown[]).includes(data.kind) || data.maxBytes !== 256) throw new Error(text.service_error);
  const result: ComputationalInputSpec = { kind: data.kind as ComputationalInputSpec['kind'], maxBytes: 256 };
  if (data.kind === 'real_set') {
    if (data.maxItems !== 8) throw new Error(text.service_error);
    result.maxItems = 8;
  }
  if (data.kind === 'formula' && data.symbols !== undefined) {
    if (!data.symbols || typeof data.symbols !== 'object' || Array.isArray(data.symbols)) throw new Error(text.service_error);
    const symbols = Object.entries(data.symbols);
    if (symbols.length > 8 || symbols.some(([name, domain]) => !SYMBOL_NAMES.includes(name) || !['real', 'positive', 'integer'].includes(domain))) throw new Error(text.service_error);
    result.symbols = Object.fromEntries(symbols);
  }
  if (data.kind === 'category') {
    if (!Array.isArray(data.choices) || data.choices.length < 2 || data.choices.length > 8 || new Set(data.choices).size !== data.choices.length
        || data.choices.some(x => typeof x !== 'string' || !/^[a-z][a-z_]{0,31}$/.test(x))) throw new Error(text.service_error);
    result.choices = [...data.choices];
  }
  if (data.kind === 'tuple') {
    if (!Array.isArray(data.components) || !Array.isArray(data.labels) || data.components.length < 1 || data.components.length > 8
        || data.labels.length !== data.components.length || data.labels.some(x => typeof x !== 'string' || !/^[A-Za-z][A-Za-z -]{0,39}$/.test(x))) throw new Error(text.service_error);
    result.components = data.components.map(x => computational(x, depth + 1, count));
    result.labels = [...data.labels];
  }
  if (data.kind === 'logic') {
    if (!Array.isArray(data.choices) || data.choices.length < 1 || data.choices.length > 3 || new Set(data.choices).size !== data.choices.length
        || data.choices.some(x => !['p', 'q', 'r'].includes(x))) throw new Error(text.service_error);
    result.choices = [...data.choices];
  }
  return result;
}

/** Explicit safe projection; no expected values are kept from an API response. */
export function parseAnswerInput(value: unknown): AnswerInputSpec | undefined {
  if (value === undefined) return undefined;
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(text.service_error);
  const data = value as Record<string, unknown>;
  if ((COMPUTATIONAL_KINDS as readonly unknown[]).includes(data.kind)) return computational(data);
  if (!['boolean', 'finite_set', 'interval'].includes(data.kind as string) || data.maxBytes !== 256
      || (data.kind === 'finite_set' && data.maxItems !== 8)) throw new Error(text.service_error);
  return { kind: data.kind as AnswerInputSpec['kind'], maxBytes: 256, ...(data.kind === 'finite_set' ? { maxItems: 8 as const } : {}) };
}
