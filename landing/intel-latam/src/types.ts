/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export type RoleTabId = "revenue" | "procurement" | "innovation";

export interface ChatMessage {
  id: string;
  sender: "user" | "bot";
  text: string;
  timestamp: string;
}

export interface PresetQuery {
  label: string;
  query: string;
  iconName: string;
}

export interface PricingTier {
  name: string;
  priceMonthly: string;
  priceAnnual: string;
  description: string;
  features: string[];
  ctaText: string;
  highlighted: boolean;
  badge?: string;
}
