import { TOPICS } from '../data/topics';
import type { TopicSlug } from '../data/types';
import { CheckIcon } from './icons';

interface ChipOption<T extends string> {
  value: T;
  label: string;
}

interface ChipsProps<T extends string> {
  options: readonly ChipOption<T>[];
  selected: T;
  onSelect: (value: T) => void;
  /** Accessible name of the group, e.g. "Topic". */
  label: string;
  labelledBy?: string;
}

/** Single-select pill chips: the topic picker and the history filters. */
export function Chips<T extends string>({ options, selected, onSelect, label, labelledBy }: ChipsProps<T>) {
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

const TOPIC_OPTIONS = TOPICS.map((t) => ({ value: t.slug, label: t.name }));

interface TopicChipsProps {
  selected: TopicSlug;
  onSelect: (slug: TopicSlug) => void;
  labelledBy?: string;
}

export function TopicChips({ selected, onSelect, labelledBy }: TopicChipsProps) {
  return <Chips options={TOPIC_OPTIONS} selected={selected} onSelect={onSelect} label="Topic" labelledBy={labelledBy} />;
}
