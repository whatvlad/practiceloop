import type { ApiHealth } from '../data/health';
import { WarningIcon } from './icons';
import text from '../../../backend/app/content/en.json';

/** Shown only when the API is configured but cannot be reached. */
export function ApiStatusNotice({ health, wrap = 'pl-wrap' }: { health: ApiHealth | undefined; wrap?: string }) {
  if (health !== 'unreachable') return null;
  return (
    <section className={`${wrap} pl-api-notice`} aria-label="Server status">
      <div className="pl-result pl-result--invalid" role="status">
        <WarningIcon />
        <div>
          <b>Can’t reach the PracticeLoop server</b>
          <span>{text.service_error}</span>
        </div>
      </div>
    </section>
  );
}
