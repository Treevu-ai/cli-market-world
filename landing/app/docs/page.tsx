import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import DocsPage from "@/components/DocsPage";

export default function DocsRoute() {
  return (
    <main className="relative min-h-screen bg-[var(--cm-background)]">
      <div className="grid-bg fixed inset-0 opacity-40 pointer-events-none" aria-hidden="true" />
      <Navbar />
      <div className="relative z-10">
        <DocsPage />
        <Footer />
      </div>
    </main>
  );
}
