import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import PixelDivider from "@/components/PixelDivider";
import Lines from "@/components/Lines";
import Features from "@/components/Features";
import FAQ from "@/components/FAQ";
import Pricing from "@/components/Pricing";
import FinalCTA from "@/components/FinalCTA";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="flex flex-col w-full bg-[#0A0A0A] pt-[60px]">
      <Navbar />
      <Hero />
      <PixelDivider />
      <Lines />
      <Features />
      <PixelDivider />
      <Pricing />
      <FAQ />
      <FinalCTA />
      <Footer />
    </main>
  );
}
