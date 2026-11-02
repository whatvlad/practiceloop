import { useState } from 'react';
import { algebraSections, analysisSections } from '../data/curriculum';

export function CurriculumPage() {
  const [area, setArea] = useState<'algebra' | 'analysis'>('algebra');
  const sections = area === 'algebra' ? algebraSections : analysisSections;

  return (
    <main id="main" tabIndex={-1} className="pl-wrap pl-app-main">
      <div className="pl-label">Curriculum</div>
      <h1 className="pl-display-md pl-page-title">Explore mathematics</h1>
      <p className="pl-muted">Choose an area, a section and a problem type. Practice is currently in development.</p>
      <div className="pl-chips" role="group" aria-label="Area">
        <button type="button" className="pl-chip" aria-pressed={area === 'algebra'} onClick={() => setArea('algebra')}>Algebra</button>
        <button type="button" className="pl-chip" aria-pressed={area === 'analysis'} onClick={() => setArea('analysis')}>Mathematical Analysis</button>
      </div>
      <div className="pl-stack pl-gap-4 pl-mt-4">
        {sections.map(section => (
          <details className="pl-card" key={section.name}>
            <summary className="pl-h-lg">{section.name}</summary>
            <div className="pl-stack pl-gap-3 pl-mt-4">
              {section.types.map(type => (
                <details className="pl-card" key={type.name}>
                  <summary className="pl-h-md">{type.name}</summary>
                  <p className="pl-muted">{type.description}</p>
                  {type.subtypes && <ul>{type.subtypes.map(subtype => <li key={subtype}>{subtype}</li>)}</ul>}
                  <p className="pl-display-md" role="status">In develop</p>
                </details>
              ))}
            </div>
          </details>
        ))}
      </div>
    </main>
  );
}
