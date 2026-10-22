import { useEffect, useRef, useState } from 'react';
import text from '../../../backend/app/content/en.json';
import { createWorksheet, downloadWorksheetPdf, getCatalogue, WORKSHEET_LIMITS, DEFAULT_PAGE_OPTIONS } from '../data/api';
import { clampCount, groupRequests, levelsOf, nearestLevel, planWorksheet, type DraftGroup } from '../data/worksheetPlan';
import type { AreaSlug, Catalogue, Difficulty, PracticeTopic } from '../data/types';
import type { Worksheet, WorksheetPageOptions } from '../data/worksheets';
import { Link } from '../router';
import { useLoad } from '../useLoad';
import { Button } from './Button';
import { DifficultyScale } from './DifficultyScale';
import { WorksheetOptions } from './WorksheetOptions';

type Phase = { step: 'idle' } | { step: 'creating' } | { step: 'rendering'; worksheet: Worksheet }
  | { step: 'done'; worksheet: Worksheet } | { step: 'failed'; message: string; worksheet: Worksheet | null };

interface Start { area: AreaSlug; topic: PracticeTopic; difficulty: Difficulty }

function choices(catalogue: Catalogue) {
  return catalogue.areas.flatMap(area => [
    ...catalogue.topics.filter(t => t.area === area.slug && t.availableDifficulties.length > 0)
      .map(t => ({ area: area.slug, topic: t.slug as PracticeTopic, label: t.name, group: area.name })),
    ...(area.mixed ? [{ area: area.slug, topic: 'mixed' as const, label: `Mixed ${area.name.toLowerCase()}`, group: area.name }] : []),
  ]);
}

function GroupRow({ catalogue, index, planned, onChange, onRemove, removable, disabled }: {
  catalogue: Catalogue;
  index: number;
  planned: ReturnType<typeof planWorksheet>['groups'][number];
  onChange: (group: DraftGroup) => void;
  onRemove: () => void;
  removable: boolean;
  disabled: boolean;
}) {
  const { group, levels, capacity, capped } = planned;
  const id = `worksheet-group-${group.key}`;
  const options = choices(catalogue);
  const areas = [...new Set(options.map(o => o.group))];
  const [draft, setDraft] = useState(String(group.count));
  useEffect(() => setDraft(String(group.count)), [group.count]);
  return (
    <li className="pl-worksheet-group" aria-labelledby={`${id}-title`}>
      <div className="pl-row pl-worksheet-group-head">
        <h3 id={`${id}-title`} className="pl-label pl-m-0">Group {index + 1}</h3>
        {removable && (
          <Button variant="ghost" size="sm" onClick={onRemove} disabled={disabled} aria-label={`Remove group ${index + 1}`}>Remove</Button>
        )}
      </div>
      <div className="pl-worksheet-fields">
        <label className="pl-field">
          <span className="pl-small pl-muted">Topic</span>
          <select className="pl-select" value={`${group.area}:${group.topic}`} disabled={disabled}
            onChange={(event) => {
              const picked = options.find(o => `${o.area}:${o.topic}` === event.target.value);
              if (!picked) return;
              const next = levelsOf(catalogue, picked.area, picked.topic);
              onChange({ ...group, area: picked.area, topic: picked.topic, difficulty: nearestLevel(next, group.difficulty) });
            }}>
            {areas.length > 1
              ? areas.map(name => (
                <optgroup key={name} label={name}>
                  {options.filter(o => o.group === name).map(o => <option key={`${o.area}:${o.topic}`} value={`${o.area}:${o.topic}`}>{o.label}</option>)}
                </optgroup>
              ))
              : options.map(o => <option key={`${o.area}:${o.topic}`} value={`${o.area}:${o.topic}`}>{o.label}</option>)}
          </select>
        </label>
        <label className="pl-field pl-worksheet-count">
          <span className="pl-small pl-muted">Problems</span>
          <input className="pl-input pl-count-input" type="number" inputMode="numeric" min={1}
            max={Math.min(WORKSHEET_LIMITS.perGroup, capacity ?? WORKSHEET_LIMITS.perGroup)} value={draft} disabled={disabled}
            aria-describedby={capped ? `${id}-cap` : undefined}
            onChange={(event) => {
              setDraft(event.target.value);
              const value = Number(event.target.value);
              if (event.target.value !== '' && Number.isFinite(value)) onChange({ ...group, count: clampCount(value) });
            }}
            onBlur={() => setDraft(String(group.count))} />
        </label>
      </div>
      <div className="pl-stack pl-gap-2">
        <div id={`${id}-level`} className="pl-small pl-muted">Level</div>
        <DifficultyScale selected={group.difficulty} onSelect={(difficulty) => onChange({ ...group, difficulty })}
          labelledBy={`${id}-level`} available={disabled ? [] : levels} shown={levels} />
      </div>
      {capped && (
        <p id={`${id}-cap`} className="pl-small pl-m-0" role="status">
          {planned.shared
            ? `Earlier groups already use some of ${planned.label}, and a worksheet never repeats a problem, so this group will have ${planned.count}.`
            : `Only ${capacity} different ${capacity === 1 ? 'problem exists' : 'problems exist'} for ${planned.label}, so this group will have ${planned.count}.`}
        </p>
      )}
    </li>
  );
}

