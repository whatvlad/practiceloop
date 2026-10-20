import { useRef, useState, type FormEvent } from 'react';
import { reportProblem } from '../data/api';
import { REPORT_CATEGORIES, type ReportCategory } from '../data/types';
import { Button } from './Button';
import text from '../../../backend/app/content/en.json';

const LABELS: Record<ReportCategory, string> = {
  answer_check: 'My answer was checked wrongly',
  solution: 'The answer or solution is wrong',
  statement: 'The problem is unclear or broken',
  display: 'Something does not display properly',
  other: 'Something else',
};

/** "Report a problem" (#38): a category and an optional comment, nothing personal. */
export function ReportProblem({ problemId }: { problemId: string }) {
  const [open, setOpen] = useState(false);
  const [category, setCategory] = useState<ReportCategory | null>(null);
  const [comment, setComment] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [sent, setSent] = useState(false);
  const pending = useRef(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!category || pending.current) return;
    pending.current = true;
    setBusy(true);
    setError('');
    try {
      await reportProblem(problemId, category, comment);
      setSent(true);
      setOpen(false);
      setCategory(null);
      setComment('');
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : text.service_error);
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }

  return (
    <section className="pl-card pl-stack pl-gap-3 pl-report" aria-labelledby={`report-${problemId}`}>
      <div className="pl-row pl-share-head">
        <h2 id={`report-${problemId}`} className="pl-label pl-m-0">Report a problem</h2>
        <span className="pl-small pl-muted">Tell us if this problem or its check looks wrong.</span>
      </div>
      {open ? (
        <form className="pl-stack pl-gap-3" onSubmit={(event) => void submit(event)}>
          <fieldset className="pl-stack pl-gap-2 pl-report-options" disabled={busy}>
            <legend className="pl-small pl-muted">What is wrong?</legend>
            {REPORT_CATEGORIES.map((value) => (
              <label key={value} className="pl-row pl-report-option">
                <input type="radio" name={`report-category-${problemId}`} value={value} checked={category === value}
                  onChange={() => setCategory(value)} />
                <span>{LABELS[value]}</span>
              </label>
            ))}
          </fieldset>
          <label className="pl-field">
            <span className="pl-small pl-muted">Comment (optional, no personal details)</span>
            <textarea className="pl-input pl-report-comment" value={comment} maxLength={500} rows={3} disabled={busy}
              onChange={(event) => setComment(event.target.value)} />
          </label>
          <div className="pl-actions">
            <Button type="submit" variant="secondary" disabled={busy || !category} aria-busy={busy}>
              {busy ? 'Sending…' : 'Send report'}
            </Button>
            <Button type="button" variant="ghost" disabled={busy} onClick={() => setOpen(false)}>
              Cancel
            </Button>
          </div>
        </form>
      ) : (
        <div>
          <Button variant="ghost" onClick={() => { setSent(false); setOpen(true); }}>
            Report a problem
          </Button>
        </div>
      )}
      {sent && <p className="pl-small pl-muted pl-m-0" role="status">Thanks, your report was sent.</p>}
      {error && <p className="pl-small pl-m-0" role="alert">{error}</p>}
    </section>
  );
}
