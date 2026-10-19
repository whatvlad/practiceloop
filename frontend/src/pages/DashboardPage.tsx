import { useEffect, useRef, useState } from 'react';
import text from '../../../backend/app/content/en.json';
import { Button, ButtonLink } from '../components/Button';
import { DifficultyScale } from '../components/DifficultyScale';
import { HistoryList } from '../components/HistoryRow';
import { StatTile } from '../components/StatTile';
import { TopicChips } from '../components/TopicChips';
import { generateProblem, getLastSelection, getProfileCounts, getTopics, listProblemPage } from '../data/api';
import type { Difficulty, TopicSlug } from '../data/types';
import { navigate } from '../router';
import { useLoad } from '../useLoad';

export function DashboardPage() {
  const [catalogueRevision, setCatalogueRevision] = useState(0);
  const catalogue = useLoad(getTopics, String(catalogueRevision));
  const [dataRevision, setDataRevision] = useState(0);
  const counts = useLoad(getProfileCounts, String(dataRevision));
  const recent = useLoad(async () => (await listProblemPage({ limit: 3 })).items, String(dataRevision));
  const last = useLoad(getLastSelection);
  const [topic, setTopic] = useState<TopicSlug>('basic-integrals');
  const [difficulty, setDifficulty] = useState<Difficulty>(1);
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const active = useRef(true);
  useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);
  const [error, setError] = useState('');
  const topics = catalogue.status === 'ready' ? catalogue.data : [];
  const levels = topics.find(t => t.slug === topic)?.availableDifficulties ?? [];
  const available = levels.includes(difficulty);

  useEffect(() => {
    if (last.status !== 'ready') return;
    setTopic(last.data.topic);
    setDifficulty(last.data.difficulty);
  }, [last]);

  async function generate() {
    if (pending.current || !available) return;
    pending.current = true;
    setError('');
    setBusy(true);
    try {
      const problem = await generateProblem(topic, difficulty);
      if (active.current) navigate(`/practice?id=${encodeURIComponent(problem.id)}`);
    } catch (failure) {
      if (active.current) setError(failure instanceof Error ? failure.message : text.service_error);
    } finally {
      pending.current = false;
      if (active.current) setBusy(false);
    }
  }

  return (
    <main className="pl-wrap pl-app-main">
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
          <p className="pl-muted pl-mt-1">Choose a topic and a difficulty. We generate the rest.</p>
        </div>
        <div className="pl-stack pl-gap-3">
          <div id="topic-label" className="pl-label">
            Topic
          </div>
          <TopicChips selected={topic} onSelect={setTopic} labelledBy="topic-label" available={busy ? [] : topics.filter(t => t.availableDifficulties.length > 0).map(t => t.slug)} />
          <p className="pl-small pl-muted">Disabled options are not available yet.</p>
        </div>
        <div className="pl-stack pl-gap-3">
          <div id="difficulty-label" className="pl-label">
            Difficulty
          </div>
          <DifficultyScale selected={difficulty} onSelect={setDifficulty} labelledBy="difficulty-label" available={busy ? [] : levels} />
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
