const comandosLinks = ["MARKET SEARCH", "MARKET COMPARE", "MARKET ADD", "MARKET CART", "MARKET CHECKOUT", "MARKET ASK"];
const recursosLinks = ["GITHUB", "DOCS", "MCP SERVER"];
const tiendasLinks = ["WONG", "METRO", "PLAZA VEA", "CARREFOUR", "JUMBO", "CHEDRAUI", "HEB", "OLÍMPICA"];

export default function Footer() {
  return (
    <footer className="flex flex-col w-full bg-[#050505] safe-bottom">
      <div className="flex flex-col md:flex-row gap-8 sm:gap-10 md:gap-[80px] px-4 sm:px-6 md:px-[120px] py-8 sm:py-10 md:py-[64px]">
        {/* Brand */}
        <div className="flex flex-col gap-5 sm:gap-6 md:w-[280px] md:shrink-0">
          <div className="flex items-center gap-[10px] sm:gap-[12px]">
            <span className="font-grotesk text-[14px] sm:text-[16px] font-bold text-[#00FF88] tracking-[2px] sm:tracking-[3px]">
              <span className="text-[#F5F5F0]">$ </span>MARKET
            </span>
          </div>
          <p className="font-ibm-mono text-[10px] sm:text-[11px] text-[#888888] tracking-[0.5px] sm:tracking-[1px] leading-[1.5] sm:leading-[1.6] max-w-[260px]">
            INFRAESTRUCTURA QUE CONVIERTE SUPERMERCADOS DE LATAM EN APIs PARA AGENTES DE INTELIGENCIA ARTIFICIAL.
          </p>
          <div className="flex gap-[10px] sm:gap-[12px]">
            {[{ label: "GH" }, { label: "MCP" }, { label: "API" }].map((s) => (
              <a
                key={s.label}
                href="https://github.com/Treevu-ai/cli-market-latam"
                className="flex items-center justify-center w-[40px] h-[40px] sm:w-[36px] sm:h-[36px] bg-[#111111] border border-[#2D2D2D] hover:border-[#888888] transition-colors"
              >
                <span className="font-grotesk text-[10px] font-bold text-[#AAAAAA]">
                  {s.label}
                </span>
              </a>
            ))}
          </div>
        </div>

        {/* Link columns */}
        <div className="grid grid-cols-3 md:flex md:flex-1 gap-6 sm:gap-8 md:gap-[80px]">
          {[
            { heading: "COMANDOS", links: comandosLinks },
            { heading: "TIENDAS",  links: tiendasLinks   },
            { heading: "RECURSOS", links: recursosLinks  },
          ].map((col) => (
            <div key={col.heading} className="flex flex-col gap-4 md:gap-[20px]">
              <span className="font-grotesk text-[11px] font-bold text-[#F5F5F0] tracking-[2px]">
                {col.heading}
              </span>
              {col.links.map((link) => (
                <a
                  key={link}
                  href="#"
                  className="font-ibm-mono text-[11px] sm:text-[12px] text-[#888888] tracking-[0.5px] sm:tracking-[1px] hover:text-[#CCCCCC] transition-colors py-1"
                >
                  {link}
                </a>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Bottom bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between w-full px-4 sm:px-6 md:px-[120px] py-4 md:h-[56px] border-t border-t-[#1D1D1D] gap-3 sm:gap-0">
        <span className="font-ibm-mono text-[10px] sm:text-[11px] text-[#666666] tracking-[0.5px] sm:tracking-[1px]">
          © 2025 CLI MARKET LATAM · TREEVU AI. TODOS LOS DERECHOS RESERVADOS.
        </span>
        <div className="flex items-center gap-4 sm:gap-6 md:gap-[32px]">
          <a href="#" className="font-ibm-mono text-[10px] sm:text-[11px] text-[#666666] tracking-[0.5px] sm:tracking-[1px] hover:text-[#AAAAAA] transition-colors">
            PRIVACIDAD
          </a>
          <a href="#" className="font-ibm-mono text-[10px] sm:text-[11px] text-[#666666] tracking-[0.5px] sm:tracking-[1px] hover:text-[#AAAAAA] transition-colors">
            TÉRMINOS
          </a>
          <span className="font-ibm-mono text-[10px] sm:text-[11px] font-bold text-[#00FF88] tracking-[0.5px] sm:tracking-[1px]">
            V1.0
          </span>
        </div>
      </div>
    </footer>
  );
}
