import type { ReactNode } from "react";

type HeroPathCardVariant = "primary" | "signal" | "default";

type HeroPathCardProps = {
  href: string;
  eyebrow: string;
  title: string;
  body: ReactNode;
  foot: string;
  variant?: HeroPathCardVariant;
  onClick?: () => void;
};

const variantClass: Record<HeroPathCardVariant, string> = {
  primary:
    "btn-action hero-terminal-cta-primary shadow-[0_0_24px_rgba(200,255,0,0.15)]",
  signal: "hero-terminal-card ring-1 ring-[var(--cm-signal)]/25",
  default: "hero-terminal-card",
};

const eyebrowClass: Record<HeroPathCardVariant, string> = {
  primary: "text-[var(--cm-on-mint)]/70",
  signal: "text-[var(--cm-signal)]/80",
  default: "text-[var(--cm-text-secondary)]",
};

const footClass: Record<HeroPathCardVariant, string> = {
  primary: "text-[var(--cm-on-mint)]/60",
  signal: "text-[var(--cm-text-secondary)]",
  default: "text-[var(--cm-text-secondary)]",
};

export default function HeroPathCard({
  href,
  eyebrow,
  title,
  body,
  foot,
  variant = "default",
  onClick,
}: HeroPathCardProps) {
  return (
    <a
      href={href}
      onClick={onClick}
      className={`hero-path-card group hover:scale-[1.02] transition-all duration-200 ${variantClass[variant]}`}
    >
      <span className={`hero-path-card__eyebrow ${eyebrowClass[variant]}`}>{eyebrow}</span>
      <span
        className={`hero-path-card__title ${
          variant === "primary" ? "text-[var(--cm-on-mint)]" : "text-[var(--cm-ink)]"
        }`}
      >
        {title}
      </span>
      <div className="hero-path-card__body">{body}</div>
      <span className={`hero-path-card__foot ${footClass[variant]}`}>{foot}</span>
    </a>
  );
}
