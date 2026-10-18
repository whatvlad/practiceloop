/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** FastAPI base address, e.g. the Oracle preview; empty skips the health check. */
  readonly VITE_API_BASE_URL?: string;
  readonly VITE_SUPABASE_URL?: string;
  readonly VITE_SUPABASE_PUBLISHABLE_KEY?: string;
}
