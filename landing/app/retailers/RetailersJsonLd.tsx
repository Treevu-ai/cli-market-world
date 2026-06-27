import { MARKET_STATS } from "@/lib/marketStats";

const FAQ_SCHEMA = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "How do I list my store on CLI Market?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Fill out the form with your store name, URL, and category. Our team indexes your catalog with no technical integration required. Free forever.",
      },
    },
    {
      "@type": "Question",
      name: "Is CLI Market free for retailers?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Yes. Completely free. No hidden fees, no usage limits, no credit card required.",
      },
    },
    {
      "@type": "Question",
      name: "Do I need a technical team to integrate?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "No. Just fill out the form with your store URL. Our team handles the indexing. No APIs, no developers, no technical setup.",
      },
    },
    {
      "@type": "Question",
      name: "How many retailers are already on CLI Market?",
      acceptedAnswer: {
        "@type": "Answer",
        text: `${MARKET_STATS.retailersDefined} retailers across ${MARKET_STATS.countries} countries (${MARKET_STATS.retailersVerified} verified active): ${MARKET_STATS.countryCodes.join(", ")}. ${MARKET_STATS.pricesVerifiedLabel} real prices refreshed every ${MARKET_STATS.pricesRefreshHours} hours.`,
      },
    },
    {
      "@type": "Question",
      name: "What is GEO and why does my store need it?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "GEO (Generative Engine Optimization) is the equivalent of SEO for AI agents. When AI assistants like ChatGPT and Claude search for products, they use structured data indexes like CLI Market. If your store isn't indexed, you're invisible to the fastest-growing shopping channel.",
      },
    },
  ],
};

export default function RetailersJsonLd() {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(FAQ_SCHEMA) }}
    />
  );
}
