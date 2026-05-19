"""Scaffold Procure Copilot landing page"""
import os

base = "/home/acuba/Proyectos/procure-copilot"

# layout.tsx
with open(f"{base}/app/layout.tsx", "w") as f:
    f.write("""import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "Procure Copilot — Procurement inteligente para empresas",
  description: "Busca, compara y ahorra en compras empresariales. Sin WhatsApp. Sin Excel. IA para procurement en Latinoamerica.",
  openGraph: { title: "Procure Copilot — Procurement inteligente", description: "Busca, compara y ahorra." },
  twitter: { card: "summary_large_image", title: "Procure Copilot", description: "Procurement inteligente. Sin WhatsApp. Sin Excel." },
};
export default function Layout({ children }: { children: React.ReactNode }) {
  return <html lang="es"><body className="bg-[#0A0A0A] font-sans antialiased">{children}</body></html>;
}
""")

# page.tsx - Full landing
with open(f"{base}/app/page.tsx", "w") as f:
    f.write(r""""use client";
export default function Page() {
  return (
    <main className="min-h-screen bg-[#0A0A0A] text-white">
      {/* Grid BG */}
      <div className="fixed inset-0 opacity-[0.03] pointer-events-none" style={{backgroundImage:"linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)",backgroundSize:"64px 64px"}} />
      
      {/* Hero */}
      <section className="relative flex flex-col items-center justify-center min-h-[90vh] px-6 gap-6 text-center">
        <span className="text-[#00FF88] font-mono text-xs tracking-widest uppercase border border-[#00FF88]/20 px-3 py-1">Beta · Latam</span>
        <h1 className="max-w-[700px] text-[clamp(2rem,6vw,5rem)] font-bold leading-[1.02]">
          <span className="text-white">Tus compras empresariales.</span><br/>
          <span className="text-[#00FF88]">Sin WhatsApp. Sin Excel.</span>
        </h1>
        <p className="max-w-[500px] text-[#888] text-sm leading-relaxed">
          Procure Copilot busca, compara y encuentra los mejores precios entre tus proveedores. 
          En segundos. Sin llamadas. Sin cadenas de mensajes.
        </p>
        <a href="#cta" className="inline-flex items-center gap-2 bg-[#00FF88] text-black font-bold px-6 py-3 text-sm hover:bg-[#00cc66] transition-colors">
          Quiero ahorrar en mis compras →
        </a>
        <div className="flex gap-6 mt-4 text-[#555] text-xs font-mono">
          <span>☕ Restaurantes</span>
          <span>🏗 Constructoras</span>
          <span>💊 Farmacias</span>
          <span>🏨 Hoteles</span>
        </div>
      </section>

      {/* How It Works */}
      <section id="how" className="relative flex flex-col items-center py-20 px-6 gap-12">
        <span className="text-[#00FF88]/60 font-mono text-xs tracking-widest uppercase">Cómo funciona</span>
        <h2 className="text-[clamp(1.5rem,3vw,2.5rem)] font-bold text-center leading-[1.1]">
          Del caos al ahorro.<br/>En 3 pasos.
        </h2>
        <div className="flex flex-wrap justify-center gap-6 max-w-[900px]">
          {[
            {n:"01",t:"Conectá tus proveedores",d:"Subí tu lista de proveedores o conectá tus canales de compra. Una vez. Sin integraciones complejas."},
            {n:"02",t:"El agente busca y compara",d:"Cada vez que necesitás comprar, Procure Copilot consulta precios, disponibilidad y tiempos de entrega entre todos tus proveedores."},
            {n:"03",t:"Aprobá y ahorrá",d:"Recibís la mejor opción. Un clic para aprobar. El ahorro queda registrado. Sin WhatsApp. Sin Excel. Sin errores."},
          ].map((s,i)=>(
            <div key={i} className="bg-[#0F0F0F] border border-[#1A1A1A] p-6 w-[280px] flex flex-col gap-3">
              <span className="text-2xl font-bold text-white/10">{s.n}</span>
              <h3 className="font-bold text-white">{s.t}</h3>
              <p className="text-[#666] text-xs leading-relaxed">{s.d}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Value */}
      <section className="relative flex flex-col items-center py-20 px-6 gap-8 bg-[#060606]">
        <span className="text-[#00FF88]/60 font-mono text-xs tracking-widest uppercase">Lo que ganás</span>
        <div className="flex flex-wrap justify-center gap-6 max-w-[900px]">
          {[
            {v:"30-40%",l:"Ahorro promedio en compras"},
            {v:"85%",l:"Menos tiempo en procurement"},
            {v:"0",l:"Errores por pedidos manuales"},
            {v:"24/7",l:"Búsqueda automática de precios"},
          ].map((m,i)=>(
            <div key={i} className="text-center w-[180px] flex flex-col gap-2">
              <span className="text-[#00FF88] text-3xl font-bold">{m.v}</span>
              <span className="text-[#555] text-xs">{m.l}</span>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section id="cta" className="relative flex flex-col items-center py-20 px-6 gap-6 text-center">
        <h2 className="text-[clamp(1.5rem,3vw,2rem)] font-bold">¿Querés saber cuánto podrías ahorrar?</h2>
        <p className="text-[#888] text-sm max-w-[400px]">Agendá una demo de 15 minutos. Te mostramos cuánto ahorrás con datos reales de tus proveedores.</p>
        <a href="mailto:hello@cli-market.dev?subject=Demo%20Procure%20Copilot" className="inline-flex items-center gap-2 bg-[#00FF88] text-black font-bold px-8 py-4 hover:bg-[#00cc66] transition-colors">
          Agendar demo gratuita →
        </a>
        <p className="text-[#444] text-[10px] font-mono">Sin compromiso. 15 minutos. Datos reales.</p>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-[#1A1A1A] text-center">
        <p className="text-[#444] text-[10px] font-mono">Procure Copilot · 2026 · Powered by CLI Market infrastructure</p>
      </footer>
    </main>
  );
}
""")

print("Scaffolded Procure Copilot landing")
