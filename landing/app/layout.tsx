import type { Metadata } from "next";
import { Space_Grotesk, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
  weight: ["400", "500", "700"],
});

const ibmPlexMono = IBM_Plex_Mono({
  variable: "--font-ibm-plex-mono",
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
  description:
    "Commerce API for AI agents. 36 MCP tools, 30 retailers, 8 countries. 13,000+ price data points refreshed every 8 hours. pip install cli-market — zero scraping.",
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
    description:
      "30 retailers in 8 countries. 36 MCP tools. 13K+ real prices every 8 hours. Checkout with PayPal + QR.",
    url: siteUrl,
    siteName: "CLI Market",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "CLI Market — Commerce infrastructure for AI agents",
    description:
      "AI commerce API + MCP tools. 30 retailers. One pip install. Zero scraping.",
  },
};

import { LanguageProvider } from "@/lib/LanguageContext";
import { ModeProvider } from "@/hooks/useMode";

const jsonLd = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "SoftwareApplication",
      name: "CLI Market",
      applicationCategory: "DeveloperApplication",
      operatingSystem: "Linux, macOS, Windows",
      description:
        "Commerce infrastructure for AI agents. AI commerce API with 36 MCP tools across 30 retailers in 8 countries.",
      url: siteUrl,
      downloadUrl: "https://pypi.org/project/cli-market/",
      softwareVersion: "1.4.3",
      author: {
        "@type": "Organization",
        name: "SINAPSIS INNOVADORA S.A.C.",
        taxID: "20613045563",
        address: {
          "@type": "PostalAddress",
          addressLocality: "Lima",
          addressCountry: "PE",
        },
        founder: {
          "@type": "Person",
          name: "Antonio Cuba",
          jobTitle: "Founder & Product Owner",
        },
      },
      offers: [
        { "@type": "Offer", name: "Free", price: "0", priceCurrency: "USD" },
        { "@type": "Offer", name: "Pro", price: "49", priceCurrency: "USD" },
      ],
    },
    {
      "@type": "WebApplication",
      name: "CLI Market",
      url: siteUrl,
      applicationCategory: "BusinessApplication",
      browserRequirements: "Requires JavaScript",
      description:
        "Web presence for CLI Market — AI shopping API, MCP server registry, and retailer listing.",
      sameAs: [
        "https://github.com/Treevu-ai/cli-market-world",
        "https://pypi.org/project/cli-market/",
      ],
    },
    {
      "@type": "WebAPI",
      name: "CLI Market API",
      url: "https://cli-market-production.up.railway.app/docs",
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
    <html lang="es" className="h-full">
      <head>
        <link rel="alternate" type="application/json" href="/server.json" title="MCP server manifest" />
      </head>
      <body
        className={`${spaceGrotesk.variable} ${ibmPlexMono.variable} h-full bg-[#e8ebe6] overflow-x-hidden`}
      >
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
        <ModeProvider><LanguageProvider>{children}</LanguageProvider></ModeProvider>
      </body>
    </html>
  );
}
