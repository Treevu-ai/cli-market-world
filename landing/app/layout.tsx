import type { Metadata } from "next";
import Script from "next/script";
import { Inter, JetBrains_Mono, EB_Garamond } from "next/font/google";
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

const ebGaramond = EB_Garamond({
  variable: "--font-garamond",
  subsets: ["latin"],
  weight: ["400", "500"],
  style: ["normal", "italic"],
});

const siteUrl = "https://cli-market.dev";
const ogImage = `${siteUrl}/og.png`;
const ogVideoMp4 = `${siteUrl}/cli-market-hero.mp4`;
const ogVideoWebm = `${siteUrl}/cli-market-hero.webm`;

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "CLI Market — Infraestructura de comercio para agentes de IA",
    template: "%s | CLI Market",
  },
  description:
    "Precios de góndola verificados en LATAM, con interfaz de agente: CLI, API y MCP. Elige Build (API/MCP), Procure (compras) o Intelligence (señales) sobre la misma data.",
  keywords: [
    "retail price intelligence LATAM",
    "commerce API for AI agents",
    "procurement software LATAM",
    "shelf price inflation data",
    "retail analytics Latin America",
    "AI shopping API",
    "price data API",
  ],
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "CLI Market — Infraestructura de comercio para agentes de IA",
    description: `${MARKET_STATS.retailersPhraseEn}. CLI, API y MCP sobre una capa de datos verificada — Build (API/MCP), Procure (compras), Intelligence (señales). ${MARKET_STATS.pricesVerifiedLabel} verified prices every ${MARKET_STATS.pricesRefreshHours} hours.`,
    url: siteUrl,
    siteName: "CLI Market",
    type: "website",
    locale: "es_PE",
    alternateLocale: ["en_US"],
    images: [
      {
        url: ogImage,
        width: 1200,
        height: 630,
        alt: "CLI Market — commerce infrastructure for AI agents",
      },
    ],
    videos: [
      {
        url: ogVideoMp4,
        width: 1280,
        height: 720,
        type: "video/mp4",
      },
      {
        url: ogVideoWebm,
        width: 1280,
        height: 720,
        type: "video/webm",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "CLI Market — Commerce infrastructure for AI agents",
    description: `AI commerce API. ${MARKET_STATS.retailersPhraseEn}. One pip install. Zero scraping.`,
    images: [ogImage],
  },
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "32x32" },
      { url: "/favicon.svg", type: "image/svg+xml" },
    ],
    shortcut: "/favicon.ico",
    apple: "/favicon.svg",
  },
};

import { LanguageProvider } from "@/lib/LanguageContext";
import { ModeProvider } from "@/hooks/useMode";
import CookieConsent from "@/components/CookieConsent";
import FunnelBeacon from "@/components/FunnelBeacon";

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
        "https://cli-market.dev",
        MARKET_STATS.pypiUrl,
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
      downloadUrl: MARKET_STATS.pypiUrl,
      softwareVersion: MARKET_STATS.packageVersion,
      author: {
        "@type": "Organization",
        name: "SINAPSIS INNOVADORA S.A.C.",
      },
      offers: [
        { "@type": "Offer", name: "Starter", price: "9", priceCurrency: "USD" },
        { "@type": "Offer", name: "Pro", price: "49", priceCurrency: "USD" },
        { "@type": "Offer", name: "Pro Annual", price: "490", priceCurrency: "USD" },
        { "@type": "Offer", name: "Enterprise", price: "custom", priceCurrency: "USD" },
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
        <link rel="alternate" type="application/json" href="/server.json" title="API server manifest" />
        <meta property="og:video" content={ogVideoMp4} />
        <meta property="og:video:secure_url" content={ogVideoMp4} />
        <meta property="og:video:type" content="video/mp4" />
        <meta property="og:video:width" content="1280" />
        <meta property="og:video:height" content="720" />
      </head>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} ${ebGaramond.variable} h-full bg-[var(--cm-background)] text-[var(--cm-on-surface)] antialiased overflow-x-hidden`}
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
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-[200] focus:rounded-lg focus:bg-[#ea580c] focus:px-4 focus:py-2 focus:text-[#f8fafc] focus:text-sm focus:font-semibold"
        >
          Skip to main content
        </a>
        <ModeProvider>
          <LanguageProvider>
            {children}
            <FunnelBeacon />
            <CookieConsent />
          </LanguageProvider>
        </ModeProvider>
      </body>
    </html>
  );
}