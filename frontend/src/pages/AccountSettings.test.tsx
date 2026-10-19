// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { AccountSettings } from './AccountSettings';
import { LearningStatistics } from './LearningStatistics';
import * as api from '../data/api';

vi.mock('../data/api', () => ({ getDisplayName: vi.fn(), saveDisplayName: vi.fn(), deleteAccount: vi.fn(), getLearningStatistics: vi.fn() }));
let root: Root;
let element: HTMLDivElement;
const button = (label: string) => Array.from(element.querySelectorAll('button')).find(item => item.textContent === label)!;
async function type(id: string, value: string) {
  const input = element.querySelector<HTMLInputElement>(`#${id}`)!;
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(input, value);
    input.dispatchEvent(new Event('input', { bubbles: true }));
  });
}
beforeEach(() => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  vi.resetAllMocks();
  vi.mocked(api.getDisplayName).mockResolvedValue(null);
  element = document.createElement('div'); document.body.append(element); root = createRoot(element);
});
afterEach(async () => { await act(async () => root.unmount()); element.remove(); });

it('requires explicit typed confirmation, allows cancellation, blocks duplicate deletion and keeps the account on failure', async () => {
  const onDeleted = vi.fn(async () => {});
  await act(async () => root.render(<AccountSettings onDeleted={onDeleted} onNameSaved={() => {}} />));
  expect(api.deleteAccount).not.toHaveBeenCalled();
  await act(async () => button('Delete account…').click());
  expect(button('Permanently delete account').disabled).toBe(true);
  await type('delete-confirmation', 'delete');
  expect(button('Permanently delete account').disabled).toBe(true);
  await type('delete-confirmation', 'DELETE');
  await act(async () => button('Cancel').click());
  expect(api.deleteAccount).not.toHaveBeenCalled();
  await act(async () => button('Delete account…').click());
  await type('delete-confirmation', 'DELETE');
  let fail!: (error: Error) => void;
  vi.mocked(api.deleteAccount).mockImplementationOnce(() => new Promise((_resolve, reject) => { fail = reject; }));
  await act(async () => { button('Permanently delete account').click(); element.querySelector<HTMLFormElement>('form:last-of-type')?.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); });
  expect(api.deleteAccount).toHaveBeenCalledTimes(1);
  await act(async () => fail(new Error('upstream private detail')));
  expect(onDeleted).not.toHaveBeenCalled();
  expect(element.textContent).toContain('Deletion could not be completed');
  expect(element.textContent).not.toContain('upstream private detail');
  vi.mocked(api.deleteAccount).mockResolvedValueOnce();
  await act(async () => button('Permanently delete account').click());
  expect(onDeleted).toHaveBeenCalledTimes(1);
});

it('saves and removes the optional name and reports failure without losing the input', async () => {
  const saved = vi.fn();
  await act(async () => root.render(<AccountSettings onDeleted={async () => {}} onNameSaved={saved} />));
  await type('display-name', 'Ada');
  vi.mocked(api.saveDisplayName).mockRejectedValueOnce(new Error('failed'));
  await act(async () => button('Save display name').click());
  expect(element.textContent).toContain('could not be saved');
  expect(saved).not.toHaveBeenCalled();
  expect(element.querySelector<HTMLInputElement>('#display-name')!.value).toBe('Ada');
  vi.mocked(api.saveDisplayName).mockResolvedValue();
  await type('display-name', '');
  await act(async () => button('Save display name').click());
  expect(api.saveDisplayName).toHaveBeenLastCalledWith('');
  expect(element.textContent).toContain('Display name removed');
  expect(saved).toHaveBeenCalledTimes(1);
});

it('shows private omission counts, breakdown and UTC trend with an honest empty state and retry', async () => {
  vi.mocked(api.getLearningStatistics).mockRejectedValueOnce(new Error('offline'));
  await act(async () => root.render(<LearningStatistics />));
  expect(element.textContent).toContain('could not be loaded');
  const zero = { checkedAttempts: 0, omitted: 0, rate: null };
  vi.mocked(api.getLearningStatistics).mockResolvedValueOnce({ ...zero, byTopicDifficulty: [], weekly: [{ ...zero, week: '2026-10-19' }] });
  await act(async () => button('Retry constant statistics').click());
  expect(element.textContent).toContain('No checked attempts yet');
  expect(element.textContent).not.toContain('NaN');
  vi.mocked(api.getLearningStatistics).mockResolvedValueOnce({ checkedAttempts: 4, omitted: 1, rate: .25,
    byTopicDifficulty: [{ checkedAttempts: 4, omitted: 1, rate: .25, topic: 'substitution', difficulty: 2 }],
    weekly: [{ checkedAttempts: 4, omitted: 1, rate: .25, week: '2026-10-19' }] });
  await act(async () => root.render(<LearningStatistics key="new-account" />));
  expect(element.textContent).toContain('1 omissions in 4 checked attempts');
  expect(element.textContent).toContain('25.0%');
  expect(element.textContent).toContain('Substitution · 2');
  expect(element.querySelector('time')?.dateTime).toBe('2026-10-19');
});
