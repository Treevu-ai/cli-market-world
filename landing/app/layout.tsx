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

export const metadata: Metadata = {
  title: "CLI Market — Infraestructura de comercio y precios para agentes de IA",
  description:
    "30 retailers, 7 países, 2 plataformas. 13,000+ precios reales cada 8 horas. Una API. Cero scraping.",
  openGraph: {
    title: "CLI Market — Infraestructura de comercio y precios para agentes de IA",
    description: "30 retailers en 7 países. 13K precios reales cada 8 horas. Checkout con PayPal + QR (Yape/Plin).",
    url: "https://cli-market.dev",
    siteName: "CLI Market",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "CLI Market — 30 retailers. Una API.",
    description: "30 retailers en 7 países. 13K precios reales cada 8 horas. Cero scraping.",
  },
};

import { LanguageProvider } from "@/lib/LanguageContext";
import { ModeProvider } from "@/hooks/useMode";

const jsonLd = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "CLI Market",
  "applicationCategory": "DeveloperApplication",
  "operatingSystem": "Linux, macOS, Windows",
  "description": "Commerce infrastructure for AI agents. 30 retailers, 7 countries. 13,000+ real prices. One API. Cero scraping.",
  "url": "https://cli-market.dev",
  "author": {
    "@type": "Organization",
    "name": "SINAPSIS INNOVADORA S.A.C.",
    "taxID": "20613045563",
    "address": { "@type": "PostalAddress", "addressLocality": "Lima", "addressCountry": "PE" },
    "founder": { "@type": "Person", "name": "Antonio Cuba", "jobTitle": "Founder & Product Owner" }
  },
  "offers": [
    { "@type": "Offer", "name": "Free", "price": "0", "priceCurrency": "USD" },
    { "@type": "Offer", "name": "Pro", "price": "49", "priceCurrency": "USD" }
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="h-full">
      <body
        className={`${spaceGrotesk.variable} ${ibmPlexMono.variable} h-full bg-[#e8ebe6] overflow-x-hidden`}
      >
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
        <ModeProvider><LanguageProvider>{children}</LanguageProvider></ModeProvider>
      </body>
    </html>
  );
}
