// Cloudflare Pages Function for the feedback form: more specific than api/[[path]],
// so /api/feedback is answered here and never reaches the Oracle API.
import { handleFeedback } from '../../src/edge/feedback';

interface Context {
  request: Request;
  env: { RESEND_API_KEY?: string };
}

export const onRequest = ({ request, env }: Context): Promise<Response> =>
  handleFeedback(request, env.RESEND_API_KEY);
