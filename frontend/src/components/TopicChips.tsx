import { TOPICS } from '../data/topics';
import type { PracticeTopic } from '../data/types';
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

const TOPIC_OPTIONS: ChipOption<PracticeTopic>[] = TOPICS.map((t) => ({ value: t.slug, label: t.name }));
const WITH_MIXED: ChipOption<PracticeTopic>[] = [...TOPIC_OPTIONS, { value: 'mixed', label: 'Mixed practice' }];

interface TopicChipsProps {
  selected: PracticeTopic;
  onSelect: (topic: PracticeTopic) => void;
  labelledBy?: string;
  available?: readonly PracticeTopic[];
  /** Offer mixed practice as a last chip (#36). */
  mixed?: boolean;
}

export function TopicChips({ selected, onSelect, labelledBy, available, mixed = false }: TopicChipsProps) {
  return <Chips options={mixed ? WITH_MIXED : TOPIC_OPTIONS} selected={selected} onSelect={onSelect} label="Topic" labelledBy={labelledBy} available={available} />;
}
