import type { Metadata } from "next";
import Script from "next/script";
import { Inter, JetBrains_Mono } from "next/font/google";
import { GeistSans } from "geist/font/sans";
import "./globals.css";
import { MARKET_STATS } from "@/lib/marketStats";
import { buildFaqJsonLd } from "@/lib/faqSchema";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
});

const siteUrl = "https://cli-market.dev";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "CLI Market — AI commerce API & MCP tools for agents",
    template: "%s | CLI Market",
  },
  description: MARKET_STATS.seoDescription,
  keywords: [
    "commerce API for AI agents",
    "AI shopping API",
    "MCP tools for e-commerce",
    "price data API",
    "VTEX API integration",
    "agentic commerce",
    "Latin America retail data",
  ],
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "CLI Market — AI commerce API & MCP tools for agents",
    description: `${MARKET_STATS.retailersPhraseEn}. ${MARKET_STATS.mcpTools} MCP tools. ${MARKET_STATS.pricesVerifiedLabel} verified prices every ${MARKET_STATS.pricesRefreshHours} hours. Quality-filtered spreads and basket compare.`,
    url: siteUrl,
    siteName: "CLI Market",
    type: "website",
    locale: "es_PE",
    alternateLocale: ["en_US"],
    images: [
      {
        url: "/og.png",
        width: 1200,
        height: 630,
        alt: "CLI Market — commerce infrastructure for AI agents",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "CLI Market — Commerce infrastructure for AI agents",
    description: `AI commerce API + MCP tools. ${MARKET_STATS.retailersPhraseEn}. One pip install. Zero scraping.`,
    images: ["/og.png"],
  },
};

import { LanguageProvider } from "@/lib/LanguageContext";
import { ModeProvider } from "@/hooks/useMode";

const cfBeaconToken = process.env.NEXT_PUBLIC_CF_BEACON_TOKEN;
const plausibleDomain = process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN;

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      name: "SINAPSIS INNOVADORA S.A.C.",
      legalName: "SINAPSIS INNOVADORA S.A.C.",
      taxID: "20613045563",
      url: siteUrl,
      logo: `${siteUrl}/logo.svg`,
      founder: {
        "@type": "Person",
        name: "Ricardo Cuba",
        jobTitle: "Founder & Product Owner",
      },
      sameAs: [
        "https://github.com/Treevu-ai/cli-market-world",
        "https://pypi.org/project/cli-market/",
        "https://www.linkedin.com/company/cli-market/",
        "https://x.com/cli_market_dev",
      ],
    },
    {
      "@type": "SoftwareApplication",
      name: "CLI Market",
      applicationCategory: "DeveloperApplication",
      operatingSystem: "Linux, macOS, Windows",
      description: MARKET_STATS.serverDescription,
      url: siteUrl,
      downloadUrl: "https://pypi.org/project/cli-market/",
      softwareVersion: MARKET_STATS.packageVersion,
      author: {
        "@type": "Organization",
        name: "SINAPSIS INNOVADORA S.A.C.",
      },
      offers: [
        { "@type": "Offer", name: "Free", price: "0", priceCurrency: "USD" },
        { "@type": "Offer", name: "Pro", price: "49", priceCurrency: "USD" },
      ],
    },
    buildFaqJsonLd("es"),
    {
      "@type": "WebAPI",
      name: "CLI Market API",
      url: `${siteUrl}/docs`,
      documentation: `${siteUrl}/llms-full.txt`,
    },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className={`dark h-full ${GeistSans.variable}`}>
      <head>
        <link rel="alternate" type="application/json" href="/server.json" title="MCP server manifest" />
      </head>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} h-full bg-[var(--cm-background)] text-[var(--cm-on-surface)] antialiased overflow-x-hidden`}
      >
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
        {cfBeaconToken ? (
          <Script
            defer
            src="https://static.cloudflareinsights.com/beacon.min.js"
            data-cf-beacon={`{"token":"${cfBeaconToken}"}`}
            strategy="afterInteractive"
          />
        ) : null}
        {plausibleDomain ? (
          <Script
            defer
            data-domain={plausibleDomain}
            src="https://plausible.io/js/script.js"
            strategy="afterInteractive"
          />
        ) : null}
        <ModeProvider><LanguageProvider>{children}</LanguageProvider></ModeProvider>
      </body>
    </html>
  );
}
