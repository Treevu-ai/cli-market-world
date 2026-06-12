/** Human-readable retailer labels for compare UI. */
export function storeLabel(store: string): string {
  const map: Record<string, string> = {
    metro_pe: "Metro",
    wong_pe: "Wong",
    plaza_vea_pe: "Plaza Vea",
    plazavea: "Plaza Vea",
  };
  return map[store] ?? store.replace(/_/g, " ");
}
