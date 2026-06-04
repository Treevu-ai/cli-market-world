"use client";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function LegalPage({
  title,
  updated,
  children,
}: {
  title: string;
  updated: string;
  children: React.ReactNode;
}) {
  return (
    <main className="relative min-h-screen bg-[var(--cm-background)]">
      <div className="grid-bg fixed inset-0 opacity-40 pointer-events-none" aria-hidden="true" />
      <Navbar />
      <div className="relative z-10 pt-24 pb-20">
        <div className="max-w-2xl mx-auto px-6">
          <p className="section-eyebrow mb-3 text-[var(--cm-mint)]">CLI Market</p>
          <h1 className="text-3xl font-black text-white mb-2">{title}</h1>
          <p className="text-xs text-[var(--cm-on-surface-variant)]/60 mb-10">
            Última actualización / Last updated: {updated}
          </p>
          <div className="prose-legal">{children}</div>
        </div>
      </div>
      <Footer />
    </main>
  );
}
