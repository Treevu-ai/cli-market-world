"use client";

import BillingCheckoutTrigger from "@/components/BillingCheckoutTrigger";
import type { ProcurePlanSlug } from "@/lib/procurePlans";

export default function ProcureSubscribeButton({
  plan,
  className = "btn-mint w-full",
  autoOpen = false,
}: {
  plan: ProcurePlanSlug;
  className?: string;
  autoOpen?: boolean;
}) {
  return (
    <BillingCheckoutTrigger
      kind={{ type: "procure", plan }}
      className={className}
      autoOpen={autoOpen}
      label_es="Suscribir →"
      label_en="Subscribe →"
    />
  );
}