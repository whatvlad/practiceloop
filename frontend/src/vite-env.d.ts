/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** FastAPI base address, e.g. the Oracle preview; empty skips the health check. */
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_SUPABASE_URL?: string;
  readonly VITE_SUPABASE_PUBLISHABLE_KEY?: string;
  /** Approved public HTTPS address for canonical URLs and the sitemap; unset on preview. */
  readonly VITE_SITE_URL?: string;
  /** "true" lets public pages be indexed; needs VITE_SITE_URL. Never set on preview. */
  readonly VITE_SITE_INDEXABLE?: string;
  /** Cloudflare Web Analytics site token (public); unset keeps the beacon off. */
  readonly VITE_CF_WEB_ANALYTICS_TOKEN?: string;
  readonly VITE_COOKIEBOT_ID?: string;
}
