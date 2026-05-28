import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "MCP Tools — 36 copy-paste configs for AI agents",
  description:
    "MCP tools for e-commerce and AI shopping API integration. Copy-paste configs for Cursor, Claude Desktop, and VS Code. 36 commerce tools across 30 retailers.",
  keywords: [
    "MCP tools for e-commerce",
    "commerce API for AI agents",
    "AI shopping API",
    "Model Context Protocol",
    "cli-market MCP",
  ],
  alternates: {
    canonical: "/tools",
  },
  openGraph: {
    title: "CLI Market MCP Tools — Agent commerce configs",
    description: "36 MCP tools. Copy-paste server configs for Cursor and Claude.",
    url: "https://cli-market.dev/tools",
    type: "website",
  },
};

export default function ToolsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
