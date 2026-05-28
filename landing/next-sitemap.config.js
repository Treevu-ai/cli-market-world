/** @type {import('next-sitemap').IConfig} */
module.exports = {
  siteUrl: "https://cli-market.dev",
  generateRobotsTxt: true,
  outDir: "./out",
  changefreq: "weekly",
  priority: 0.7,
  exclude: ["/404"],
  robotsTxtOptions: {
    policies: [{ userAgent: "*", allow: "/" }],
    additionalSitemaps: [],
  },
};
