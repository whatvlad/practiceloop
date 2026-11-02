const FORWARDED_HEADERS = ['accept', 'authorization', 'content-type', 'idempotency-key'];
// Cloudflare answers 530 (error 1016) when it cannot resolve the origin's sslip.io name. The
// request never reached the API, so repeating it is safe; stopgap until the API has its own domain.
const ORIGIN_DNS_ERROR = 530;
const ATTEMPTS = 3;

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
    const body = hasBody ? await request.arrayBuffer() : undefined;
    let response = await fetchImpl(target, { method: request.method, headers, body, redirect: 'manual' });
    for (let attempt = 1; attempt < ATTEMPTS && response.status === ORIGIN_DNS_ERROR; attempt++) {
      response = await fetchImpl(target, { method: request.method, headers, body, redirect: 'manual' });
    }
    return new Response(response.body, { status: response.status, headers: response.headers });
  } catch {
    return new Response('API unreachable', { status: 502 });
  }
}
