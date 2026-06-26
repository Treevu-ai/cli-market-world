/** Public site URL (apex). Override at build via NEXT_PUBLIC_PROCURE_SITE_URL. */
export const PROCURE_SITE_URL = (
  process.env.NEXT_PUBLIC_PROCURE_SITE_URL || "https://procurecopilot.com"
).replace(/\/$/, "");

export const PROCURE_SITE_NAME = "Procure Copilot";

export const PROCURE_OG_IMAGE = `${PROCURE_SITE_URL}/og.png`;

export const PROCURE_DEFAULT_TITLE =
  "Procure Copilot | AI Procurement Platform";

export const PROCURE_DEFAULT_DESCRIPTION =
  "AI-native procurement infrastructure for enterprise purchasing in Latin America. Compare shelf prices, approvals, and checkout — from $29/mo.";

export const PROCURE_PROCURE_TITLE =
  "Procure Copilot — Procurement inteligente para empresas en LatAm";

export const PROCURE_PROCURE_DESCRIPTION =
  "Compara compras en retailers verificados (8 países). Desde $29/mes. Aprobaciones, data-gate y checkout. Sin WhatsApp. Sin Excel.";
