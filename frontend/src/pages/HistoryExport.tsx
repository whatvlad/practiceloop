import { useEffect, useRef, useState } from 'react';
import { Button } from '../components/Button';
import { WorksheetOptions } from '../components/WorksheetOptions';
import { createWorksheet, DEFAULT_PAGE_OPTIONS, downloadWorksheetPdf, WORKSHEET_LIMITS } from '../data/api';
import type { WorksheetPageOptions } from '../data/worksheets';
import text from '../../../backend/app/content/en.json';

/** ADR-007: one History export holds at most 40 problems. */
export const MAX_EXPORT = WORKSHEET_LIMITS.ids;

interface HistoryExportProps {
  selected: readonly string[];
  /** Why a "Select all" stopped short of the loaded rows, if it did. */
  limitNote: string;
  /** The printed ids, and whether the answer key revealed their answers. */
  onExported: (ids: readonly string[], revealed: boolean) => void;
}

/** The bulk action bar for the History selection (#118): count, page options and "Export PDF". */
export function HistoryExport({ selected, limitNote, onExported }: HistoryExportProps) {
  const [options, setOptions] = useState<WorksheetPageOptions>(DEFAULT_PAGE_OPTIONS);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  // A worksheet that was created but whose download failed: retry the download only.
  const [saved, setSaved] = useState<{ id: string; count: number } | null>(null);
  const active = useRef(true);
  useEffect(() => () => { active.current = false; }, []);
  const count = selected.length;

  async function download(id: string, printed: number) {
    try {
      await downloadWorksheetPdf(id);
      if (!active.current) return;
      setSaved(null);
      setNotice(`Downloaded a PDF with ${printed} ${printed === 1 ? 'problem' : 'problems'}.`);
    } catch (failure) {
      if (!active.current) return;
      setSaved({ id, count: printed });
      setError(failure instanceof Error ? failure.message : text.service_error);
    }
  }

  async function exportPdf() {
    if (busy || count === 0 || count > MAX_EXPORT) return;
    setBusy(true);
    setError('');
    setNotice('');
    try {
      const worksheet = await createWorksheet({ source: 'history', problemIds: [...selected], ...options });
      if (!active.current) return;
      // The worksheet exists now, so its reveals are already recorded.
      onExported(worksheet.problemIds, options.answerKey);
      await download(worksheet.id, worksheet.problemIds.length);
    } catch (failure) {
      if (active.current) setError(failure instanceof Error ? failure.message : text.service_error);
    } finally {
      if (active.current) setBusy(false);
    }
  }

  async function retryDownload() {
    if (!saved || busy) return;
    setBusy(true);
    setError('');
    await download(saved.id, saved.count);
    if (active.current) setBusy(false);
  }

  return (
    <section className={`pl-hexport${count > 0 || notice || error ? ' is-active' : ''}`} aria-label="Export selected problems">
      <p className="pl-hexport-count" role="status" aria-live="polite">
        {count > 0 ? `${count} selected` : ''}
        {count >= MAX_EXPORT ? ` · the limit is ${MAX_EXPORT} problems per PDF` : ''}
      </p>
      {limitNote && <p className="pl-small pl-muted" role="status">{limitNote}</p>}
      {count > 0 && (
        <>
          <WorksheetOptions value={options} onChange={setOptions} disabled={busy} idPrefix="history-export" />
          <Button onClick={() => void exportPdf()} disabled={busy}>
            {busy ? 'Preparing PDF…' : 'Export PDF'}
          </Button>
        </>
      )}
      {error && (
        <div role="alert">
          <p className="pl-result pl-result--invalid">{error}</p>
          {saved && <Button variant="secondary" size="sm" onClick={() => void retryDownload()} disabled={busy}>Retry the download</Button>}
        </div>
      )}
      {notice && <p className="pl-small pl-muted" role="status">{notice}</p>}
    </section>
  );
}
