/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from "react";
import Header from "./components/Header";
import Hero from "./components/Hero";
import PainSection from "./components/PainSection";
import SecretSauce from "./components/SecretSauce";
import Solutions from "./components/Solutions";
import ConversationalBridge from "./components/ConversationalBridge";
import Pricing from "./components/Pricing";
import Footer from "./components/Footer";
import { RoleTabId } from "./types";

export default function App() {
  const [activeRole, setActiveRole] = useState<RoleTabId>("revenue");

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans" id="app-root">
      {/* Header with active role selection callback */}
      <Header onSelectRole={setActiveRole} />
      
      {/* Main content flow */}
      <main className="flex-grow">
        {/* 1. Hero Section (with dynamic WhatsApp conversation mockup) */}
        <Hero />

        {/* 2. The "Pain" Section (agitate and educate) */}
        <PainSection />

        {/* 3. The "Secret Sauce" (Data Moat with SKU Entity resolver simulator) */}
        <SecretSauce />

        {/* 4. Soluciones por Rol (Matrix of value bento tabs) */}
        <Solutions activeRole={activeRole} setActiveRole={setActiveRole} />

        {/* 5. El Puente Conversacional (WhatsApp Live Sandbox Playground) */}
        <ConversationalBridge />

        {/* 6. Pricing Plan Matrix (Scale from Validation to Enterprise) */}
        <Pricing />
      </main>

      {/* 7. Footer & Final CTA (Terminal code card invitation) */}
      <Footer />
    </div>
  );
}

