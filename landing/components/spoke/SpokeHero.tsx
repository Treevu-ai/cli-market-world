"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useLang } from "@/lib/LanguageContext";
import HeroBackground from "@/components/HeroBackground";
import { SPOKE_CONFIG, type SpokeIcp } from "@/lib/spokeConfig";

type SpokeHeroProps = {
  icp: SpokeIcp;
  /** Override primary CTA click (e.g. open modal on retailers). */
  onPrimaryClick?: () => void;
};

export default function SpokeHero({ icp, onPrimaryClick }: SpokeHeroProps) {
  const { lang } = useLang();
  const isES = lang === "es";
  const config = SPOKE_CONFIG[icp];
  const hero = config.hero;
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const primaryLabel = isES ? hero.primaryCta.es : hero.primaryCta.en;
  const secondary = hero.secondaryCta;
  const secondaryLabel = secondary ? (isES ? secondary.es : secondary.en) : null;

  const primaryClass = "btn-mint";
  const primaryProps = onPrimaryClick
    ? { type: "button" as const, onClick: onPrimaryClick }
    : hero.primaryCta.external
      ? { href: hero.primaryCta.href, target: "_blank" as const, rel: "noopener noreferrer" }
      : { href: hero.primaryCta.href };

  return (
    <section
      id="hero"
      className="landing-section animate-fade-in relative overflow-hidden scroll-mt-24"
      style={{ borderBottom: "1px solid var(--cm-hairline-soft)" }}
    >
      <HeroBackground dense={config.heroBackgroundDense} />
      <div className="landing-container-wide hero-inner pt-4 pb-8 sm:pt-6 sm:pb-10 lg:py-8 relative z-10">
        <div className="max-w-3xl text-left">
          <motion.span
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="inline-flex mb-4 stripe-tag-soft"
          >
            {isES ? hero.eyebrow_es : hero.eyebrow_en}
          </motion.span>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="hero-garamond-headline text-balance"
          >
            <span className="text-[var(--cm-on-surface)]">
              {isES ? hero.titleBefore_es : hero.titleBefore_en}
            </span>
            <span className="text-gradient-orange">
              {isES ? hero.titleAccent_es : hero.titleAccent_en}
            </span>
            {(isES ? hero.titleAfter_es : hero.titleAfter_en) ? (
              <span className="text-[var(--cm-on-surface)]">
                {isES ? hero.titleAfter_es : hero.titleAfter_en}
              </span>
            ) : null}
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
            className="mt-4 text-base sm:text-lg max-w-[540px] leading-relaxed text-[var(--cm-on-surface-variant)]"
          >
            {isES ? hero.subhead_es : hero.subhead_en}
          </motion.p>

          {mounted && hero.chips.length > 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.16 }}
              className="mt-4 flex flex-wrap justify-start gap-2"
            >
              {hero.chips.map((chip) => (
                <span
                  key={isES ? chip.label_es : chip.label_en}
                  className="text-xs font-mono text-[var(--cm-on-surface-variant)] bg-[var(--cm-surface-high)] border border-[var(--cm-outline-variant)] rounded-full px-3 py-1"
                >
                  {isES ? chip.label_es : chip.label_en}
                </span>
              ))}
            </motion.div>
          ) : null}

          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.22 }}
            className="flex flex-wrap justify-start gap-3 mt-6"
          >
            {onPrimaryClick ? (
              <button type="button" className={primaryClass} onClick={onPrimaryClick}>
                {primaryLabel}
              </button>
            ) : (
              <a className={primaryClass} {...primaryProps}>
                {primaryLabel}
              </a>
            )}
            {secondary && secondaryLabel ? (
              <a
                href={secondary.href}
                className="btn-outline"
                {...(secondary.external
                  ? { target: "_blank", rel: "noopener noreferrer" }
                  : {})}
              >
                {secondaryLabel}
              </a>
            ) : null}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
