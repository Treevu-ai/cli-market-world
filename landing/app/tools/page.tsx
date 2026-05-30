import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import ToolsPage from "@/components/ToolsPage";

export default function ToolsRoute() {
  return (
    <main className="relative min-h-screen bg-[var(--cm-background)]">
      <div className="grid-bg fixed inset-0 opacity-40 pointer-events-none" aria-hidden="true" />
      <Navbar />
      <div className="relative z-10">
        <ToolsPage />
        <Footer />
      </div>
    </main>
  );
}
