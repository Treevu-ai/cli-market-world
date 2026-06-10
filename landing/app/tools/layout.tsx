import type { Metadata } from "next";
import { MARKET_STATS } from "@/lib/marketStats";

export const metadata: Metadata = {
  title: `MCP Tools — ${MARKET_STATS.mcpTools} tools · copy-paste configs for AI agents`,
  description:
    `MCP tools for e-commerce and AI shopping API integration. Copy-paste configs for Cursor, Claude Desktop, and VS Code. ${MARKET_STATS.mcpTools} commerce tools across ${MARKET_STATS.retailersVerified} verified retailers.`,
  keywords: [
    "MCP tools for e-commerce",
    "commerce API for AI agents",
    "AI shopping API",
    "Model Context Protocol",
    "cli-market MCP",
    "market mcp-setup",
    "Cursor MCP config",
    "Claude Desktop MCP",
  ],
  alternates: {
    canonical: "/tools",
  },
  openGraph: {
    title: "CLI Market MCP Tools — Agent commerce configs",
    description: `${MARKET_STATS.mcpTools} MCP tools. Copy-paste server configs for Cursor and Claude.`,
    url: "https://cli-market.dev/tools",
    type: "website",
  },
};

export default function ToolsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
