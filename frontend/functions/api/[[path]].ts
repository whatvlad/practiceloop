// Cloudflare Pages Function: the browser calls /api/* on its own origin and
// this forwards it to the Oracle API (API_ORIGIN).
import { proxyToApi } from '../../src/edge/apiProxy';

interface Context {
  request: Request;
  env: { API_ORIGIN?: string };
}

export const onRequest = ({ request, env }: Context): Promise<Response> =>
  proxyToApi(request, env.API_ORIGIN ?? '');
