import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import AccountDashboard from "@/components/AccountDashboard";

export const metadata = {
  title: "Account — CLI Market",
  description: "View your CLI Market tier, API usage, and upgrade path.",
};

export default function AccountPage() {
  return (
    <main className="relative min-h-screen bg-[var(--cm-background)]">
      <div className="grid-bg fixed inset-0 opacity-40 pointer-events-none" aria-hidden="true" />
      <Navbar />
      <div className="relative z-10 pt-20">
        <AccountDashboard />
        <Footer />
      </div>
    </main>
  );
}