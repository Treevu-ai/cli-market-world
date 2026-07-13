"use client";

import { useEffect, useState } from "react";

import {
  paymentsChannelsForCheckout,
  paymentsChannelsShort,
  pricingBillingFootnote,
  pricingBillingFootnoteDefault,
} from "@/lib/billingCopy";

/** Hydration-safe label for pricing cards (updates after mount in Peru). */
export function usePaymentsChannels(isES: boolean): string {
  const [label, setLabel] = useState(() => paymentsChannelsShort(isES));
  useEffect(() => {
    setLabel(paymentsChannelsForCheckout(isES));
  }, [isES]);
  return label;
}

/** Footnote with Peru/international order after client geo detection. */
export function usePricingBillingFootnote(isES: boolean): string {
  const [footnote, setFootnote] = useState(() => pricingBillingFootnoteDefault(isES));
  useEffect(() => {
    setFootnote(pricingBillingFootnote(isES));
  }, [isES]);
  return footnote;
}
