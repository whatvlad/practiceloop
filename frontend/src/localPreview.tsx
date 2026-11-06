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
import { LocalDeterminantProblem } from './components/LocalDeterminantProblem';
import { algebraGroups } from './data/algebraGroups';
import type { Catalogue } from './data/types';
import { CurriculumPage } from './pages/CurriculumPage';

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
  return <div className="pl-page">
  <AppNav current="/dashboard" initial="A" onLogOut={() => {}} busy={false} />
  <div className="pl-wrap pl-api-notice"><p className="pl-small pl-muted">Local visual preview — practice links require a configured account.</p></div>
  <div className="pl-workspace"><PracticeSidebar preview={preview} onPreviewTopic={setTopic} /><div className="pl-workspace-content">{topic === 'determinants' || topic === 'inverse-matrices' ? <LocalDeterminantProblem key={topic} topic={topic} /> : <LocalMatrixProblem />}<CurriculumPage /></div></div>
</div>;
}
createRoot(root).render(<LocalPreview />);
