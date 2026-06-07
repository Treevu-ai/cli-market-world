"use client";

import { useLang } from "@/lib/LanguageContext";

type Props = {
  checked: boolean;
  onChange: (checked: boolean) => void;
  className?: string;
  includeSubscriptions?: boolean;
};

export default function LegalConsentCheckbox({
  checked,
  onChange,
  className = "",
  includeSubscriptions = false,
}: Props) {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <label className={`flex items-start gap-3 cursor-pointer select-none ${className}`}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-0.5 accent-[var(--cm-mint)] shrink-0"
      />
      <span className="text-xs text-[var(--cm-on-surface-variant)] leading-relaxed">
        {isES ? (
          <>
            Acepto los{" "}
            <a
              href="/legal/tos"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--cm-mint)] hover:underline"
            >
              Términos de Servicio
            </a>
            {includeSubscriptions ? " (incl. suscripciones)" : ""} y la{" "}
            <a
              href="/legal/privacy"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--cm-mint)] hover:underline"
            >
              Política de Privacidad
            </a>
            . Autorizo el tratamiento de mis datos para responder esta solicitud.
          </>
        ) : (
          <>
            I agree to the{" "}
            <a
              href="/legal/tos"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--cm-mint)] hover:underline"
            >
              Terms of Service
            </a>
            {includeSubscriptions ? " (incl. subscriptions)" : ""} and{" "}
            <a
              href="/legal/privacy"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--cm-mint)] hover:underline"
            >
              Privacy Policy
            </a>
            . I authorize processing of my data to respond to this request.
          </>
        )}
      </span>
    </label>
  );
}