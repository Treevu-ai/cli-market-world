import { MARKET_STATS } from "@/lib/marketStats";

/** Verified / active retailers shown on the retailers page ticker (marketing sample). */
const VTEX_ACTIVE = [
  "Wong PE",
  "Metro PE",
  "Plaza Vea PE",
  "Carrefour AR",
  "Jumbo AR",
  "Vea AR",
  "Chedraui MX",
  "HEB MX",
  "Éxito CO",
  "Carulla CO",
  "Olimpica CO",
  "Sam's Club BR",
  "Farmatodo MX",
  "Cruz Verde CL",
  "Motorola MX",
  "Electrolux CL",
  "Samsung",
  "C&A Brasil",
];

const MAGENTO_ACTIVE = ["Falabella CL", "Paris CL", "Ripley CL", "Liverpool MX", "El Palacio MX"];

export const ACTIVE_BRAND_NAMES: readonly string[] = [
  ...VTEX_ACTIVE,
  ...MAGENTO_ACTIVE,
  ...MARKET_STATS.shopifyBrands,
  ...MARKET_STATS.woocommerceStores,
];
