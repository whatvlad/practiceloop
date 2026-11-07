import { createRoot } from 'react-dom/client';
import { useState } from 'react';
import '@fontsource/geist/400.css';
import '@fontsource/geist/600.css';
import '@fontsource/geist-mono/400.css';
import '@fontsource/instrument-serif/400.css';
import 'katex/dist/katex.min.css';
import './styles/tokens.css';
import './styles/components.css';
import './styles/app.css';
import { AppNav } from './components/AppNav';
import { PracticeSidebar } from './components/PracticeSidebar';
import { LocalMatrixProblem } from './components/LocalMatrixProblem';
import { LocalRandomPractice } from './components/LocalRandomPractice';
import { LocalDeterminantProblem } from './components/LocalDeterminantProblem';
import { algebraGroups } from './data/algebraGroups';
import type { Catalogue } from './data/types';

// Local-only visual preview: no account or saved-problem access is simulated.
const preview: Catalogue = {
  areas: [
    { slug: 'algebra', name: 'Algebra', mixed: null },
    { slug: 'mathematical-analysis', name: 'Mathematical Analysis', mixed: null },
    { slug: 'probability-statistics', name: 'Probability and Statistics', mixed: null },
  ],
  topics: [...algebraGroups.flatMap(group => group.items.flatMap(item => item.topic
    ? [{ slug: item.topic, name: item.title, area: 'algebra' as const, availableDifficulties: [1 as const] }]
    : [])),
    { slug: 'derivatives', name: 'Derivatives', area: 'mathematical-analysis', availableDifficulties: [1, 2, 3] },
    { slug: 'basic-integrals', name: 'Basic integrals', area: 'mathematical-analysis', availableDifficulties: [1, 2] },
    { slug: 'probability-events', name: 'Events and counting', area: 'probability-statistics', availableDifficulties: [1, 2] },
  ],
};
const root = document.getElementById('root');
if (!root) throw new Error('Missing preview root');
function LocalPreview() {
  const [topic, setTopic] = useState('matrix-operations');
  const [menuOpen, setMenuOpen] = useState(false);
  const selectTopic = (next: string) => {
    setTopic(next); setMenuOpen(false);
    if (window.matchMedia('(max-width: 760px)').matches) requestAnimationFrame(() => {
      const content = document.querySelector<HTMLElement>('.pl-workspace-content');
      content?.focus({ preventScroll: true }); content?.scrollIntoView({ block: 'start' });
    });
  };
  return <div className="pl-page">
  <AppNav current="/dashboard" initial="A" onLogOut={() => {}} busy={false} />
  <div className="pl-wrap pl-api-notice"><p className="pl-small pl-muted">Local visual preview — practice links require a configured account.</p></div>
  <button type="button" className="pl-btn pl-btn--secondary pl-local-menu-toggle" aria-expanded={menuOpen} aria-controls="local-topic-panel" onClick={() => setMenuOpen(!menuOpen)}>{menuOpen ? 'Close topics' : 'Choose topic'}</button>
  <div className="pl-workspace"><div id="local-topic-panel" className={`pl-local-topic-panel${menuOpen ? ' is-open' : ''}`}><PracticeSidebar preview={preview} onPreviewTopic={selectTopic} onLocalRandom={() => selectTopic('local-random')} /></div><div className="pl-workspace-content" tabIndex={-1}>{topic === 'local-random' ? <LocalRandomPractice /> : topic === 'determinants' || topic === 'inverse-matrices' || topic === 'matrix-rank' || topic === 'linear-systems' || topic === 'complex-arithmetic' || topic === 'complex-numbers' || topic === 'complex-polar-form' || topic === 'complex-conversion' || topic === 'polynomial-division' || topic === 'polynomial-roots' || topic === 'polynomial-operations' || topic === 'partial-fractions' || topic === 'fundamental-theorem-algebra' ? <LocalDeterminantProblem key={topic} topic={topic} /> : <LocalMatrixProblem />}</div></div>
</div>;
}
createRoot(root).render(<LocalPreview />);
