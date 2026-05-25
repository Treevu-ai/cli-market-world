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
  title: "CLI Market — 60 retailers. Una API. Tus agentes compran solos.",
  description:
    "60 retailers en 11 países, 3 plataformas. 36 herramientas MCP. Precios reales de góndola actualizados cada 8 horas. Una API. Cero scraping.",
  openGraph: {
    title: "CLI Market — Comercio programable para agentes de IA",
    description: "60 retailers, 11 países, 3 plataformas. 36 MCP tools. Precios reales. Sin scraping.",
    url: "https://cli-market.dev",
    siteName: "CLI Market",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "CLI Market — 60 retailers. Una API.",
    description: "60 retailers en 11 países. 36 MCP tools. Precios reales cada 8 horas.",
  },
};

import { LanguageProvider } from "@/lib/LanguageContext";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="h-full">
      <body
        className={`${spaceGrotesk.variable} ${ibmPlexMono.variable} h-full bg-[#131313] overflow-x-hidden`}
      >
        <LanguageProvider>{children}</LanguageProvider>
      </body>
    </html>
  );
}
