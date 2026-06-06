/**
 * Cloudflare Pages middleware — canonical host redirects.
 * Requires www.cli-market.dev as a custom domain (or zone redirect rule).
 */
export async function onRequest(context) {
  const url = new URL(context.request.url);

  if (url.hostname === "www.cli-market.dev") {
    url.hostname = "cli-market.dev";
    return Response.redirect(url.toString(), 301);
  }

  if (url.hostname === "cli-market-world.pages.dev") {
    url.hostname = "cli-market.dev";
    return Response.redirect(url.toString(), 301);
  }

  return context.next();
}