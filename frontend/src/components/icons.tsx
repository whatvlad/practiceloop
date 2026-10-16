import type { ReactNode } from 'react';

// 24-unit line icons, 2px stroke, round caps and joins, drawn in currentColor.

function Icon({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {children}
    </svg>
  );
}

type IconProps = { className?: string };

export const CheckIcon = (p: IconProps) => <Icon {...p}><path d="M20 6 9 17l-5-5" /></Icon>;
export const CrossIcon = (p: IconProps) => <Icon {...p}><path d="M18 6 6 18M6 6l12 12" /></Icon>;
export const ArrowIcon = (p: IconProps) => <Icon {...p}><path d="M5 12h14M13 6l6 6-6 6" /></Icon>;
export const ChevronIcon = (p: IconProps) => <Icon {...p}><path d="m9 6 6 6-6 6" /></Icon>;
export const DashIcon = (p: IconProps) => <Icon {...p}><path d="M5 12h14" /></Icon>;
export const WarningIcon = (p: IconProps) => (
  <Icon {...p}>
    <path d="M12 9v4M12 17h.01" />
    <path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" />
  </Icon>
);

/** The PracticeLoop mark: a ring with a gap and a centre point. */
export const LoopMark = (p: IconProps) => (
  <Icon {...p}>
    <path d="M20 12a8 8 0 1 1-2.34-5.66" strokeWidth="2.5" />
    <circle cx="12" cy="12" r="2.2" fill="currentColor" stroke="none" />
  </Icon>
);
