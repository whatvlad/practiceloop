import { describe, expect, it } from 'vitest';
import { renderToStaticMarkup } from 'react-dom/server';
import { createElement } from 'react';
import { SiteFooter } from './components/SiteFooter';
import { SUPPORT_AFTER_SOLVED, SUPPORT_SNOOZE_DAYS, dismissSupportNotice, recordSolved, supportNoticeDue } from './support';

const URL_ = 'https://ko-fi.com/example';
const DAY = 24 * 60 * 60 * 1000;

function memory() {
  const data = new Map<string, string>();
  return { getItem: (k: string) => data.get(k) ?? null, setItem: (k: string, v: string) => { data.set(k, v); } };
}

describe('support notice', () => {
  it('waits until enough problems are solved', () => {
    const store = memory();
    for (let i = 1; i < SUPPORT_AFTER_SOLVED; i += 1) recordSolved(store);
    expect(supportNoticeDue(URL_, 0, store)).toBe(false);
    recordSolved(store);
    expect(supportNoticeDue(URL_, 0, store)).toBe(true);
  });

  it('stays hidden without a support page', () => {
    const store = memory();
    for (let i = 0; i < SUPPORT_AFTER_SOLVED; i += 1) recordSolved(store);
    expect(supportNoticeDue('', 0, store)).toBe(false);
  });

  it('returns only after the snooze period once closed', () => {
    const store = memory();
    for (let i = 0; i < SUPPORT_AFTER_SOLVED; i += 1) recordSolved(store);
    dismissSupportNotice(1000, store);
    expect(supportNoticeDue(URL_, 1000 + (SUPPORT_SNOOZE_DAYS - 1) * DAY, store)).toBe(false);
    expect(supportNoticeDue(URL_, 1000 + SUPPORT_SNOOZE_DAYS * DAY, store)).toBe(true);
  });

  it('survives broken storage', () => {
    const broken = { getItem: () => { throw new Error('denied'); }, setItem: () => { throw new Error('denied'); } };
    expect(() => recordSolved(broken)).not.toThrow();
    expect(supportNoticeDue(URL_, 0, broken)).toBe(false);
  });
});

describe('footer support link', () => {
  it('opens the support page in a new tab', () => {
    const html = renderToStaticMarkup(createElement(SiteFooter, { supportUrl: URL_ }));
    expect(html).toContain(`href="${URL_}" target="_blank" rel="noopener noreferrer">Support</a>`);
  });

  it('is absent until a page is configured', () => {
    expect(renderToStaticMarkup(createElement(SiteFooter, { supportUrl: '' }))).not.toContain('Support</a>');
  });
});
