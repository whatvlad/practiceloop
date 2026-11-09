import { useEffect, useRef, useState } from 'react';
import text from '../../../backend/app/content/en.json';
import { Button } from '../components/Button';
import { DifficultyScale } from '../components/DifficultyScale';
import { initialMatrixOptions, matrixOptionsQuery, matrixOptionsValid, MatrixSettings } from '../components/MatrixSettings';
import { modulusModeQuery, type ModulusMode } from '../components/ModulusSettings';
import { generateProblem, getCatalogue, getLastSelection } from '../data/api';
import { mixedShares } from '../data/topics';
import type { AreaSlug, Difficulty, PracticeTopic } from '../data/types';
import { navigate } from '../router';
import { useLoad } from '../useLoad';

export function TopicPage({ initialArea, initialTopic }: { initialArea?: AreaSlug; initialTopic?: PracticeTopic } = {}) {
  const [catalogueRevision, setCatalogueRevision] = useState(0);
  const catalogue = useLoad(getCatalogue, String(catalogueRevision));
  const last = useLoad(getLastSelection);
  const [area, setArea] = useState<AreaSlug>(initialArea ?? 'mathematical-analysis');
  const [topic, setTopic] = useState<PracticeTopic>(initialTopic ?? 'basic-integrals');
  const [difficulty, setDifficulty] = useState<Difficulty>(1);
  const [matrixOptions, setMatrixOptions] = useState(() => initialMatrixOptions(1));
  const [modulusMode, setModulusMode] = useState<ModulusMode>('expression');
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const active = useRef(true);
  useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);
  const [error, setError] = useState('');
  const areas = catalogue.status === 'ready' ? catalogue.data.areas : [];
  // ADR-005: the learner picks an area first; topics and mixed practice belong to it.
  const topics = catalogue.status === 'ready' ? catalogue.data.topics.filter(t => t.area === area) : [];
  // Algebra's old server-side mixed pool still contains retired topics; the
  // workspace random selector draws only the learner's explicit choices.
  const mixed = area === 'algebra' ? null : areas.find(a => a.slug === area)?.mixed ?? null;
  const allLevels = topic === 'mixed' ? mixed?.availableDifficulties ?? [] : topics.find(t => t.slug === topic)?.availableDifficulties ?? [];
  const levels = topic === 'complex-numbers' && modulusMode ? allLevels.filter(level => level <= 3) : allLevels;
  const offered: PracticeTopic[] = [...topics.filter(t => t.availableDifficulties.length > 0).map(t => t.slug), ...(mixed ? ['mixed' as const] : [])];
  const available = levels.includes(difficulty);
  const selectedMatrixOptions = matrixOptionsValid(difficulty, matrixOptions) ? matrixOptions : initialMatrixOptions(difficulty);

  useEffect(() => {
    if (initialTopic || last.status !== 'ready' || catalogue.status !== 'ready') return;
    // A code/share can be opened before the topic catalogue was ever loaded.
    // Restore its authoritative area rather than the client's temporary fallback.
    const restoredTopic = catalogue.data.topics.find(entry => entry.slug === last.data.topic);
    setArea(restoredTopic?.area ?? last.data.area);
    setTopic(last.data.topic);
    setDifficulty(last.data.difficulty);
  }, [last, initialTopic, catalogue]);

  // An area the catalogue does not offer falls back to the first one it does.
  useEffect(() => {
    if (areas.length === 0 || areas.some(a => a.slug === area)) return;
    setArea(areas[0].slug);
  }, [areas, area]);

  // A topic outside the chosen area moves to the area's first topic.
  useEffect(() => {
    if (topics.length === 0 || offered.includes(topic)) return;
    setTopic(offered[0]);
  }, [topics, offered, topic]);

  // A topic shows only its own levels, so move a level it lacks to the nearest one it has.
  useEffect(() => {
    if (levels.length === 0 || levels.includes(difficulty)) return;
    setDifficulty(levels.reduce((best, level) => Math.abs(level - difficulty) < Math.abs(best - difficulty) ? level : best));
  }, [levels, difficulty]);

  async function generate() {
    if (pending.current || !available) return;
    pending.current = true;
    setError('');
    setBusy(true);
    try {
      const options = topic === 'matrix-operations' ? selectedMatrixOptions : undefined;
      const mode = topic === 'complex-numbers' ? modulusMode : undefined;
      const problem = await generateProblem(topic, difficulty, area, options, mode);
      if (active.current) navigate(`/practice?id=${encodeURIComponent(problem.id)}${options ? matrixOptionsQuery(options) : ''}${mode ? modulusModeQuery(mode) : ''}`);
    } catch (failure) {
      if (active.current) setError(failure instanceof Error ? failure.message : text.service_error);
    } finally {
      pending.current = false;
      if (active.current) setBusy(false);
    }
  }

  return (
    <main id="main" tabIndex={-1} className="pl-wrap pl-app-main">
      <div className="pl-label">{areas.find(a => a.slug === area)?.name ?? 'Practice'}</div>
      <h1 className="pl-display-md pl-page-title">{topic === 'mixed' ? 'Mixed practice' : topics.find(item => item.slug === topic)?.name ?? 'Practice'}</h1>
      <section className="pl-problem pl-problem--flat pl-mb-6" aria-labelledby="start-title">
        <div>
          <h2 id="start-title" className="pl-h-lg">
            Start a new problem
          </h2>
          <p className="pl-muted pl-mt-1">Select a difficulty, then generate. Other topics are in the list on the left.</p>
        </div>
        <div className="pl-stack pl-gap-3">
          <div id="difficulty-label" className="pl-label">
            Difficulty
          </div>
          <DifficultyScale selected={difficulty} onSelect={setDifficulty} labelledBy="difficulty-label" available={busy ? [] : levels} shown={levels} topic={topic} />
          {topic === 'matrix-operations' && <MatrixSettings level={difficulty} value={selectedMatrixOptions} onChange={setMatrixOptions} />}
          {topic === 'complex-numbers' && <label className="pl-label">Exercise type
            <select className="pl-input" value={modulusMode} onChange={event => setModulusMode(event.target.value as ModulusMode)}>
              <option value="expression">Modulus of an expression</option>
              <option value="properties">Modulus properties</option>
              <option value="geometry">Modulus and geometry</option>
            </select>
          </label>}
          {topic === 'mixed' && mixed && available && (
            <p className="pl-small pl-muted" id="mixed-weights">
              Mixed practice picks one topic for each problem with fixed weights:{' '}
              {mixedShares(topics, mixed, difficulty).map(({ topic: t, percent }) => `${t.name} ${percent}%`).join(', ')}.
            </p>
          )}
        </div>
        <div>
          <Button size="lg" arrow onClick={generate} disabled={busy || !available} aria-busy={busy}>
            {busy ? 'Generating…' : 'Generate problem'}
          </Button>
          {catalogue.status === 'loading' && <p role="status">Loading available topics…</p>}
          {catalogue.status === 'error' && <div role="alert"><p>{text.service_error}</p><Button variant="secondary" onClick={() => setCatalogueRevision(value => value + 1)}>Retry loading topics</Button></div>}
          {catalogue.status === 'ready' && !available && <p role="status">This topic and level are not available yet. Choose an available option.</p>}
          {error && <p role="alert">{error}</p>}
        </div>
      </section>
    </main>
  );
}
