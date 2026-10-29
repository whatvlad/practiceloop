import { useEffect, useRef, useState } from 'react';
import text from '../../../backend/app/content/en.json';
import { Button, ButtonLink } from '../components/Button';
import { DifficultyScale } from '../components/DifficultyScale';
import { HistoryList } from '../components/HistoryRow';
import { StatTile } from '../components/StatTile';
import { AreaChips, TopicChips } from '../components/TopicChips';
import { generateProblem, getCatalogue, getLastSelection, getProfileCounts, listProblemPage } from '../data/api';
import { mixedShares } from '../data/topics';
import type { AreaSlug, Difficulty, PracticeTopic } from '../data/types';
import { navigate } from '../router';
import { useLoad } from '../useLoad';

export function DashboardPage() {
  const [catalogueRevision, setCatalogueRevision] = useState(0);
  const catalogue = useLoad(getCatalogue, String(catalogueRevision));
  const [dataRevision, setDataRevision] = useState(0);
  const counts = useLoad(getProfileCounts, String(dataRevision));
  const recent = useLoad(async () => (await listProblemPage({ limit: 3 })).items, String(dataRevision));
  const last = useLoad(getLastSelection);
  const [area, setArea] = useState<AreaSlug>('mathematical-analysis');
  const [topic, setTopic] = useState<PracticeTopic>('basic-integrals');
  const [difficulty, setDifficulty] = useState<Difficulty>(1);
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const active = useRef(true);
  useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);
  const [error, setError] = useState('');
  const areas = catalogue.status === 'ready' ? catalogue.data.areas : [];
  // ADR-005: the learner picks an area first; topics and mixed practice belong to it.
  const topics = catalogue.status === 'ready' ? catalogue.data.topics.filter(t => t.area === area) : [];
  const mixed = areas.find(a => a.slug === area)?.mixed ?? null;
  const levels = topic === 'mixed' ? mixed?.availableDifficulties ?? [] : topics.find(t => t.slug === topic)?.availableDifficulties ?? [];
  const offered: PracticeTopic[] = [...topics.filter(t => t.availableDifficulties.length > 0).map(t => t.slug), ...(mixed ? ['mixed' as const] : [])];
  const available = levels.includes(difficulty);

  useEffect(() => {
    if (last.status !== 'ready') return;
    setArea(last.data.area);
    setTopic(last.data.topic);
    setDifficulty(last.data.difficulty);
  }, [last]);

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
      const problem = await generateProblem(topic, difficulty, area);
      if (active.current) navigate(`/practice?id=${encodeURIComponent(problem.id)}`);
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
          <p className="pl-muted pl-mt-1">Choose {areas.length > 1 ? 'an area, a topic' : 'a topic'} and a difficulty. We generate the rest.</p>
        </div>
        {areas.length > 1 && (
          <div className="pl-stack pl-gap-3">
            <div id="area-label" className="pl-label">
              Area
            </div>
            <AreaChips areas={areas.map(a => a.slug)} selected={area} onSelect={setArea} labelledBy="area-label" disabled={busy} />
          </div>
        )}
        <div className="pl-stack pl-gap-3">
          <div id="topic-label" className="pl-label">
            Topic
          </div>
          <TopicChips topics={topics} selected={topic} onSelect={setTopic} labelledBy="topic-label" mixed={mixed !== null} available={busy ? [] : offered} />
          <p className="pl-small pl-muted">Disabled options are not available yet.</p>
        </div>
        <div className="pl-stack pl-gap-3">
          <div id="difficulty-label" className="pl-label">
            Difficulty
          </div>
          <DifficultyScale selected={difficulty} onSelect={setDifficulty} labelledBy="difficulty-label" available={busy ? [] : levels} shown={levels} />
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
