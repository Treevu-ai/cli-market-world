"use client";

import { TICKER_ITEMS, type TickerItem } from "@/lib/tickerItems";

function TickerChip({ item }: { item: TickerItem }) {
  const dirClass = item.direction === "up" ? "price-ticker-dir-up" : "price-ticker-dir-down";
  const arrow = item.direction === "up" ? "▲" : "▼";
  return (
    <span className="price-ticker-item">
      <b>{item.product}</b>
      <span className="price-ticker-sep">·</span>
      {item.store}
      <span className="price-ticker-sep">·</span>
      <b>{item.price}</b>{" "}
      <span className={dirClass}>
        {arrow} {item.change}
      </span>
    </span>
  );
}

export default function PriceTicker() {
  const track = [...TICKER_ITEMS, ...TICKER_ITEMS];
  return (
    <div className="price-ticker brand-mode-terminal" aria-hidden="true">
      <div className="price-ticker-track">
        {track.map((item, i) => (
          <TickerChip key={`${item.product}-${i}`} item={item} />
        ))}
      </div>
    </div>
  );
}
