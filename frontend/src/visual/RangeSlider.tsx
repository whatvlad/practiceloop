import { useId, type ReactNode } from 'react';

interface RangeSliderProps {
  label: ReactNode;
  /** Spoken value, e.g. "x = 1.5"; the visible output shows `display` or the same text. */
  valueText: string;
  display?: ReactNode;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
}

/** A labelled native range input: drag, tap, arrow keys, Page Up/Down and Home/End all work. */
export function RangeSlider({ label, valueText, display, value, min, max, step, onChange }: RangeSliderProps) {
  const id = useId();
  return (
    <div className="pl-vis-slider">
      <label htmlFor={id} className="pl-small">{label}</label>
      <output htmlFor={id} className="pl-small pl-mono" aria-hidden="true">{display ?? valueText}</output>
      <input id={id} type="range" min={min} max={max} step={step} value={value} aria-valuetext={valueText}
        onChange={event => onChange(Number(event.currentTarget.value))} />
    </div>
  );
}
