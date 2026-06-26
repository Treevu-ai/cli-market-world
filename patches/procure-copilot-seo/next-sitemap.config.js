/** @type {import('next-sitemap').IConfig} */
module.exports = {
  siteUrl: process.env.NEXT_PUBLIC_PROCURE_SITE_URL || "https://procurecopilot.com",
  generateRobotsTxt: true,
  outDir: "public",
  changefreq: "weekly",
  priority: 0.8,
  exclude: ["/dashboard", "/dashboard/*", "/api/*"],
  robotsTxtOptions: {
    policies: [
      { userAgent: "*", allow: "/" },
      { userAgent: "GPTBot", allow: "/" },
      { userAgent: "ChatGPT-User", allow: "/" },
      { userAgent: "ClaudeBot", allow: "/" },
      { userAgent: "PerplexityBot", allow: "/" },
      { userAgent: "Google-Extended", allow: "/" },
    ],
    additionalSitemaps: [],
  },
  transform: async (config, path) => ({
    loc: path,
    changefreq: config.changefreq,
    priority: path === "/procure" ? 1.0 : config.priority,
    lastmod: new Date().toISOString(),
    alternateRefs: [
      {
        href: `https://www.procurecopilot.com${path}`,
        hreflang: "x-default",
      },
    ],
  }),
};
