import { useRef, useState } from 'react';
import { Button } from '../components/Button';
import { initialMatrixOptions, matrixOptionsValid, MatrixSettings } from '../components/MatrixSettings';
import { CheckIcon } from '../components/icons';
import { generateProblem, getCatalogue } from '../data/api';
import { algebraGroups } from '../data/algebraGroups';
import { difficultyLabel } from '../data/difficultyLabels';
import { eligibleRandomChoices, loadRandomMatrixOptions, loadRandomSelection, pickRandomChoice, saveRandomMatrixOptions, saveRandomSelection } from '../data/randomPractice';
import type { RandomSelection } from '../data/randomPractice';
import type { AvailableTopic, Catalogue, Difficulty } from '../data/types';
import { navigate } from '../router';
import { useLoad } from '../useLoad';

interface Group { key: string; area: string; title: string; topics: { topic: AvailableTopic; title: string }[] }

/** Algebra keeps its navigation groups; every other area is one group. */
function groupsOf(catalogue: Catalogue): Group[] {
  const available = catalogue.topics.filter(topic => topic.availableDifficulties.length > 0);
  const algebraName = catalogue.areas.find(area => area.slug === 'algebra')?.name ?? 'Algebra';
  const algebra = algebraGroups.map(group => ({
    key: `algebra:${group.title}`,
    area: algebraName,
    title: group.title,
    topics: group.items.flatMap(item => {
      const topic = available.find(entry => entry.slug === item.topic);
      return topic ? [{ topic, title: item.title }] : [];
    }),
  }));
  const others = catalogue.areas.filter(area => area.slug !== 'algebra').map(area => ({
    key: area.slug,
    area: area.name,
    title: area.name,
    topics: available.filter(topic => topic.area === area.slug).map(topic => ({ topic, title: topic.name })),
  }));
  return [...algebra, ...others].filter(group => group.topics.length > 0);
}

/** Random practice: pick topics and a level for each; every problem draws one of them. */
export function RandomPracticePage({ accountId }: { accountId: string }) {
  const catalogue = useLoad(getCatalogue);
  const topics = catalogue.status === 'ready' ? catalogue.data.topics : [];
  const [selection, setSelection] = useState<RandomSelection>(() => loadRandomSelection(accountId));
  const [matrixOptions, setMatrixOptions] = useState(() => loadRandomMatrixOptions(accountId) ?? initialMatrixOptions(1));
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const [error, setError] = useState('');
  const choices = eligibleRandomChoices(selection, topics);
  const count = Object.keys(selection).length;
  const missingLevel = Object.values(selection).some(level => level === null);

  function update(next: RandomSelection) {
    setSelection(next);
    saveRandomSelection(accountId, next);
    setError('');
  }
  function toggle(slugs: string[], on: boolean) {
    const next = { ...selection };
    for (const slug of slugs) {
      if (on) next[slug] ??= null;
      else delete next[slug];
    }
    update(next);
  }
  async function generate() {
    if (!choices || pending.current) return;
    pending.current = true;
    setBusy(true);
    setError('');
    try {
      const choice = pickRandomChoice(choices);
      let options;
      if (choice.topic === 'matrix-operations') {
        options = matrixOptionsValid(choice.difficulty, matrixOptions) ? matrixOptions : initialMatrixOptions(choice.difficulty);
        saveRandomMatrixOptions(accountId, options);
      }
      const problem = options ? await generateProblem(choice.topic, choice.difficulty, choice.area, options)
        : await generateProblem(choice.topic, choice.difficulty, choice.area);
      navigate(`/practice?id=${encodeURIComponent(problem.id)}&mode=random`);
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'Could not generate a problem.');
    } finally { pending.current = false; setBusy(false); }
  }

  function tile({ topic, title }: Group['topics'][number]) {
    const on = Object.hasOwn(selection, topic.slug);
    const level = selection[topic.slug] ?? null;
    return <li key={topic.slug} className={`pl-rtile${on ? ' is-on' : ''}`}>
      <button type="button" className="pl-rtile-toggle" aria-pressed={on} onClick={() => toggle([topic.slug], !on)}>
        <span className="pl-rtile-check" aria-hidden="true">{on && <CheckIcon />}</span>
        <span>{title}</span>
      </button>
      {on && <div className="pl-rtile-levels" role="group" aria-label={`Level for ${title}`}>
        {topic.availableDifficulties.map(value => (
          <button key={value} type="button" className="pl-rlevel" aria-pressed={level === value}
            onClick={() => update({ ...selection, [topic.slug]: value as Difficulty })}>
            {difficultyLabel(topic.slug, value)}
          </button>
        ))}
      </div>}
      {on && level === null && <p className="pl-small pl-rtile-note">Choose a level.</p>}
      {on && topic.slug === 'matrix-operations' && level !== null && <MatrixSettings level={level} value={matrixOptions}
        onChange={value => { setMatrixOptions(value); saveRandomMatrixOptions(accountId, value); }} />}
    </li>;
  }

  const groups = catalogue.status === 'ready' ? groupsOf(catalogue.data) : [];
  return (
    <main id="main" tabIndex={-1} className="pl-wrap pl-app-main pl-random">
      <div className="pl-label">Random practice</div>
      <h1 className="pl-display-md pl-page-title">Mix topics</h1>
      <p className="pl-lead pl-random-lead">Select topics and a level for each. Every problem comes from one of them, chosen at random.</p>
      {catalogue.status === 'loading' && <p role="status">Loading topics…</p>}
      {catalogue.status === 'error' && <p role="alert">Topics could not be loaded.</p>}
      {groups.map(group => {
        const slugs = group.topics.map(entry => entry.topic.slug);
        const all = slugs.every(slug => Object.hasOwn(selection, slug));
        return <section key={group.key} className="pl-rgroup" aria-labelledby={`random-${group.key}`}>
          <div className="pl-rgroup-head">
            <h2 id={`random-${group.key}`} className="pl-h-md">
              {group.title !== group.area && <span className="pl-rgroup-area">{group.area}</span>}
              {group.title}
            </h2>
            <Button variant="ghost" size="sm" onClick={() => toggle(slugs, !all)}>{all ? 'Clear group' : 'Select all'}</Button>
          </div>
          <ul className="pl-rtiles">{group.topics.map(tile)}</ul>
        </section>;
      })}
      {catalogue.status === 'ready' && <div className="pl-random-bar">
        <p className="pl-m-0" role="status">
          {count === 0 ? 'No topics selected.' : `${count} ${count === 1 ? 'topic' : 'topics'} selected${missingLevel ? ', choose a level for each' : ''}.`}
        </p>
        <div className="pl-row">
          {count > 0 && <Button variant="ghost" onClick={() => update({})} disabled={busy}>Clear</Button>}
          <Button arrow onClick={() => void generate()} disabled={!choices || busy} aria-busy={busy}>{busy ? 'Generating…' : 'Generate random problem'}</Button>
        </div>
        {error && <p className="pl-random-error" role="alert">{error}</p>}
      </div>}
    </main>
  );
}
