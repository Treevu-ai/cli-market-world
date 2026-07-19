/**
 * Reverse-proxies cli-market.dev/intel-latam(/*) to the CLI Market
 * Intelligence prototype (a standalone Node/Express app on Fly.io, not part
 * of this repo or the Next.js static export at cli-market.dev).
 *
 * Cloudflare Pages' _redirects only supports true redirects (301/302) to a
 * different origin -- a 200-status "rewrite" is silently ignored for
 * cross-origin destinations, so the request falls through to the Next.js
 * site's own 404 instead of proxying. A Worker on an explicit zone route is
 * the only way to keep the browser's URL under cli-market.dev while
 * fetching content from Fly.
 */

const UPSTREAM_ORIGIN = "https://cli-market-intelligence.fly.dev";
const MOUNT_PREFIX = "/intel-latam";

export default {
  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const upstreamPath = url.pathname.startsWith(MOUNT_PREFIX)
      ? url.pathname.slice(MOUNT_PREFIX.length) || "/"
      : url.pathname;

    const upstreamUrl = new URL(upstreamPath + url.search, UPSTREAM_ORIGIN);

    const upstreamRequest = new Request(upstreamUrl, request);
    upstreamRequest.headers.set("Host", new URL(UPSTREAM_ORIGIN).host);

    const response = await fetch(upstreamRequest);

    // Fly's response headers pass through as-is; strip anything that would
    // leak the upstream's own domain/cookies into the cli-market.dev origin.
    const headers = new Headers(response.headers);
    headers.delete("set-cookie");

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers,
    });
  },
};
