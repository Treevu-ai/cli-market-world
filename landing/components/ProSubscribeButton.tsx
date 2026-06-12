"use client";

import BillingCheckoutTrigger from "@/components/BillingCheckoutTrigger";

/** Opens 2-step checkout modal — email/username deferred from pricing cards. */
export default function ProSubscribeButton({
  className,
  kind = { type: "build-pro" },
}: {
  className?: string;
  kind?: import("@/components/BillingCheckoutModal").BillingCheckoutKind;
}) {
  return <BillingCheckoutTrigger kind={kind} className={className ?? "btn-mint w-full"} />;
}