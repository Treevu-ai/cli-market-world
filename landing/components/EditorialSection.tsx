import type { ReactNode } from "react";

type EditorialSectionProps = {
  id: string;
  eyebrow: string;
  children: ReactNode;
  variant?: "default" | "muted";
};

export function EditorialSection({
  id,
  eyebrow,
  children,
  variant = "default",
}: EditorialSectionProps) {
  return (
    <section
      id={id}
      className={`landing-editorial-section${variant === "muted" ? " landing-editorial-section--muted" : ""}`}
    >
      <div className="landing-container-wide">
        <header className="landing-editorial-header">
          <p className="landing-editorial-eyebrow">{eyebrow}</p>
          <div className="landing-editorial-rule" aria-hidden="true" />
        </header>
        {children}
      </div>
    </section>
  );
}

export function EditorialRule({ className = "" }: { className?: string }) {
  return <div className={`landing-editorial-rule ${className}`.trim()} aria-hidden="true" />;
}