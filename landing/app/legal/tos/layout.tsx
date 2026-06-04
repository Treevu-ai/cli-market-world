import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Términos de Servicio / Terms of Service — CLI Market",
  description: "CLI Market Terms of Service / Términos de Servicio. Governs use of the API, MCP tools, CLI client, and data services.",
  alternates: { canonical: "/legal/tos" },
};

export default function TosLayout({ children }: { children: React.ReactNode }) {
  return children;
}
