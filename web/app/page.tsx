import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Stats from "@/components/Stats";
import Features from "@/components/Features";
import HowToUse from "@/components/HowToUse";
import Commands from "@/components/Commands";
import FAQ from "@/components/FAQ";
import CTA from "@/components/CTA";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Stats />
        <Features />
        <HowToUse />
        <Commands />
        <FAQ />
        <CTA />
      </main>
      <Footer />
    </>
  );
}
