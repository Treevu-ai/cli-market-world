import type { Metadata } from "next";
import { Space_Grotesk, IBM_Plex_Mono } from "next/font/google";
import { LangProvider } from "@/components/lang";
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
  title: "CLI Market — Infraestructura de comercio para agentes de IA",
  description:
    "100 retailers VTEX en 12 países y 12 líneas de negocio. API REST, CLI y 12 herramientas MCP para agentes de inteligencia artificial. Open source.",
  openGraph: {
    title: "CLI Market — Infraestructura de comercio para agentes IA",
    description: "100 retailers, 12 líneas, 12 países. Una sola API. Open source.",
    url: "https://cli-market.dev",
    siteName: "CLI Market",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "CLI Market — Comercio para agentes IA",
    description: "100 retailers VTEX en 12 países. API REST, CLI y 12 MCP tools.",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className="h-full">
      <body
        className={`${spaceGrotesk.variable} ${ibmPlexMono.variable} h-full bg-[#0A0A0A] overflow-x-hidden`}
      >
        <LangProvider>{children}</LangProvider>
      </body>
    </html>
  );
}
