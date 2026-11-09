export type ModulusMode = 'expression' | 'properties' | 'geometry';

export function modulusModeFromSearch(params: URLSearchParams): ModulusMode | undefined {
  const mode = params.get('modulusMode');
  return mode === 'expression' || mode === 'properties' || mode === 'geometry' ? mode : undefined;
}

export function modulusModeQuery(mode: ModulusMode): string {
  return `&modulusMode=${encodeURIComponent(mode)}`;
}
