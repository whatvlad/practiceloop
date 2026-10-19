import { useState } from 'react';
import { Button } from '../components/Button';
import { getLearningStatistics } from '../data/api';
import { topicName } from '../data/topics';
import type { OmissionMetric } from '../data/types';
import { useLoad } from '../useLoad';

const rate = (metric: OmissionMetric) => metric.rate === null ? '—' : `${(metric.rate * 100).toFixed(1)}%`;

export function LearningStatistics() {
  const [revision, setRevision] = useState(0);
  const stats = useLoad(getLearningStatistics, String(revision));
  return <section className="pl-card pl-card--lg pl-stack pl-gap-4" aria-labelledby="constant-title">
    <h2 id="constant-title" className="pl-h-lg">Remembering + C</h2>
    <p className="pl-small pl-muted pl-m-0">A separate measure of answers that omit the arbitrary integration constant. Each checked attempt counts; invalid expressions are excluded. A lower rate means fewer omissions.</p>
    {stats.status === 'loading' && <p role="status">Loading constant statistics…</p>}
    {stats.status === 'error' && <div role="alert"><p>Constant statistics could not be loaded.</p><Button variant="secondary" onClick={() => setRevision(value => value + 1)}>Retry constant statistics</Button></div>}
    {stats.status === 'ready' && <>
      <p>{stats.data.omitted} omissions in {stats.data.checkedAttempts} checked attempts · {rate(stats.data)}</p>
      {!stats.data.checkedAttempts && <p className="pl-muted">No checked attempts yet. Your first checked answer will start these statistics.</p>}
      {!!stats.data.byTopicDifficulty.length && <div className="pl-table-scroll"><table className="pl-learning-table"><caption>All-time breakdown</caption><thead><tr><th scope="col">Topic / level</th><th scope="col">Omitted / checked</th><th scope="col">Rate</th></tr></thead><tbody>{stats.data.byTopicDifficulty.map(row => <tr key={`${row.topic}:${row.difficulty}`}><th scope="row">{topicName(row.topic)} · {row.difficulty}</th><td>{row.omitted} / {row.checkedAttempts}</td><td>{rate(row)}</td></tr>)}</tbody></table></div>}
      <div className="pl-table-scroll"><table className="pl-learning-table"><caption>Last eight weeks · UTC · current week is incomplete</caption><thead><tr><th scope="col">Week starting</th><th scope="col">Omitted / checked</th><th scope="col">Rate</th></tr></thead><tbody>{stats.data.weekly.map(row => <tr key={row.week}><th scope="row"><time dateTime={row.week}>{row.week}</time></th><td>{row.omitted} / {row.checkedAttempts}</td><td>{rate(row)}</td></tr>)}</tbody></table></div>
    </>}
  </section>;
}
