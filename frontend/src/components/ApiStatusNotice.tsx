import type { ApiHealth } from '../data/health';
import { WarningIcon } from './icons';
import text from '../../../backend/app/content/en.json';

/** Shown only when the API is configured but cannot be reached. */
export function ApiStatusNotice({ health }: { health: ApiHealth | undefined }) {
  if (health !== 'unreachable') return null;
  return (
    <div className="pl-wrap pl-api-notice">
      <div className="pl-result pl-result--invalid" role="status">
        <WarningIcon />
        <div>
          <b>Can’t reach the PracticeLoop server</b>
          <span>{text.service_error}</span>
        </div>
      </div>
    </div>
  );
}
