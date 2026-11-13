import publicOptions from '../../../backend/app/content/geometry_modes.json';
import { VECTOR_MODES, type VectorMode } from './vectorModes';

export type GeometryMode = keyof typeof publicOptions.modes;
export type GeometryChoice = { id: GeometryMode | VectorMode; label: string; topic: string };
export const GEOMETRY_SECTIONS = publicOptions.sections;

export function geometrySection(id?: string | null) {
  return GEOMETRY_SECTIONS.find(section => section.id === id);
}

export function geometryOptions(topic: string, sectionId?: string): GeometryChoice[] {
  if (!['vectors', 'lines-and-planes'].includes(topic)) return [];
  const section = geometrySection(sectionId);
  if (section) return section.modes.map(id => ({ id: id as GeometryMode, ...publicOptions.modes[id as GeometryMode] }));
  if (topic === 'vectors') return [
    ...VECTOR_MODES.map(mode => ({ ...mode, topic: 'vectors' })),
    ...Object.entries(publicOptions.modes).filter(([id, mode]) => mode.topic === topic
      && !VECTOR_MODES.some(existing => existing.id === id)).map(([id, mode]) => ({ id: id as GeometryMode, ...mode })),
  ];
  if (topic === 'lines-and-planes') return Object.entries(publicOptions.modes)
    .filter(([, mode]) => mode.topic === topic).map(([id, mode]) => ({ id: id as GeometryMode, ...mode }));
  return [];
}

export function geometryModesForTopic(topic: string): readonly string[] {
  return geometryOptions(topic).map(mode => mode.id);
}

export function isGeometryMode(topic: string, value: unknown): value is GeometryMode | VectorMode {
  return typeof value === 'string' && geometryModesForTopic(topic).includes(value);
}
