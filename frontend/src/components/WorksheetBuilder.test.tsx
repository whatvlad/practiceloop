// @vitest-environment jsdom
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { WorksheetBuilder } from './WorksheetBuilder';
import * as api from '../data/api';
import type { Catalogue } from '../data/types';

vi.mock('../data/api', async original => ({ ...await original<typeof import('../data/api')>(),
  getCatalogue: vi.fn(), createWorksheet: vi.fn(), downloadWorksheetPdf: vi.fn() }));

const catalogue: Catalogue = {
  areas: [
    { slug: 'integrals', name: 'Integrals', mixed: { availableDifficulties: [1, 2, 3, 4, 5], weights: { 'basic-integrals': 1, 'integration-by-parts': 2 }, worksheetCapacity: { 1: 20, 2: 20, 3: 20, 4: 20, 5: 20 } } },
    { slug: 'derivatives', name: 'Derivatives', mixed: null },
  ],
  topics: [
    { slug: 'basic-integrals', name: 'Basic integrals', area: 'integrals', availableDifficulties: [1, 2, 3, 4, 5], worksheetCapacity: { 1: 12, 2: 12, 3: 12, 4: 12, 5: 12 } },
    { slug: 'integration-by-parts', name: 'Integration by parts', area: 'integrals', availableDifficulties: [1, 2, 3], worksheetCapacity: { 1: 4, 2: 4, 3: 3 } },
    { slug: 'derivatives', name: 'Derivatives', area: 'derivatives', availableDifficulties: [1, 2], worksheetCapacity: { 1: 9, 2: 9 } },
  ],
};
const made = { id: 'w-1', problemIds: ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
  groups: [{ label: 'Basic integrals, level 4', topic: 'basic-integrals' as const, difficulty: 4 as const, requested: 5, count: 5 },
    { label: 'Integration by parts, level 3', topic: 'integration-by-parts' as const, difficulty: 3 as const, requested: 2, count: 2 }] };

let root: Root;
let element: HTMLDivElement;
const buttons = (label: string) => Array.from(element.querySelectorAll('button')).filter(b => b.textContent?.trim() === label || b.getAttribute('aria-label') === label);
const button = (label: string) => buttons(label)[0];
const groups = () => Array.from(element.querySelectorAll('.pl-worksheet-group'));
const selects = () => Array.from(element.querySelectorAll<HTMLSelectElement>('select'));
const counts = () => Array.from(element.querySelectorAll<HTMLInputElement>('input[type="number"]'));
const shownLevels = (index: number) => Array.from(groups()[index].querySelectorAll('.pl-seg button')).map(b => b.querySelector('.n')?.textContent);

function setValue(input: HTMLInputElement | HTMLSelectElement, value: string) {
  const setter = Object.getOwnPropertyDescriptor(Object.getPrototypeOf(input), 'value')!.set!;
  setter.call(input, value);
  input.dispatchEvent(new Event(input instanceof HTMLSelectElement ? 'change' : 'input', { bubbles: true }));
}

beforeEach(async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  vi.resetAllMocks();
  vi.mocked(api.getCatalogue).mockResolvedValue(catalogue);
  element = document.createElement('div');
  document.body.append(element);
  root = createRoot(element);
  await act(async () => root.render(<WorksheetBuilder start={{ area: 'integrals', topic: 'basic-integrals', difficulty: 4 }} />));
  expect(api.getCatalogue).not.toHaveBeenCalled();
  await act(async () => button('Build a worksheet').click());
});
afterEach(async () => { await act(async () => root.unmount()); element.remove(); });

it('starts with one group from the current problem and says the problems are saved and revealed by the key', () => {
  expect(groups()).toHaveLength(1);
  expect(selects()[0].value).toBe('integrals:basic-integrals');
  expect(groups()[0].querySelector('[aria-pressed="true"] .n')?.textContent).toBe('4');
  expect(counts()[0].value).toBe('5');
  expect(element.textContent).toContain('saved to your history');
  const key = element.querySelector<HTMLInputElement>('input[type="checkbox"]')!;
  expect(key.checked).toBe(true);
  expect(element.textContent).toContain('marked as answer revealed');
  // The only group cannot be removed.
  expect(button('Remove group 1')).toBeUndefined();
});

it('adds and removes groups, hides levels a topic lacks and offers mixed per area', async () => {
  await act(async () => button('Add group').click());
  expect(groups()).toHaveLength(2);
  const options = Array.from(selects()[1].querySelectorAll('option')).map(o => o.textContent);
  expect(options).toEqual(['Basic integrals', 'Integration by parts', 'Mixed integrals', 'Derivatives']);
  await act(async () => setValue(selects()[1], 'integrals:integration-by-parts'));
  expect(shownLevels(1)).toEqual(['1', '2', '3']);
  // Level 4 is not offered by parts, so the group moves to the nearest level.
  expect(groups()[1].querySelector('[aria-pressed="true"] .n')?.textContent).toBe('3');
  await act(async () => button('Remove group 1').click());
  expect(groups()).toHaveLength(1);
  expect(selects()[0].value).toBe('integrals:integration-by-parts');
});

