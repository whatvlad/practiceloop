// The one real backend call so far: liveness of the FastAPI service.

export type ApiHealth = 'ok' | 'unreachable' | 'unconfigured';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? '').trim().replace(/\/+$/, '');

/** Resolves, never rejects: a down, slow or misbehaving API is 'unreachable'. */
export async function checkApiHealth(
  baseUrl: string = API_BASE_URL,
  fetchImpl: typeof fetch = fetch,
  timeoutMs = 5000,
): Promise<ApiHealth> {
  if (!baseUrl) return 'unconfigured';
  try {
    const response = await fetchImpl(`${baseUrl}/health`, { signal: AbortSignal.timeout(timeoutMs) });
    if (!response.ok) return 'unreachable';
    const body: unknown = await response.json();
    return (body as { status?: unknown } | null)?.status === 'ok' ? 'ok' : 'unreachable';
  } catch {
    return 'unreachable';
  }
}
