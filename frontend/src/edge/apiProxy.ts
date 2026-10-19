const FORWARDED_HEADERS = ['accept', 'authorization', 'content-type'];

/** Forwards /api/<path>?<query> to <origin>/<path>?<query>, keeping only the headers the API reads. */
export async function proxyToApi(
  request: Request,
  origin: string,
  fetchImpl: typeof fetch = fetch,
): Promise<Response> {
  const base = origin.trim().replace(/\/+$/, '');
  if (!base) return new Response('API_ORIGIN is not set', { status: 503 });

  const url = new URL(request.url);
  const target = `${base}${url.pathname.replace(/^\/api(?=\/|$)/, '') || '/'}${url.search}`;
  const headers = new Headers();
  for (const name of FORWARDED_HEADERS) {
    const value = request.headers.get(name);
    if (value !== null) headers.set(name, value);
  }
  const hasBody = request.method !== 'GET' && request.method !== 'HEAD';
  try {
    const response = await fetchImpl(target, {
      method: request.method,
      headers,
      body: hasBody ? await request.arrayBuffer() : undefined,
      redirect: 'manual',
    });
    return new Response(response.body, { status: response.status, headers: response.headers });
  } catch {
    return new Response('API unreachable', { status: 502 });
  }
}
