// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { LocalRandomPractice } from './LocalRandomPractice';

it('offers saved algebra random practice for signed-in accounts', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  await act(async () => root.render(<LocalRandomPractice accountId="student" />));
  expect(host.querySelector('section')?.getAttribute('aria-label')).toBe('Random algebra practice');
  expect(host.textContent).toContain('Choose topics');
  await act(async () => root.unmount()); host.remove();
});

it('generates and continues a saved selection without a signed-in account', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  localStorage.clear();
  const host = document.createElement('div'); document.body.append(host); const root = createRoot(host);
  const fetcher = vi.fn(async (_path: string, options?: RequestInit) => {
    expect(JSON.parse(String(options?.body))).toEqual({ level: 2, complexModulus: true, modulusMode: 'expression' });
    return new Response(JSON.stringify({ code: 'modulus', statement: String.raw`\text{Calculate }|1+i|\text{.}` }), { status: 200 });
  });
  vi.stubGlobal('fetch', fetcher);
  await act(async () => root.render(<LocalRandomPractice />));
  const topic = [...host.querySelectorAll('label')].find(label => label.textContent?.trim() === 'Modulus')!.querySelector('input')!;
  await act(async () => topic.click());
  const level = [...host.querySelectorAll('label')].find(label => label.textContent?.startsWith('Difficulty'))!.querySelector('select')!;
  await act(async () => { level.value = '2'; level.dispatchEvent(new Event('change', { bubbles: true })); });
  const type = [...host.querySelectorAll('label')].find(label => label.textContent?.trim() === 'Modulus of an expression')!.querySelector('input')!;
  await act(async () => type.click());
  await act(async () => [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate problem'))!.click());
  expect(host.querySelector('.pl-problem')).not.toBeNull();
  expect(host.querySelector<HTMLDetailsElement>('.pl-local-random-config')?.open).toBe(false);
  await act(async () => [...host.querySelectorAll('button')].find(button => button.textContent?.includes('Generate next problem'))!.click());
  expect(fetcher).toHaveBeenCalledTimes(2);
  await act(async () => root.unmount());
  const restored = createRoot(host);
  await act(async () => restored.render(<LocalRandomPractice />));
  expect([...host.querySelectorAll('label')].find(label => label.textContent?.trim() === 'Modulus')!.querySelector('input')!.checked).toBe(true);
  await act(async () => restored.unmount()); vi.unstubAllGlobals(); localStorage.clear(); host.remove();
});
