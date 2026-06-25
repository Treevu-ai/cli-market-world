"use client";
import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { useLang } from "@/lib/LanguageContext";

type TocItem = { id: string; label: string };

export default function LegalPage({
  titleES,
  titleEN,
  updatedES,
  updatedEN,
  children,
}: {
  titleES: string;
  titleEN: string;
  updatedES: string;
  updatedEN: string;
  children: (isES: boolean) => React.ReactNode;
}) {
  const { lang } = useLang();
  const isES = lang === "es";
  const [toc, setToc] = useState<TocItem[]>([]);

  useEffect(() => {
    const root = document.querySelector(".prose-legal");
    if (!root) return;
    const items: TocItem[] = [];
    root.querySelectorAll("h2").forEach((heading, index) => {
      if (!heading.id) {
        heading.id = `section-${index + 1}`;
      }
      items.push({ id: heading.id, label: heading.textContent?.trim() ?? `§${index + 1}` });
    });
    setToc(items);
  }, [isES]);

  return (
    <main className="relative min-h-screen bg-[#09090B]">
      <Navbar />
      <div className="relative z-10 pt-24 pb-20">
        <div className="max-w-5xl mx-auto px-6">
          <p className="section-eyebrow mb-3 text-[var(--cm-mint)]">CLI Market</p>
          <h1 className="text-3xl font-black text-[#FAFAFA] mb-2">
            {isES ? titleES : titleEN}
          </h1>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/60 mb-10">
            {isES ? `Última actualización: ${updatedES}` : `Last updated: ${updatedEN}`}
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,11rem)_1fr] gap-10 lg:gap-14">
            {toc.length > 0 && (
              <aside className="lg:sticky lg:top-24 lg:self-start">
                <p className="font-label-caps text-[10px] text-[var(--cm-on-surface-variant)]/50 mb-4 tracking-widest">
                  {isES ? "Contenido" : "Contents"}
                </p>
                <nav aria-label={isES ? "Tabla de contenidos" : "Table of contents"}>
                  <ul className="space-y-2 text-sm">
                    {toc.map((item) => (
                      <li key={item.id}>
                        <a
                          href={`#${item.id}`}
                          className="text-[var(--cm-on-surface-variant)] hover:text-[var(--cm-mint)] transition-colors leading-snug block"
                        >
                          {item.label}
                        </a>
                      </li>
                    ))}
                  </ul>
                </nav>
              </aside>
            )}
            <div className="prose-legal min-w-0">{children(isES)}</div>
          </div>
        </div>
      </div>
      <Footer />
    </main>
  );
}
