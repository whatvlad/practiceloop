// Cloudflare Pages Function for the feedback form: more specific than api/[[path]],
// so /api/feedback is answered here and never reaches the Oracle API.
import { handleFeedback, type FeedbackEnv } from '../../src/edge/feedback';

interface Context {
  request: Request;
  env: FeedbackEnv;
}

export const onRequest = ({ request, env }: Context): Promise<Response> => handleFeedback(request, env);
