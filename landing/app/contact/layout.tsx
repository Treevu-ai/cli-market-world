import type { Metadata } from "next";

const ogImage = "https://cli-market.dev/og.png";

export const metadata: Metadata = {
  title: "Contact",
  description:
    "Contact CLI Market for enterprise pricing, retailer listings, press, or general inquiries. We usually reply the same business day.",
  alternates: { canonical: "/contact" },
  openGraph: {
    title: "Contact — CLI Market",
    description: "Enterprise, retailers, press, or general inquiry — one form.",
    url: "https://cli-market.dev/contact",
    type: "website",
    images: [{ url: ogImage, width: 1200, height: 630, alt: "Contact CLI Market" }],
  },
};

export default function ContactLayout({ children }: { children: React.ReactNode }) {
  return children;
}
