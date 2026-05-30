import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "API Docs — Quickstart, Compare, MCP",
  description:
    "CLI Market API documentation. Quickstart, authentication, POST /products/compare, basket, Intelligence endpoints, rate limits. 36 MCP tools.",
  keywords: ["CLI Market API", "commerce API docs", "MCP tools", "retail price API", "LatAm"],
  alternates: { canonical: "/docs" },
  openGraph: {
    title: "CLI Market API Docs",
    description: "REST + CLI + MCP reference for verified LatAm retail prices.",
    url: "https://cli-market.dev/docs",
    type: "website",
    images: [{ url: "/og.png", width: 1200, height: 630, alt: "CLI Market API documentation" }],
  },
};

export default function DocsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
