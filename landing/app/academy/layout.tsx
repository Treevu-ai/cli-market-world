import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Taller de Inteligencia de Mercados — CLI Market Academy",
  description:
    "Pricing, growth, marketing y compras con evidencia, no con intuición. Taller en vivo de 2 horas con Ricardo Cuba Alván, fundador de CLI Market y Procure Copilot.",
  alternates: {
    canonical: "https://cli-market.dev/academy",
  },
  openGraph: {
    title: "Taller de Inteligencia de Mercados — CLI Market Academy",
    description: "Deja de adivinar. Pricing, growth, marketing y compras en una sola sesión en vivo.",
    url: "https://cli-market.dev/academy",
  },
};

export default function AcademyLayout({ children }: { children: React.ReactNode }) {
  return children;
}
