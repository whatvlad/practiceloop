import { AREAS } from '../data/topics';
import type { AreaSlug, PracticeTopic, Topic } from '../data/types';
import { CheckIcon } from './icons';

interface ChipOption<T extends string> {
  value: T;
  label: string;
}

interface ChipsProps<T extends string> {
  available?: readonly T[];
  options: readonly ChipOption<T>[];
  selected: T;
  onSelect: (value: T) => void;
  /** Accessible name of the group, e.g. "Topic". */
  label: string;
  labelledBy?: string;
}

/** Single-select pill chips: the topic picker and the history filters. */
export function Chips<T extends string>({ options, selected, onSelect, label, labelledBy, available }: ChipsProps<T>) {
  return (
    <div className="pl-chips" role="group" aria-label={labelledBy ? undefined : label} aria-labelledby={labelledBy}>
      {options.map((option) => {
        const pressed = option.value === selected;
        return (
          <button
            key={option.value}
            type="button"
            className="pl-chip"
            aria-pressed={pressed}
            disabled={available !== undefined && !available.includes(option.value)}
            title={available !== undefined && !available.includes(option.value) ? 'Not available yet' : undefined}
            onClick={() => onSelect(option.value)}
          >
            {pressed && <CheckIcon />}
            {option.label}
          </button>
        );
      })}
    </div>
  );
}

interface TopicChipsProps {
  /** The topics of the chosen area, in catalogue order. */
  topics: readonly Topic[];
  selected: PracticeTopic;
  onSelect: (topic: PracticeTopic) => void;
  labelledBy?: string;
  available?: readonly PracticeTopic[];
  /** Offer mixed practice as a last chip (#36). */
  mixed?: boolean;
}

export function TopicChips({ topics, selected, onSelect, labelledBy, available, mixed = false }: TopicChipsProps) {
  const options: ChipOption<PracticeTopic>[] = topics.map((t) => ({ value: t.slug, label: t.name }));
  if (mixed) options.push({ value: 'mixed', label: 'Mixed practice' });
  return <Chips options={options} selected={selected} onSelect={onSelect} label="Topic" labelledBy={labelledBy} available={available} />;
}

interface AreaChipsProps {
  /** The areas the catalogue offers (ADR-005). */
  areas: readonly AreaSlug[];
  selected: AreaSlug;
  onSelect: (area: AreaSlug) => void;
  labelledBy?: string;
  disabled?: boolean;
}

export function AreaChips({ areas, selected, onSelect, labelledBy, disabled = false }: AreaChipsProps) {
  const options = AREAS.filter((a) => areas.includes(a.slug)).map((a) => ({ value: a.slug, label: a.name }));
  return <Chips options={options} selected={selected} onSelect={onSelect} label="Area" labelledBy={labelledBy} available={disabled ? [] : undefined} />;
}
