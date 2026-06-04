import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Política de Privacidad / Privacy Policy — CLI Market",
  description: "CLI Market Privacy Policy / Política de Privacidad. How we collect, use, and protect your data.",
  alternates: { canonical: "/legal/privacy" },
};

export default function PrivacyLayout({ children }: { children: React.ReactNode }) {
  return children;
}
