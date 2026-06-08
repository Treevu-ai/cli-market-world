"use client";

import BillingCheckoutTrigger from "@/components/BillingCheckoutTrigger";
import type { ProcurePlanSlug } from "@/lib/procurePlans";

export default function ProcureSubscribeButton({
  plan,
  className = "btn-mint w-full",
}: {
  plan: ProcurePlanSlug;
  className?: string;
}) {
  return (
    <BillingCheckoutTrigger
      kind={{ type: "procure", plan }}
      className={className}
      label_es="Suscribir con PayPal →"
      label_en="Subscribe with PayPal →"
    />
  );
}