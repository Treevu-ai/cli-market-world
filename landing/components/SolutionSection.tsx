"use client";
import { useLang } from "@/lib/LanguageContext";

export default function SolutionSection() {
  const { lang } = useLang();
  const isES = lang === "es";

  return (
    <section id="solution" className="landing-section animate-fade-in scroll-mt-24" style={{ backgroundColor: "#111113" }}>
      <div className="landing-container-wide">
        <div className="landing-section-header text-center">
          <p className="section-eyebrow mb-4">{isES ? "SOLUCIÓN" : "SOLUTION"}</p>
          <h2 className="section-title text-[var(--cm-on-surface)]">
            {isES
              ? "Una capa programable desde el descubrimiento hasta la ejecución"
              : "One programmable layer from discovery to execution"}
          </h2>
          <p className="section-intro">
            {isES
              ? "CLI Market convierte la infraestructura retail fragmentada en primitivos de comercio limpios para agentes. Busca productos, compara precios, arma canastas y ejecuta flujos de compra empresarial a través de una sola interfaz."
              : "CLI Market converts fragmented retail infrastructure into clean commerce primitives for agents. Search products, compare prices, build baskets, and execute procurement workflows through one interface."}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
          <div className="card-cyber rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="w-7 h-7 rounded-full bg-[var(--cm-mint)] text-[#09090B] text-xs font-bold flex items-center justify-center shrink-0">
                1
              </span>
              <h3 className="text-base font-semibold text-[var(--cm-on-surface)]">
                {isES ? "Buscar" : "Search"}
              </h3>
            </div>
            <div
              className="rounded-lg p-4 font-mono text-xs leading-relaxed"
              style={{ background: "#0d1117", color: "#e6edf3" }}
            >
              <span style={{ color: "#79c0ff" }}>results</span>{" "}
              <span style={{ color: "#ff7b72" }}>=</span>{" "}
              <span style={{ color: "#d2a8ff" }}>cli_market</span>
              <span style={{ color: "#e6edf3" }}>.</span>
              <span style={{ color: "#79c0ff" }}>compare</span>
              <span style={{ color: "#e6edf3" }}>(</span>
              <span style={{ color: "#a5d6ff" }}>&quot;rice&quot;</span>
              <span style={{ color: "#e6edf3" }}>, </span>
              <span style={{ color: "#79c0ff" }}>country</span>
              <span style={{ color: "#ff7b72" }}>=</span>
              <span style={{ color: "#a5d6ff" }}>&quot;PE&quot;</span>
              <span style={{ color: "#e6edf3" }}>)</span>
            </div>
          </div>

          <div className="card-cyber rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="w-7 h-7 rounded-full bg-[var(--cm-mint)] text-[#09090B] text-xs font-bold flex items-center justify-center shrink-0">
                2
              </span>
              <h3 className="text-base font-semibold text-[var(--cm-on-surface)]">
                {isES ? "Comparar" : "Compare"}
              </h3>
            </div>
            <div
              className="rounded-lg p-4 font-mono text-xs leading-relaxed space-y-1"
              style={{ background: "#0d1117", color: "#8b949e" }}
            >
              <div>
                <span style={{ color: "#3fb950" }}>Metro PE</span>
                <span style={{ color: "#e6edf3" }}> → S/ 2.90 /kg</span>
              </div>
              <div>
                <span style={{ color: "#8b949e" }}>Plaza Vea</span>
                <span style={{ color: "#e6edf3" }}> → S/ 3.05 /kg</span>
              </div>
              <div>
                <span style={{ color: "#8b949e" }}>Wong PE</span>
                <span style={{ color: "#e6edf3" }}> → S/ 3.10 /kg</span>
              </div>
            </div>
          </div>

          <div className="card-cyber rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-4">
              <span className="w-7 h-7 rounded-full bg-[var(--cm-mint)] text-[#09090B] text-xs font-bold flex items-center justify-center shrink-0">
                3
              </span>
              <h3 className="text-base font-semibold text-[var(--cm-on-surface)]">
                {isES ? "Ejecutar" : "Execute"}
              </h3>
            </div>
            <div
              className="rounded-lg p-4 font-mono text-xs leading-relaxed"
              style={{ background: "#0d1117", color: "#e6edf3" }}
            >
              <span style={{ color: "#79c0ff" }}>basket</span>{" "}
              <span style={{ color: "#ff7b72" }}>=</span>{" "}
              <span style={{ color: "#d2a8ff" }}>cli_market</span>
              <span style={{ color: "#e6edf3" }}>.</span>
              <span style={{ color: "#79c0ff" }}>basket</span>
              <span style={{ color: "#e6edf3" }}>(</span>
              <br />
              <span style={{ color: "#e6edf3" }}>{"  "}</span>
              <span style={{ color: "#79c0ff" }}>items</span>
              <span style={{ color: "#ff7b72" }}>=</span>
              <span style={{ color: "#e6edf3" }}>[</span>
              <span style={{ color: "#a5d6ff" }}>&quot;rice:1kg&quot;</span>
              <span style={{ color: "#e6edf3" }}>, </span>
              <span style={{ color: "#a5d6ff" }}>&quot;milk:1L&quot;</span>
              <span style={{ color: "#e6edf3" }}>]</span>
              <br />
              <span style={{ color: "#e6edf3" }}>)</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
