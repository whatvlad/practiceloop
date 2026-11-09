import { useEffect, useRef, useState } from 'react';
import text from '../../../backend/app/content/en.json';
import { Button, ButtonLink } from '../components/Button';
import { DifficultyScale } from '../components/DifficultyScale';
import { initialMatrixOptions, matrixOptionsQuery, matrixOptionsValid, MatrixSettings } from '../components/MatrixSettings';
import { modulusModeQuery, type ModulusMode } from '../components/ModulusSettings';
import { HistoryList } from '../components/HistoryRow';
import { StatTile } from '../components/StatTile';
import { generateProblem, getCatalogue, getLastSelection, getProfileCounts, listProblemPage } from '../data/api';
import { mixedShares } from '../data/topics';
import type { AreaSlug, Difficulty, PracticeTopic } from '../data/types';
import type { MatrixDimensions } from '../data/types';
import { navigate } from '../router';
import { useLoad } from '../useLoad';

export function DashboardPage({ initialArea, initialTopic }: { initialArea?: AreaSlug; initialTopic?: PracticeTopic } = {}) {
  const [catalogueRevision, setCatalogueRevision] = useState(0);
  const catalogue = useLoad(getCatalogue, String(catalogueRevision));
  const [dataRevision, setDataRevision] = useState(0);
  const counts = useLoad(getProfileCounts, String(dataRevision));
  const recent = useLoad(async () => (await listProblemPage({ limit: 3 })).items, String(dataRevision));
  const last = useLoad(getLastSelection);
  const [area, setArea] = useState<AreaSlug>(initialArea ?? 'mathematical-analysis');
  const [topic, setTopic] = useState<PracticeTopic>(initialTopic ?? 'basic-integrals');
  const [difficulty, setDifficulty] = useState<Difficulty>(1);
  const [matrixOptions, setMatrixOptions] = useState(() => initialMatrixOptions(1));
  const [modulusMode, setModulusMode] = useState<ModulusMode>('expression');
  const [rankDimensions, setRankDimensions] = useState({ rows: 2, columns: 2 });
  const [squareSize, setSquareSize] = useState(2);
  const [complexMode, setComplexMode] = useState<'multiply' | 'divide'>('multiply');
  const [conversionMode, setConversionMode] = useState<'alg-trig' | 'alg-exp' | 'trig-alg' | 'exp-alg'>('alg-trig');
  const [polarMode, setPolarMode] = useState<'argument' | 'power' | 'root'>('argument');
  const [polynomialMode, setPolynomialMode] = useState<'division' | 'remainder' | 'divisibility'>('division');
  const [customMatrix, setCustomMatrix] = useState(false);
  const [matrixDimensions, setMatrixDimensions] = useState<MatrixDimensions>({ operation: 'add', rowsA: 2, colsA: 2, rowsB: 2, colsB: 2 });
  const compatibleMatrix = matrixDimensions.operation === 'divide' ? matrixDimensions.colsA === matrixDimensions.rowsB && matrixDimensions.rowsB === matrixDimensions.colsB : matrixDimensions.operation === 'multiply' ? matrixDimensions.colsA === matrixDimensions.rowsB : matrixDimensions.rowsA === matrixDimensions.rowsB && matrixDimensions.colsA === matrixDimensions.colsB;
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
  const levels = topic === 'complex-polar-form' ? allLevels.filter(level => level === 1) : topic === 'complex-numbers' && modulusMode ? allLevels.filter(level => level <= 3) : allLevels;
  const offered: PracticeTopic[] = [...topics.filter(t => t.availableDifficulties.length > 0).map(t => t.slug), ...(mixed ? ['mixed' as const] : [])];
  const available = levels.includes(difficulty) && (topic !== 'matrix-operations' || !customMatrix || compatibleMatrix);
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
      const options = topic === 'matrix-operations' && !customMatrix ? selectedMatrixOptions : undefined;
      const mode = topic === 'complex-numbers' ? modulusMode : undefined;
      const exerciseMode = difficulty <= 3 ? topic === 'complex-arithmetic' ? complexMode : topic === 'polynomial-division' ? polynomialMode : topic === 'complex-conversion' ? conversionMode : topic === 'polynomial-roots' ? 'roots' : topic === 'partial-fractions' ? 'fractions' : topic === 'complex-polar-form' ? polarMode : undefined : undefined;
      const chosenDifficulty = topic === 'complex-polar-form' ? ({ argument: 1, power: 2, root: 3 } as const)[polarMode] : difficulty;
      const problem = await generateProblem(topic, chosenDifficulty, area, options, mode, topic === 'matrix-rank' ? rankDimensions : undefined, topic === 'matrix-operations' && customMatrix ? matrixDimensions : undefined, ['determinants', 'inverse-matrices', 'linear-systems'].includes(topic) && difficulty <= 3 ? squareSize : undefined, exerciseMode);
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
      <div className="pl-label">Dashboard</div>
      <h1 className="pl-display-md pl-page-title">
        Pick up where you <em>left off.</em>
      </h1>
      {counts.status === 'ready' && (
        <div className="pl-grid-3 pl-mb-6">
          <StatTile label="Generated" value={counts.data.generated} />
          <StatTile label="Attempted" value={counts.data.attempted} />
          <StatTile label="Correct" value={counts.data.correct} of={counts.data.attempted} />
        </div>
      )}
      {counts.status === 'loading' && <p role="status">Loading your statistics…</p>}
      {(counts.status === 'error' || recent.status === 'error') && <div role="alert"><p>Your history or statistics could not be loaded.</p><Button variant="secondary" onClick={() => setDataRevision(value => value + 1)}>Retry history and statistics</Button></div>}
      <section className="pl-problem pl-problem--flat pl-mb-6" aria-labelledby="start-title">
        <div>
          <h2 id="start-title" className="pl-h-lg">
            Start a new problem
          </h2>
          <p className="pl-muted pl-mt-1">Choose a topic from the practice tree, then select a difficulty.</p>
        </div>
        <p className="pl-small">Selected topic: {topics.find(item => item.slug === topic)?.name ?? topic}</p>
        <div className="pl-stack pl-gap-3">
          {topic !== 'complex-polar-form' && <><div id="difficulty-label" className="pl-label">
            Difficulty
          </div>
          <DifficultyScale selected={difficulty} onSelect={setDifficulty} labelledBy="difficulty-label" available={busy ? [] : levels} shown={levels} topic={topic} /></>}
          {topic === 'matrix-operations' && <><label className="pl-label"><input type="checkbox" checked={customMatrix} onChange={event => setCustomMatrix(event.target.checked)} /> Custom dimensions</label>
            {!customMatrix ? <MatrixSettings level={difficulty} value={selectedMatrixOptions} onChange={setMatrixOptions} /> : <div className="pl-stack pl-gap-3">
              <label className="pl-label">Operation<select className="pl-input" value={matrixDimensions.operation} onChange={event => setMatrixDimensions(current => ({ ...current, operation: event.target.value as MatrixDimensions['operation'] }))}>
                <option value="add">Addition</option><option value="subtract">Subtraction</option><option value="multiply">Multiplication</option><option value="divide">Division</option>
              </select></label>
              {(['rowsA', 'colsA', 'rowsB', 'colsB'] as const).map(key => <label key={key} className="pl-label">{{ rowsA: 'Rows of A', colsA: 'Columns of A', rowsB: 'Rows of B', colsB: 'Columns of B' }[key]}
                <select className="pl-input" value={matrixDimensions[key]} onChange={event => setMatrixDimensions(current => ({ ...current, [key]: Number(event.target.value) }))}>
                  {[1, 2, 3, 4, 5].map(size => <option key={size} value={size}>{size}</option>)}
                </select></label>)}
              {!compatibleMatrix && <p role="alert">Choose compatible matrix dimensions.</p>}
            </div>}</>}
          {topic === 'matrix-rank' && (['rows', 'columns'] as const).map(key => <label key={key} className="pl-label">{key === 'rows' ? 'Rows' : 'Columns'}
            <select className="pl-input" value={rankDimensions[key]} onChange={event => setRankDimensions(current => ({ ...current, [key]: Number(event.target.value) }))}>
              {[2, 3, 4, 5].map(size => <option key={size} value={size}>{size}</option>)}
            </select>
          </label>)}
          {['determinants', 'inverse-matrices', 'linear-systems'].includes(topic) && difficulty <= 3 && <label className="pl-label">{topic === 'linear-systems' ? 'Number of unknowns' : 'Matrix size'}
            <select className="pl-input" value={squareSize} onChange={event => setSquareSize(Number(event.target.value))}>{[2, 3, 4, 5].map(size => <option key={size} value={size}>{size}</option>)}</select>
          </label>}
          {topic === 'complex-arithmetic' && difficulty <= 3 && <label className="pl-label">Exercise type<select className="pl-input" value={complexMode} onChange={event => setComplexMode(event.target.value as typeof complexMode)}><option value="multiply">Multiplication</option><option value="divide">Division</option></select></label>}
          {topic === 'complex-conversion' && <label className="pl-label">Exercise type<select className="pl-input" value={conversionMode} onChange={event => setConversionMode(event.target.value as typeof conversionMode)}><option value="alg-trig">Algebraic → trigonometric</option><option value="alg-exp">Algebraic → exponential</option><option value="trig-alg">Trigonometric → algebraic</option><option value="exp-alg">Exponential → algebraic</option></select></label>}
          {topic === 'complex-polar-form' && <label className="pl-label">Exercise type<select className="pl-input" value={polarMode} onChange={event => setPolarMode(event.target.value as typeof polarMode)}><option value="argument">Principal argument</option><option value="power">Powers (de Moivre)</option><option value="root">One root</option></select></label>}
          {topic === 'polynomial-division' && difficulty <= 3 && <label className="pl-label">Exercise type<select className="pl-input" value={polynomialMode} onChange={event => setPolynomialMode(event.target.value as typeof polynomialMode)}><option value="division">Quotient and remainder</option><option value="remainder">Remainder theorem</option><option value="divisibility">Divisibility condition</option></select></label>}
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
      <div className="pl-row pl-section-head">
        <h2 className="pl-h-lg">Recent problems</h2>
        <ButtonLink to="/history" variant="ghost" size="sm" arrow>
          View all history
        </ButtonLink>
      </div>
      {recent.status === 'ready' &&
        (recent.data.length > 0 ? (
          <HistoryList problems={recent.data} />
        ) : (
          <p className="pl-muted">Problems you generate appear here.</p>
        ))}
      {recent.status === 'loading' && <p role="status">Loading recent problems…</p>}
    </main>
  );
}
