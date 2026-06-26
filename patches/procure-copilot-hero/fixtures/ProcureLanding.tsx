"use client";

import { motion } from "framer-motion";

export default function ProcureLanding() {
  return (
    <>
      <section id="hero" className="landing-section relative z-10 animate-fade-in">
        <div className="proc-container-wide pt-10 pb-6 sm:pt-14 sm:pb-10">
          <h1>Hero</h1>
        </div>
      </section>
      <section id="segments" className="landing-section landing-section-alt relative z-10">
        <div className="landing-section-header text-center">Segments</div>
      </section>
    </>
  );
}
