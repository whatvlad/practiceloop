import text from '../../../backend/app/content/en.json';
import type { AnswerInputSpec } from './types';

/** Explicit safe projection; no expected values are kept from an API response. */
export function parseAnswerInput(value: unknown): AnswerInputSpec | undefined {
  if (value === undefined) return undefined;
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error(text.service_error);
  const data = value as Record<string, unknown>;
  if (!['boolean', 'finite_set', 'interval'].includes(data.kind as string) || data.maxBytes !== 256
      || (data.kind === 'finite_set' && data.maxItems !== 8)) throw new Error(text.service_error);
  return { kind: data.kind as AnswerInputSpec['kind'], maxBytes: 256, ...(data.kind === 'finite_set' ? { maxItems: 8 as const } : {}) };
}
