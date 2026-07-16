import type { Metadata } from "next";
import CaseStudiesPage from "@/components/CaseStudiesPage";

const ogImage = "https://cli-market.dev/og.png";

export const metadata: Metadata = {
  title: "Case Studies",
  description:
    "Case studies: fintech intelligence, B2B procurement, trade marketing, AI agents, and retailer listing on CLI Market LATAM price data.",
  alternates: { canonical: "/case-studies" },
  openGraph: {
    title: "Case Studies — CLI Market",
    description: "How teams use Build, Procure, and Advisors on verified LATAM shelf prices.",
    url: "https://cli-market.dev/case-studies",
    type: "website",
    images: [{ url: ogImage, width: 1200, height: 630, alt: "CLI Market case studies" }],
  },
};

export default function Page() {
  return <CaseStudiesPage />;
}
