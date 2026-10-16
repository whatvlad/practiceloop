import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { Link } from '../router';
import { ArrowIcon } from './icons';

export type ButtonVariant = 'primary' | 'secondary' | 'ghost';

interface ButtonStyle {
  variant?: ButtonVariant;
  size?: 'sm' | 'md' | 'lg';
  pill?: boolean;
  block?: boolean;
  /** Trailing arrow: the action moves forward. */
  arrow?: boolean;
  className?: string;
  children: ReactNode;
}

export function buttonClass({ variant = 'primary', size = 'md', pill, block, className }: Omit<ButtonStyle, 'children'>): string {
  return [
    'pl-btn',
    `pl-btn--${variant}`,
    size !== 'md' && `pl-btn--${size}`,
    pill && 'pl-btn--pill',
    block && 'pl-btn--block',
    className,
  ]
    .filter(Boolean)
    .join(' ');
}

type ButtonProps = ButtonStyle & Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'className' | 'children'>;

export function Button({ variant, size, pill, block, arrow, className, children, type = 'button', ...rest }: ButtonProps) {
  return (
    <button type={type} className={buttonClass({ variant, size, pill, block, className })} {...rest}>
      {children}
      {arrow && <ArrowIcon />}
    </button>
  );
}

type ButtonLinkProps = ButtonStyle & { to: string };

export function ButtonLink({ variant, size, pill, block, arrow, className, children, to }: ButtonLinkProps) {
  return (
    <Link to={to} className={buttonClass({ variant, size, pill, block, className })}>
      {children}
      {arrow && <ArrowIcon />}
    </Link>
  );
}
