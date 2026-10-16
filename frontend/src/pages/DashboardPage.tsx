import { useEffect, useState } from 'react';
import { Button, ButtonLink } from '../components/Button';
import { DifficultyScale } from '../components/DifficultyScale';
import { HistoryList } from '../components/HistoryRow';
import { StatTile } from '../components/StatTile';
import { TopicChips } from '../components/TopicChips';
import { generateProblem, getLastSelection, getProfileCounts, listProblems } from '../data/api';
import type { Difficulty, TopicSlug } from '../data/types';
import { navigate } from '../router';
import { useLoad } from '../useLoad';

export function DashboardPage() {
  const counts = useLoad(getProfileCounts);
  const recent = useLoad(async () => (await listProblems()).slice(0, 3));
  const last = useLoad(getLastSelection);
  const [topic, setTopic] = useState<TopicSlug>('substitution');
  const [difficulty, setDifficulty] = useState<Difficulty>(3);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (last.status !== 'ready') return;
    setTopic(last.data.topic);
    setDifficulty(last.data.difficulty);
  }, [last]);

  async function generate() {
    setBusy(true);
    try {
      const problem = await generateProblem(topic, difficulty);
      navigate(`/practice?id=${encodeURIComponent(problem.id)}`);
    } finally {
      setBusy(false);
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
          <TopicChips selected={topic} onSelect={setTopic} labelledBy="topic-label" />
        </div>
        <div className="pl-stack pl-gap-3">
          <div id="difficulty-label" className="pl-label">
            Difficulty
          </div>
          <DifficultyScale selected={difficulty} onSelect={setDifficulty} labelledBy="difficulty-label" />
        </div>
        <div>
          <Button size="lg" arrow onClick={generate} disabled={busy}>
            Generate problem
          </Button>
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
    </main>
  );
}
