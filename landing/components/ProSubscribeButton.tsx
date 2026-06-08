"use client";

import BillingCheckoutTrigger from "@/components/BillingCheckoutTrigger";

/** Opens 2-step checkout modal — email/username deferred from pricing cards. */
export default function ProSubscribeButton({ className }: { className?: string }) {
  return <BillingCheckoutTrigger kind={{ type: "build-pro" }} className={className ?? "btn-mint w-full"} />;
}