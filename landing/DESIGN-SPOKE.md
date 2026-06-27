# Spoke Design System — primitives

Canonical hub: `/` · Config: `landing/lib/spokeConfig.ts` · PRD: `docs/prd-landing-spoke-design-system.md`

## Phase A primitives (shipped)

| Component | Path | Role |
|-----------|------|------|
| `SpokePageShell` | `components/spoke/SpokePageShell.tsx` | Glow + Navbar + ErrorBoundary |
| `SpokeHero` | `components/spoke/SpokeHero.tsx` | Hero unificado (garamond, chips, CTAs) |
| `SpokeHubLink` | `components/spoke/SpokeHubLink.tsx` | ← CLI Market |
| `SPOKE_CONFIG` | `lib/spokeConfig.ts` | Copy + brandMode por ICP |

## Usage

```tsx
import SpokePageShell from "@/components/spoke/SpokePageShell";
import SpokeHero from "@/components/spoke/SpokeHero";
import SpokeHubLink from "@/components/spoke/SpokeHubLink";
import { SPOKE_CONFIG } from "@/lib/spokeConfig";

export default function BuildPage() {
  return (
    <SpokePageShell brandMode={SPOKE_CONFIG.build.brandMode} legacyHashRedirect>
      <SpokeHero icp="build" />
      <SpokeHubLink />
      {/* body sections */}
    </SpokePageShell>
  );
}
```

Retailers modal CTA: `<SpokeHero icp="retailers" onPrimaryClick={() => setOpen(true)} />`

## ICP config

| ICP | Route | brandMode | heroBackgroundDense |
|-----|-------|-----------|---------------------|
| build | `/build` | terminal | false |
| intelligence | `/intelligence` | terminal | false |
| retailers | `/retailers` | operations | true |

## Pending (Phase B–D)

- `SpokeSection`, `SpokeStepsSection`, `SpokeFinalCTA`
- Retailers body sections → `landing-container-wide`
- Intelligence retokenize `#0369a1` → `--cm-signal`
