import type { Metadata } from "next";
import {
  PROCURE_DEFAULT_DESCRIPTION,
  PROCURE_DEFAULT_TITLE,
  PROCURE_OG_IMAGE,
  PROCURE_PROCURE_DESCRIPTION,
  PROCURE_PROCURE_TITLE,
  PROCURE_SITE_NAME,
  PROCURE_SITE_URL,
} from "@/lib/site";

export const rootMetadata: Metadata = {
  metadataBase: new URL(PROCURE_SITE_URL),
  title: {
    default: PROCURE_DEFAULT_TITLE,
    template: `%s | ${PROCURE_SITE_NAME}`,
  },
  description: PROCURE_DEFAULT_DESCRIPTION,
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: PROCURE_SITE_NAME,
    description:
      "AI-native procurement platform for LatAm — compare, approve, checkout.",
    url: PROCURE_SITE_URL,
    siteName: PROCURE_SITE_NAME,
    type: "website",
    locale: "es_PE",
    alternateLocale: ["en_US"],
    images: [
      {
        url: PROCURE_OG_IMAGE,
        width: 1200,
        height: 630,
        alt: "Procure Copilot — AI procurement for Latin America",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: PROCURE_DEFAULT_TITLE,
    description: PROCURE_DEFAULT_DESCRIPTION,
    images: [PROCURE_OG_IMAGE],
  },
};

export const procurePageMetadata: Metadata = {
  title: PROCURE_PROCURE_TITLE,
  description: PROCURE_PROCURE_DESCRIPTION,
  alternates: { canonical: "/procure" },
  openGraph: {
    title: PROCURE_PROCURE_TITLE,
    description: PROCURE_PROCURE_DESCRIPTION,
    url: `${PROCURE_SITE_URL}/procure`,
    siteName: PROCURE_SITE_NAME,
    images: [{ url: PROCURE_OG_IMAGE, width: 1200, height: 630 }],
  },
  twitter: {
    card: "summary_large_image",
    title: PROCURE_PROCURE_TITLE,
    description: PROCURE_PROCURE_DESCRIPTION,
    images: [PROCURE_OG_IMAGE],
  },
};

export const organizationJsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      name: PROCURE_SITE_NAME,
      url: PROCURE_SITE_URL,
      logo: `${PROCURE_SITE_URL}/logo.svg`,
      sameAs: [
        "https://www.linkedin.com/company/procure-copilot/",
        "https://cli-market.dev/procure",
      ],
    },
    {
      "@type": "SoftwareApplication",
      name: PROCURE_SITE_NAME,
      applicationCategory: "BusinessApplication",
      operatingSystem: "Web",
      url: PROCURE_SITE_URL,
      description: PROCURE_DEFAULT_DESCRIPTION,
      offers: {
        "@type": "AggregateOffer",
        lowPrice: "29",
        highPrice: "149",
        priceCurrency: "USD",
      },
    },
  ],
};
