import { useEffect, useState } from 'react';
import { getCatalogue } from '../data/api';
import { algebraGroups } from '../data/algebraGroups';
import type { AvailableTopic, Catalogue } from '../data/types';
import { Link, useLocation } from '../router';
import { useLoad } from '../useLoad';

const LOCAL_PREVIEW_TOPICS = ['matrix-operations', 'determinants', 'inverse-matrices', 'matrix-rank', 'linear-systems', 'complex-arithmetic', 'complex-numbers', 'complex-polar-form', 'complex-conversion', 'polynomial-division', 'polynomial-roots', 'polynomial-operations', 'partial-fractions', 'fundamental-theorem-algebra'];

/** The topic tree beside the workspace. The server catalogue remains the authority for available topics. */
export function PracticeSidebar({ preview, onLocalRandom, onPreviewTopic }: { preview?: Catalogue; onPreviewTopic?: (topic: string) => void; onLocalRandom?: () => void } = {}) {
  const loaded = useLoad(getCatalogue);
  const { pathname, params } = useLocation();
  const catalogue = preview ? { status: 'ready' as const, data: preview } : loaded;
  const topics = catalogue.status === 'ready' ? catalogue.data.topics : [];
  const current = pathname === '/dashboard' ? params.get('topic') : null;

  function topicRow(topic: AvailableTopic, title = topic.name, section?: string) {
    return <li key={`${topic.slug}:${section ?? ''}`}>
      {onPreviewTopic && LOCAL_PREVIEW_TOPICS.includes(topic.slug)
        ? <button type="button" className="pl-sidebar-topic" onClick={() => onPreviewTopic(topic.slug)}>{title}</button>
        : preview && onPreviewTopic ? <span aria-disabled="true">{title} <small>Not available locally</small></span>
        : <Link to={`/dashboard?area=${topic.area}&topic=${topic.slug}${section ? `&section=${section}` : ''}`} aria-current={current === topic.slug && (params.get('section') ?? undefined) === section ? 'page' : undefined}>{title}</Link>}
    </li>;
  }
  const randomCurrent = pathname === '/random';
  // Phones show the tree only on request, so the page itself is the first thing on screen.
  // The local preview has its own menu button, so its tree is never folded a second time.
  const [open, setOpen] = useState(Boolean(preview));
  const where = `${pathname}?${params.toString()}`;
  useEffect(() => { if (!preview) setOpen(false); }, [where, preview]);
  return (
    <aside className={`pl-practice-sidebar${open ? ' is-open' : ''}`} aria-label="Practice topics">
      <div className="pl-sidebar-head">
        <p className="pl-label pl-m-0 pl-sidebar-title">Topics</p>
        {!preview && <button type="button" className="pl-btn pl-btn--secondary pl-btn--sm pl-sidebar-toggle" aria-expanded={open} aria-controls="pl-sidebar-tree" onClick={() => setOpen(value => !value)}>{open ? 'Hide topics' : 'Topics'}</button>}
        {onLocalRandom
          ? <button type="button" className="pl-btn pl-btn--secondary pl-btn--sm pl-random-toggle" onClick={onLocalRandom}>Random problems</button>
          : <Link className="pl-btn pl-btn--secondary pl-btn--sm pl-random-toggle" to="/random" aria-current={randomCurrent ? 'page' : undefined}>Random problems</Link>}
      </div>
      <div id="pl-sidebar-tree" className="pl-sidebar-tree">
      {!preview && <Link className="pl-sidebar-extra" to="/algebra-random">Random algebra with settings</Link>}
      {catalogue.status === 'loading' && <p role="status">Loading topics…</p>}
      {catalogue.status === 'error' && <p role="alert">Topics could not be loaded.</p>}
      {catalogue.status === 'ready' && <>
        <details open>
          <summary>Algebra</summary>
          {algebraGroups.map(group => {
            const available = group.items.flatMap(item => topics.filter(topic => topic.slug === item.topic && topic.availableDifficulties.length > 0));
            const holdsCurrent = available.some(topic => topic.slug === current);
            return <details className="pl-practice-sidebar-group" key={group.title} open={holdsCurrent || undefined}>
              <summary>{group.title}</summary>
              <ul>{group.items.filter(item => !(preview && onLocalRandom && ['polynomial-operations', 'fundamental-theorem-algebra'].includes(item.topic ?? ''))).map(item => {
                const topic = available.find(entry => entry.slug === item.topic);
                return topic ? topicRow(topic, item.title, item.section) : <li key={item.title}><span>{item.title} <small>Coming soon</small></span></li>;
              })}</ul>
            </details>;
          })}
        </details>
        {catalogue.data.areas.filter(area => area.slug !== 'algebra').map(area => {
          const available = topics.filter(topic => topic.area === area.slug && topic.availableDifficulties.length > 0);
          return <details key={area.slug} open={available.some(topic => topic.slug === current) || undefined}>
            <summary>{area.name}</summary>
            <ul>{available.map(topic => topicRow(topic))}</ul>
          </details>;
        })}
      </>}
      </div>
    </aside>
  );
}
