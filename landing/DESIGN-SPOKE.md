# Spoke Design System — primitives

Canonical hub: `/` · Config: `landing/lib/spokeConfig.ts` · PRD: `docs/prd-landing-spoke-design-system.md`

## Phase A primitives (shipped)

| Component | Path | Role |
|-----------|------|------|
| `SpokePageShell` | `components/spoke/SpokePageShell.tsx` | Glow + Navbar + ErrorBoundary |
| `SpokeHero` | `components/spoke/SpokeHero.tsx` | Hero unificado (garamond, chips, CTAs) |
| `SpokeHubLink` | `components/spoke/SpokeHubLink.tsx` | ← CLI Market |
| `SpokeFinalCTA` | `components/spoke/SpokeFinalCTA.tsx` | CTA final parametrizado por ICP |
| `SpokeStepsSection` | `components/spoke/SpokeStepsSection.tsx` | Pasos con círculos naranja (parametrizable) |
| `RetailersStatsStrip` | `components/retailers/RetailersStatsStrip.tsx` | Stats compactos retailers |
| `RetailersBenefitsSection` | `components/retailers/RetailersBenefitsSection.tsx` | Grid beneficios retailers |
| `SPOKE_CONFIG` | `lib/spokeConfig.ts` | Copy + brandMode por ICP |
| `SPOKE_FINAL_CTA` | `lib/spokeConfig.ts` | Copy CTA final por ICP |

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
      <Pricing spoke="build" />
      <FAQ />
      <SpokeFinalCTA icp="build" />
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

## Phase D (retailers — shipped)

- `SpokeStepsSection`, `RetailersStatsStrip`, `RetailersBenefitsSection`
- JSON-LD en `app/retailers/layout.tsx` via `RetailersJsonLd`
- `retailers/page.tsx` composición (~35 LOC)
- `ActiveBrandTicker` sin `ScrambleText`
