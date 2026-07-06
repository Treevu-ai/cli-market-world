"use client";

export interface PromoEvent {
  product_id: string;
  name: string;
  brand: string;
  store: string;
  store_name: string;
  price: number;
  list_price: number | null;
  discount: number | null;
  discount_depth_pct: number | null;
  currency: string;
  queried_at: string;
}

function dayLabel(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleDateString("es-PE", { month: "short", day: "numeric" });
}

function groupByDay(events: PromoEvent[]): Map<string, PromoEvent[]> {
  const map = new Map<string, PromoEvent[]>();
  for (const e of events) {
    const day = new Date(e.queried_at).toISOString().slice(0, 10);
    if (!map.has(day)) map.set(day, []);
    map.get(day)!.push(e);
  }
  return map;
}

interface Props {
  events: PromoEvent[];
  myBrand: string;
}

export default function BrandPromoTimeline({ events, myBrand }: Props) {
  if (events.length === 0) {
    return (
      <p className="text-[var(--cm-text-secondary)] text-sm py-8 text-center">
        Sin eventos de promo detectados en el período.
      </p>
    );
  }

  const byDay = groupByDay(events);
  const days = Array.from(byDay.keys()).sort().reverse();

  const myBrandNorm = myBrand.toLowerCase();

  return (
    <div className="space-y-1">
      {/* Summary chips */}
      <div className="flex flex-wrap gap-2 mb-4">
        {Array.from(new Set(events.map((e) => e.store_name))).map((store) => {
          const storeEvents = events.filter((e) => e.store_name === store);
          const myCount = storeEvents.filter((e) => e.brand.toLowerCase() === myBrandNorm).length;
          const compCount = storeEvents.length - myCount;
          return (
            <div
              key={store}
              className="flex items-center gap-2 text-xs font-mono border border-white/10 rounded px-2 py-1 bg-[var(--cm-surface-card)]"
            >
              <span className="text-[var(--cm-ink)]">{store}</span>
              {myCount > 0 && (
                <span className="text-[var(--cm-data)]">{myCount} propias</span>
              )}
              {compCount > 0 && (
                <span className="text-[var(--cm-text-secondary)]">{compCount} competencia</span>
              )}
            </div>
          );
        })}
      </div>

      {/* Timeline */}
      <div className="space-y-3">
        {days.map((day) => {
          const dayEvents = byDay.get(day)!;
          return (
            <div key={day} className="flex gap-3">
              {/* Date col */}
              <div className="w-16 shrink-0 text-right">
                <span className="text-xs text-[var(--cm-text-secondary)] font-mono">
                  {dayLabel(day)}
                </span>
              </div>
              {/* Line */}
              <div className="flex flex-col items-center">
                <div className="w-px flex-1 bg-white/10" />
                <div className="w-1.5 h-1.5 rounded-full bg-[var(--cm-action)] shrink-0" />
                <div className="w-px flex-1 bg-white/10" />
              </div>
              {/* Events */}
              <div className="flex-1 pb-3 space-y-1">
                {dayEvents.map((e, i) => {
                  const isMe = e.brand.toLowerCase() === myBrandNorm;
                  return (
                    <div
                      key={i}
                      className={`text-xs flex flex-wrap items-center gap-x-2 gap-y-0.5 rounded px-2 py-1 border ${
                        isMe
                          ? "border-[var(--cm-data)]/20 bg-[var(--cm-data)]/[0.04]"
                          : "border-white/5 bg-white/[0.02]"
                      }`}
                    >
                      <span
                        className={`font-medium ${
                          isMe ? "text-[var(--cm-data)]" : "text-[var(--cm-text-secondary)]"
                        }`}
                      >
                        {e.brand}
                      </span>
                      <span className="text-[var(--cm-ink)] truncate max-w-[200px]" title={e.name}>
                        {e.name}
                      </span>
                      <span className="text-[var(--cm-text-secondary)]">{e.store_name}</span>
                      <span className="font-mono text-[var(--cm-ink)]">
                        {e.currency} {e.price.toFixed(2)}
                      </span>
                      {e.discount_depth_pct !== null && (
                        <span className="font-mono text-[var(--cm-action)] bg-[var(--cm-action-soft)] border border-[var(--cm-action)]/30 rounded px-1">
                          -{e.discount_depth_pct.toFixed(1)}%
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