/** #117: "Print worksheet" at the bottom of the Practice page. New problems, saved to History, typeset by the server. */
export function WorksheetBuilder({ start }: { start: Start }) {
  const [open, setOpen] = useState(false);
  if (open) return <WorksheetForm start={start} />;
  return (
    <section className="pl-card pl-stack pl-gap-3 pl-worksheet" aria-labelledby="worksheet-title">
      <div className="pl-row pl-share-head">
        <h2 id="worksheet-title" className="pl-label pl-m-0">Print worksheet</h2>
        <span className="pl-small pl-muted">New problems in groups as a PDF, with space to write.</span>
      </div>
      <div><Button variant="secondary" onClick={() => setOpen(true)}>Build a worksheet</Button></div>
    </section>
  );
}

function WorksheetForm({ start }: { start: Start }) {
  const [revision, setRevision] = useState(0);
  const heading = useRef<HTMLHeadingElement>(null);
  const catalogue = useLoad(getCatalogue, String(revision));
  const nextKey = useRef(1);
  const [groups, setGroups] = useState<DraftGroup[]>([{ key: 0, ...start, count: 5 }]);
  const [options, setOptions] = useState<WorksheetPageOptions>(DEFAULT_PAGE_OPTIONS);
  const [phase, setPhase] = useState<Phase>({ step: 'idle' });
  const pending = useRef(false);
  const active = useRef(true);
  useEffect(() => { active.current = true; return () => { active.current = false; }; }, []);
  // Opening the builder moves focus to it, so keyboard and screen-reader users land in the form.
  useEffect(() => { heading.current?.focus(); }, [catalogue.status]);

  // A topic the catalogue does not offer moves to the first one it does, and a level it lacks to the nearest.
  useEffect(() => {
    if (catalogue.status !== 'ready') return;
    const offered = choices(catalogue.data);
    if (offered.length === 0) return;
    setGroups(current => {
      let changed = false;
      const next = current.map(group => {
        const known = offered.find(o => o.area === group.area && o.topic === group.topic) ?? offered[0];
        const difficulty = nearestLevel(levelsOf(catalogue.data, known.area, known.topic), group.difficulty);
        if (known.area === group.area && known.topic === group.topic && difficulty === group.difficulty) return group;
        changed = true;
        return { ...group, area: known.area, topic: known.topic, difficulty };
      });
      return changed ? next : current;
    });
  }, [catalogue]);

  if (catalogue.status === 'loading') return <section className="pl-card pl-worksheet"><p role="status" className="pl-m-0">Loading worksheet options…</p></section>;
  if (catalogue.status === 'error') {
    return (
      <section className="pl-card pl-stack pl-gap-3 pl-worksheet">
        <p role="alert" className="pl-m-0">{text.service_error}</p>
        <div><Button variant="secondary" onClick={() => setRevision(value => value + 1)}>Retry loading worksheet options</Button></div>
      </section>
    );
  }

  const plan = planWorksheet(catalogue.data, groups);
  const busy = phase.step === 'creating' || phase.step === 'rendering';
  const full = groups.length >= WORKSHEET_LIMITS.groups;

  function update(key: number, group: DraftGroup) {
    setGroups(current => current.map(g => (g.key === key ? group : g)));
  }

  function addGroup() {
    if (full || catalogue.status !== 'ready') return;
    const last = groups[groups.length - 1] ?? { key: 0, ...start, count: 5 };
    const count = Math.max(1, Math.min(5, WORKSHEET_LIMITS.total - plan.total));
    // Prefer the last group's topic and level; when earlier groups use it up, take the first cell with room left.
    const near = (levels: Difficulty[]) => [...levels].sort((a, b) => Math.abs(a - last.difficulty) - Math.abs(b - last.difficulty));
    const offered = choices(catalogue.data).sort((a, b) => Number(b.area === last.area && b.topic === last.topic) - Number(a.area === last.area && a.topic === last.topic));
    const candidates = offered.flatMap(o => near(levelsOf(catalogue.data, o.area, o.topic))
      .map(difficulty => ({ ...last, area: o.area, topic: o.topic, difficulty })));
    const fits = (group: DraftGroup) => planWorksheet(catalogue.data, [...groups, group]).groups.at(-1)!.count > 0;
    const next = candidates.map(c => ({ ...c, key: nextKey.current, count })).find(fits) ?? { ...last, key: nextKey.current, count };
    nextKey.current += 1;
    setGroups(current => [...current, next]);
  }

  async function render(worksheet: Worksheet) {
    setPhase({ step: 'rendering', worksheet });
    try {
      await downloadWorksheetPdf(worksheet.id);
      if (active.current) setPhase({ step: 'done', worksheet });
    } catch (failure) {
      if (active.current) setPhase({ step: 'failed', worksheet, message: failure instanceof Error ? failure.message : text.service_error });
    }
  }

  async function generate() {
    if (pending.current || plan.blocked) return;
    pending.current = true;
    setPhase({ step: 'creating' });
    try {
      const worksheet = await createWorksheet({ source: 'generate', groups: groupRequests(plan), ...options });
      if (active.current) await render(worksheet);
    } catch (failure) {
      if (active.current) setPhase({ step: 'failed', worksheet: null, message: failure instanceof Error ? failure.message : text.service_error });
    } finally {
      pending.current = false;
    }
  }

  async function retryDownload(worksheet: Worksheet) {
    if (pending.current) return;
    pending.current = true;
    try { await render(worksheet); } finally { pending.current = false; }
  }

  const made = phase.step === 'done' ? phase.worksheet : null;
  const short = made?.groups.filter(g => g.count < g.requested) ?? [];

  return (
    <section className="pl-card pl-card--lg pl-stack pl-gap-5 pl-worksheet" aria-labelledby="worksheet-title">
      <div className="pl-stack pl-gap-2">
        <h2 id="worksheet-title" ref={heading} tabIndex={-1} className="pl-h-lg pl-m-0">Print worksheet</h2>
        <p className="pl-muted pl-m-0">
          A PDF of new problems in groups, with space to write after each one. The problems are saved to your history, so you can check your answers online later.
        </p>
      </div>
      <ol className="pl-worksheet-groups" aria-label="Worksheet groups">
        {plan.groups.map((planned, index) => (
          <GroupRow key={planned.group.key} catalogue={catalogue.data} index={index} planned={planned} disabled={busy}
            removable={groups.length > 1} onChange={(group) => update(planned.group.key, group)}
            onRemove={() => setGroups(current => current.filter(g => g.key !== planned.group.key))} />
        ))}
      </ol>
      <div className="pl-row pl-worksheet-totals">
        <Button variant="secondary" size="sm" onClick={addGroup} disabled={busy || full}>Add group</Button>
        <span className="pl-small pl-muted" aria-live="polite">
          {plan.total} of {WORKSHEET_LIMITS.total} problems · {groups.length} of {WORKSHEET_LIMITS.groups} groups
        </span>
      </div>
      {full && <p className="pl-small pl-muted pl-m-0">A worksheet has at most {WORKSHEET_LIMITS.groups} groups.</p>}
      <WorksheetOptions idPrefix="worksheet" value={options} onChange={setOptions} disabled={busy} />
      <div className="pl-stack pl-gap-3">
        <div className="pl-actions">
          <Button arrow onClick={() => void generate()} disabled={busy || plan.blocked !== null} aria-busy={busy}>
            {phase.step === 'creating' ? 'Generating problems…' : phase.step === 'rendering' ? 'Making the PDF…' : 'Generate PDF'}
          </Button>
          {phase.step === 'failed' && phase.worksheet && (
            <Button variant="secondary" onClick={() => void retryDownload(phase.worksheet!)}>Retry download</Button>
          )}
        </div>
        {plan.blocked && <p className="pl-small pl-m-0" role="status">{plan.blocked}</p>}
        {busy && <p className="pl-small pl-muted pl-m-0" role="status">{phase.step === 'creating' ? 'Generating and saving the problems.' : 'Typesetting the PDF. This can take up to half a minute.'}</p>}
        {phase.step === 'failed' && (
          <p className="pl-small pl-m-0" role="alert">
            {phase.message}
            {phase.worksheet && ' The problems are already saved to your history; retrying makes no new ones.'}
          </p>
        )}
        {made && (
          <p className="pl-small pl-m-0" role="status">
            Your worksheet with {made.problemIds.length} {made.problemIds.length === 1 ? 'problem' : 'problems'} was downloaded and saved to your <Link to="/history">history</Link>.
            {short.length > 0 && ` ${short.map(g => `${g.label} got ${g.count} of ${g.requested}`).join('; ')}.`}
          </p>
        )}
      </div>
    </section>
  );
}
