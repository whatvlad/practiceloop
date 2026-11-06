import { useRef, useState } from 'react';
import { generateProblem, getCatalogue } from '../data/api';
import { algebraGroups } from '../data/algebraGroups';
import { difficultyLabel } from '../data/difficultyLabels';
import { eligibleRandomChoices, loadRandomMatrixOptions, loadRandomSelection, pickRandomChoice, saveRandomMatrixOptions, saveRandomSelection } from '../data/randomPractice';
import { initialMatrixOptions, matrixOptionsValid, MatrixSettings } from './MatrixSettings';
import type { RandomSelection } from '../data/randomPractice';
import type { AvailableTopic, Catalogue, Difficulty } from '../data/types';
import { Link, navigate } from '../router';
import { useLoad } from '../useLoad';

/** The server catalogue remains the authority for available topics and levels. */
export function PracticeSidebar({ preview, accountId = 'local-preview', onPreviewTopic }: { preview?: Catalogue; accountId?: string; onPreviewTopic?: (topic: string) => void } = {}) {
  const loaded = useLoad(getCatalogue);
  const catalogue = preview ? { status: 'ready' as const, data: preview } : loaded;
  const topics = catalogue.status === 'ready' ? catalogue.data.topics : [];
  const [randomMode, setRandomMode] = useState(false);
  const [selection, setSelection] = useState<RandomSelection>(() => loadRandomSelection(accountId));
  const [matrixOptions, setMatrixOptions] = useState(() => loadRandomMatrixOptions(accountId) ?? initialMatrixOptions(1));
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const [error, setError] = useState('');
  const choices = eligibleRandomChoices(selection, topics);

  function updateSelection(next: RandomSelection) {
    setSelection(next);
    saveRandomSelection(accountId, next);
    setError('');
  }
  function toggle(slugs: string[], checked: boolean) {
    const next = { ...selection };
    for (const slug of slugs) {
      if (checked) next[slug] ??= null;
      else delete next[slug];
    }
    updateSelection(next);
  }
  function topicRow(topic: AvailableTopic, title = topic.name) {
    const checked = Object.hasOwn(selection, topic.slug);
    return <li key={topic.slug}>
      {randomMode ? <>
        <label><input type="checkbox" checked={checked} onChange={event => toggle([topic.slug], event.target.checked)} /> {title}</label>
        {checked && <label className="pl-random-level">Level for {title}
          <select value={selection[topic.slug] ?? ''} onChange={event => updateSelection({ ...selection, [topic.slug]: event.target.value ? Number(event.target.value) as Difficulty : null })}>
            <option value="">Choose level</option>
            {topic.availableDifficulties.map(level => <option key={level} value={level}>{difficultyLabel(topic.slug, level)}</option>)}
          </select>
        </label>}
        {checked && topic.slug === 'matrix-operations' && selection[topic.slug] && <MatrixSettings
          level={selection[topic.slug]!} value={matrixOptions}
          onChange={value => { setMatrixOptions(value); saveRandomMatrixOptions(accountId, value); }} />}
      </> : onPreviewTopic && ['matrix-operations', 'determinants', 'inverse-matrices'].includes(topic.slug)
        ? <button type="button" className="pl-sidebar-topic" onClick={() => onPreviewTopic(topic.slug)}>{title}</button>
        : <Link to={`/dashboard?area=${topic.area}&topic=${topic.slug}`}>{title}</Link>}
    </li>;
  }
  async function generate() {
    if (!choices || pending.current || preview) return;
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
  return (
    <aside className="pl-practice-sidebar" aria-label="Practice topics">
      <p className="pl-label">Practice topics</p>
      <button type="button" className="pl-btn pl-btn--secondary pl-random-toggle" aria-pressed={randomMode} onClick={() => setRandomMode(!randomMode)}>Random problems</button>
      {catalogue.status === 'loading' && <p role="status">Loading topics…</p>}
      {catalogue.status === 'error' && <p role="alert">Topics could not be loaded.</p>}
      {catalogue.status === 'ready' && <>
        <details open>
          <summary>Algebra</summary>
          {algebraGroups.map(group => {
            const available = group.items.flatMap(item => topics.filter(topic => topic.slug === item.topic && topic.availableDifficulties.length > 0));
            const selected = available.filter(topic => Object.hasOwn(selection, topic.slug));
            return <details className="pl-practice-sidebar-group" key={group.title}>
              <summary>{group.title}</summary>
              {randomMode && available.length > 0 && <label className="pl-random-group"><input type="checkbox" checked={selected.length === available.length} onChange={event => toggle(available.map(topic => topic.slug), event.target.checked)} /> Select all in {group.title}</label>}
              <ul>{group.items.map(item => {
                const topic = available.find(entry => entry.slug === item.topic);
                return topic ? topicRow(topic, item.title) : <li key={item.title}><span>{item.title} <small>In develop</small></span></li>;
              })}</ul>
            </details>;
          })}
        </details>
        {catalogue.data.areas.filter(area => area.slug !== 'algebra').map(area => {
          const available = topics.filter(topic => topic.area === area.slug && topic.availableDifficulties.length > 0);
          return <details key={area.slug}>
            <summary>{area.name}</summary>
            {randomMode && available.length > 0 && <label className="pl-random-group"><input type="checkbox" checked={available.every(topic => Object.hasOwn(selection, topic.slug))} onChange={event => toggle(available.map(topic => topic.slug), event.target.checked)} /> Select all in {area.name}</label>}
            <ul>{available.map(topic => topicRow(topic))}</ul>
          </details>;
        })}
        {randomMode && <div className="pl-random-actions">
          <p className="pl-small pl-muted">{Object.keys(selection).length} selected. Choose a level for every topic.</p>
          <button type="button" className="pl-btn pl-btn--primary" onClick={() => void generate()} disabled={!choices || busy || !!preview}>{busy ? 'Generating…' : 'Generate random problem'}</button>
          {preview && <p className="pl-small pl-muted">Generating requires a signed-in account.</p>}
          {error && <p role="alert">{error}</p>}
        </div>}
      </>}
    </aside>
  );
}
