const APEX = 'https://mathloop.net';
const PREVIEW = 'https://mathloop.pages.dev';

interface Context {
  request: Request;
  env: { CANONICAL_REDIRECTS?: string };
  next: () => Promise<Response>;
}

export function onRequest({ request, env, next }: Context): Response | Promise<Response> {
  const url = new URL(request.url);
  const enabled = env.CANONICAL_REDIRECTS === 'true';
  let target: string;
  switch (url.hostname) {
    case 'practiceloop.pages.dev':
      target = enabled ? APEX : PREVIEW;
      break;
    case 'mathloop.pages.dev':
    case 'www.mathloop.net':
      if (!enabled) return next();
      target = APEX;
      break;
    default:
      // The apex and branch/hash previews still serve the application and API.
      return next();
  }
  return new Response(null, {
    status: 301,
    headers: {
      Location: target + url.href.slice(url.origin.length),
      'Cache-Control': 'no-store',
      'X-Robots-Tag': 'noindex',
    },
  });
}
