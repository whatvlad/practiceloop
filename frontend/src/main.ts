import { createElement } from 'react';
import { createRoot } from 'react-dom/client';

const root = document.getElementById('root');
if (!root) throw new Error('Missing application root');

createRoot(root).render(createElement('main', null,
  createElement('h1', null, 'PracticeLoop'),
  createElement('p', null, 'Mathematics practice. Development scaffold; MVP flows are being built.'),
));
