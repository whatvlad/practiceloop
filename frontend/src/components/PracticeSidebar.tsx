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

  function topicRow(topic: AvailableTopic, title = topic.name) {
    return <li key={topic.slug}>
      {onPreviewTopic && LOCAL_PREVIEW_TOPICS.includes(topic.slug)
        ? <button type="button" className="pl-sidebar-topic" onClick={() => onPreviewTopic(topic.slug)}>{title}</button>
        : preview && onPreviewTopic ? <span aria-disabled="true">{title} <small>Not available locally</small></span>
        : <Link to={`/dashboard?area=${topic.area}&topic=${topic.slug}`} aria-current={current === topic.slug ? 'page' : undefined}>{title}</Link>}
    </li>;
  }
  const randomCurrent = pathname === '/random';
  return (
    <aside className="pl-practice-sidebar" aria-label="Practice topics">
      <div className="pl-sidebar-head">
        <p className="pl-label pl-m-0">Topics</p>
        {onLocalRandom
          ? <button type="button" className="pl-btn pl-btn--secondary pl-btn--sm pl-random-toggle" onClick={onLocalRandom}>Random problems</button>
          : <Link className="pl-btn pl-btn--secondary pl-btn--sm pl-random-toggle" to="/random" aria-current={randomCurrent ? 'page' : undefined}>Random problems</Link>}
      </div>
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
                return topic ? topicRow(topic, item.title) : <li key={item.title}><span>{item.title} <small>In develop</small></span></li>;
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
    </aside>
  );
}
