/** Shared API + PayPal config for static landing (Cloudflare Pages). */

export const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ||
  "https://cli-market-production.up.railway.app";

export const PAYPAL_CLIENT_ID =
  process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID ||
  "BAAfBIr1EMh4S3ZeKdHlf2mpimlRKr2r7E2b7bNxFgu5h9LX8p40BMhRPgxvCreC-SRhIl1NjyhmdGaJuY";

export const PAYPAL_HOSTED_BUTTON_ID =
  process.env.NEXT_PUBLIC_PAYPAL_HOSTED_BUTTON_ID || "B6YVFTG4MA73J";

export const PRO_PAYMENT_URL =
  process.env.NEXT_PUBLIC_PRO_PAYMENT_URL ||
  `https://www.paypal.com/ncp/payment/${PAYPAL_HOSTED_BUTTON_ID}`;
