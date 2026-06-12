export type TickerItem = {
  product: string;
  store: string;
  price: string;
  direction: "up" | "down";
  change: string;
};

/** Illustrative shelf signals for the hero ticker (demo — not live quotes). */
export const TICKER_ITEMS: TickerItem[] = [
  { product: "ARROZ COSTEÑO 750g", store: "METRO PE", price: "S/ 2.90", direction: "up", change: "+0.3%" },
  { product: "LECHE GLORIA 1L", store: "WONG PE", price: "S/ 4.65", direction: "down", change: "−1.1%" },
  { product: "ACEITE GIRASOL 900ml", store: "CARREFOUR AR", price: "$ 2,899", direction: "up", change: "+2.4%" },
  { product: "HUEVOS x30", store: "JUMBO AR", price: "$ 4,150", direction: "down", change: "−0.8%" },
  { product: "CAFÉ MOLIDO 250g", store: "ÉXITO CO", price: "$ 18,900", direction: "up", change: "+1.6%" },
  { product: "DETERGENTE 2kg", store: "CHEDRAUI MX", price: "$ 145", direction: "up", change: "+0.5%" },
  { product: "PAN MOLDE 600g", store: "PLAZA VEA PE", price: "S/ 7.20", direction: "down", change: "−0.4%" },
  { product: "AZÚCAR 1kg", store: "HEB MX", price: "$ 32.5", direction: "up", change: "+1.2%" },
  { product: "YOGURT 1L", store: "FALABELLA CL", price: "$ 1,990", direction: "down", change: "−2.0%" },
  { product: "FIDEOS 500g", store: "VEA AR", price: "$ 1,210", direction: "up", change: "+3.1%" },
];
