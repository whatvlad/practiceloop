// Cloudflare Pages Function: the browser calls /api/* on practiceloop.pages.dev and
// this forwards it to the Oracle API (API_ORIGIN). Networks that intercept HTTPS to
// unfamiliar hosts such as sslip.io (a campus FortiGate, for one) then never see it.
import { proxyToApi } from '../../src/edge/apiProxy';

interface Context {
  request: Request;
  env: { API_ORIGIN?: string };
}

export const onRequest = ({ request, env }: Context): Promise<Response> =>
  proxyToApi(request, env.API_ORIGIN ?? '');
