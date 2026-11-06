import { createRoot } from 'react-dom/client';
import { MathKeypad } from './components/MathKeypad';
import tokens from './styles/tokens.css?raw';
import components from './styles/components.css?raw';

const host = document.getElementById('original-keypad');
if (!host) throw new Error('Missing mockup keypad');
const shadow = host.attachShadow({ mode: 'open' });
const styles = document.createElement('style');
styles.textContent = `${tokens.replaceAll(':root', ':host')}\n${components}`;
shadow.append(styles);
const root = document.createElement('div');
shadow.append(root);

createRoot(root).render(
  <MathKeypad
    onInsert={(insert) => host.dispatchEvent(new CustomEvent('keypad-insert', { detail: insert }))}
    onMove={(step) => host.dispatchEvent(new CustomEvent('keypad-move', { detail: step }))}
  />,
);