it('shows the cap before generating when a group asks for more than its cell', async () => {
  await act(async () => setValue(selects()[0], 'integrals:integration-by-parts'));
  await act(async () => setValue(counts()[0], '9'));
  expect(element.textContent).toContain('Only 3 different problems exist for Integration by parts, level 3, so this group will have 3.');
  expect(element.textContent).toContain('3 of 40 problems');
});

it('adds a new group where problems are left when the last group used up its cell', async () => {
  await act(async () => setValue(selects()[0], 'integrals:integration-by-parts'));
  await act(async () => button('Add group').click());
  // Parts level 3 holds 3 problems and group 1 takes them all, so the new group takes the nearest level.
  expect(selects()[1].value).toBe('integrals:integration-by-parts');
  expect(groups()[1].querySelector('[aria-pressed="true"] .n')?.textContent).toBe('2');
  await act(async () => groups()[1].querySelectorAll<HTMLButtonElement>('.pl-seg button')[2].click());
  expect(element.textContent).toContain('Earlier groups already use some of Integration by parts, level 3');
  expect(element.textContent).toContain('no problems left');
  expect(button('Generate PDF').disabled).toBe(true);
});

it('enforces the group and problem limits', async () => {
  await act(async () => setValue(counts()[0], '50'));
  expect(counts()[0].value).toBe('20');
  expect(element.textContent).toContain('12 of 40 problems');
  for (let i = 1; i < 4; i += 1) {
    await act(async () => button('Add group').click());
    await act(async () => setValue(counts()[i], '20'));
  }
  // Each new group moves to the nearest level with room left: four basic-integrals cells of 12.
  expect(groups().map(g => g.querySelector('[aria-pressed="true"] .n')?.textContent)).toEqual(['4', '3', '2', '1']);
  expect(element.textContent).toContain('48 of 40 problems');
  expect(element.textContent).toContain('Remove 8.');
  expect(button('Generate PDF').disabled).toBe(true);
  for (let i = 0; i < 4; i += 1) await act(async () => button('Add group').click());
  expect(groups()).toHaveLength(8);
  expect(button('Add group').disabled).toBe(true);
  expect(element.textContent).toContain('at most 8 groups');
});

it('generates, shows progress, downloads and reports what each group got', async () => {
  await act(async () => button('Add group').click());
  await act(async () => setValue(selects()[1], 'integrals:integration-by-parts'));
  await act(async () => setValue(counts()[1], '2'));
  let finish!: () => void;
  vi.mocked(api.createWorksheet).mockResolvedValueOnce(made);
  vi.mocked(api.downloadWorksheetPdf).mockImplementationOnce(() => new Promise(resolve => { finish = resolve; }));
  await act(async () => button('Generate PDF').click());
  expect(api.createWorksheet).toHaveBeenCalledWith({ source: 'generate', paper: 'a4', columns: 1, answerKey: true, groups: [
    { topic: 'basic-integrals', difficulty: 4, count: 5 }, { topic: 'integration-by-parts', difficulty: 3, count: 2 }] });
  expect(button('Making the PDF…')?.disabled).toBe(true);
  expect(selects()[0].disabled).toBe(true);
  await act(async () => finish());
  expect(api.downloadWorksheetPdf).toHaveBeenCalledWith('w-1');
  expect(element.textContent).toContain('Your worksheet with 7 problems was downloaded');
});

it('retries only the download when the PDF fails, and shows a rate limit clearly', async () => {
  vi.mocked(api.createWorksheet).mockResolvedValueOnce(made);
  vi.mocked(api.downloadWorksheetPdf).mockRejectedValueOnce(new Error('The PDF service is busy with another worksheet.'));
  await act(async () => button('Generate PDF').click());
  expect(element.querySelector('[role="alert"]')?.textContent).toContain('busy');
  expect(element.querySelector('[role="alert"]')?.textContent).toContain('retrying makes no new ones');
  vi.mocked(api.downloadWorksheetPdf).mockResolvedValueOnce();
  await act(async () => button('Retry download').click());
  expect(api.createWorksheet).toHaveBeenCalledTimes(1);
  expect(api.downloadWorksheetPdf).toHaveBeenCalledTimes(2);
  vi.mocked(api.createWorksheet).mockRejectedValueOnce(new Error('You have made a lot of worksheets just now. Wait a minute and try again.'));
  await act(async () => button('Generate PDF').click());
  expect(element.querySelector('[role="alert"]')?.textContent).toContain('Wait a minute');
  expect(button('Retry download')).toBeUndefined();
});

it('sends the page options and an answer key turned off', async () => {
  vi.mocked(api.createWorksheet).mockResolvedValueOnce(made);
  vi.mocked(api.downloadWorksheetPdf).mockResolvedValueOnce();
  await act(async () => button('Letter').click());
  await act(async () => button('Two columns').click());
  await act(async () => element.querySelector<HTMLInputElement>('input[type="checkbox"]')!.click());
  expect(element.textContent).toContain('stay unrevealed');
  await act(async () => button('Generate PDF').click());
  expect(api.createWorksheet).toHaveBeenCalledWith(expect.objectContaining({ paper: 'letter', columns: 2, answerKey: false }));
});
