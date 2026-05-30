/**
 * Cloudflare Pages middleware — sticky hero variant cookie at the edge.
 * Enable with HERO_AB=1 in Cloudflare Pages env (alongside NEXT_PUBLIC_HERO_AB=1 at build).
 */
const VARIANTS = ["a", "b", "c", "d", "e", "f"] as const;
const COOKIE = "cm_hero_variant";
const MAX_AGE = 60 * 60 * 24 * 30;

type Variant = (typeof VARIANTS)[number];

function isVariant(v: string): v is Variant {
  return (VARIANTS as readonly string[]).includes(v);
}

function readCookie(header: string | null, name: string): string | null {
  if (!header) return null;
  const match = header.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function pickRandom(): Variant {
  return VARIANTS[Math.floor(Math.random() * VARIANTS.length)];
}

export async function onRequest(context: {
  request: Request;
  env: { HERO_AB?: string };
  next: () => Promise<Response>;
}): Promise<Response> {
  const response = await context.next();

  if (context.env.HERO_AB !== "1") {
    return response;
  }

  const url = new URL(context.request.url);
  const fromQuery = url.searchParams.get("hero")?.toLowerCase() ?? "";
  let variant: Variant | null = isVariant(fromQuery) ? fromQuery : null;

  if (!variant) {
    const fromCookie = readCookie(context.request.headers.get("Cookie"), COOKIE);
    variant = fromCookie && isVariant(fromCookie) ? fromCookie : pickRandom();
  }

  const headers = new Headers(response.headers);
  headers.append(
    "Set-Cookie",
    `${COOKIE}=${encodeURIComponent(variant)}; Path=/; Max-Age=${MAX_AGE}; SameSite=Lax; Secure`,
  );
  headers.set("X-Hero-Variant", variant);

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}
