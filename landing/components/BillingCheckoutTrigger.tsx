"use client";

import { useState } from "react";
import { useLang } from "@/lib/LanguageContext";
import BillingCheckoutModal, { type BillingCheckoutKind } from "@/components/BillingCheckoutModal";

export default function BillingCheckoutTrigger({
  kind,
  className = "btn-mint w-full",
  label_es,
  label_en,
  id,
}: {
  kind: BillingCheckoutKind;
  className?: string;
  label_es?: string;
  label_en?: string;
  id?: string;
}) {
  const { lang } = useLang();
  const isES = lang === "es";
  const [open, setOpen] = useState(false);

  const defaultLabel =
    kind.type === "build-starter"
      ? isES
        ? "Suscribir Starter →"
        : "Subscribe Starter →"
      : kind.type === "build-pro-founding"
        ? isES
          ? "Pro Founding $29 →"
          : "Pro Founding $29 →"
        : kind.type === "build-pro"
          ? isES
            ? "Configurar Pro →"
            : "Set up Pro →"
          : isES
            ? "Suscribir →"
            : "Subscribe →";

  const label = isES ? label_es ?? defaultLabel : label_en ?? defaultLabel;

  return (
    <>
      <button type="button" id={id} className={className} onClick={() => setOpen(true)}>
        {label}
      </button>
      <BillingCheckoutModal open={open} onClose={() => setOpen(false)} kind={kind} />
    </>
  );
}