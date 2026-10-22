// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { VisualBoundary } from './VisualBoundary';

function Broken(): never {
  throw new Error('render failed');
}

it('hides only the failed visual and keeps what is around it', async () => {
  (globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
  const quiet = vi.spyOn(console, 'error').mockImplementation(() => {});
  const element = document.createElement('div');
  const root = createRoot(element);
  await act(async () => root.render(<><ol><li>Step one</li></ol><VisualBoundary><Broken /></VisualBoundary></>));
  expect(element.textContent).toBe('Step one');
  await act(async () => root.unmount());
  quiet.mockRestore();
});
