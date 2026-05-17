const stores = [
  {
    name: "Wong",
    country: "Perú",
    svg: (
      <svg viewBox="0 0 120 40" width="100" height="33" aria-label="Wong">
        <rect width="120" height="40" rx="4" fill="#E31837" />
        <text x="60" y="26" textAnchor="middle" fontFamily="Space Grotesk, sans-serif" fontSize="20" fontWeight="700" fill="white" letterSpacing="4">WONG</text>
      </svg>
    ),
  },
  {
    name: "Metro",
    country: "Perú",
    svg: (
      <svg viewBox="0 0 120 40" width="100" height="33" aria-label="Metro">
        <rect width="120" height="40" rx="4" fill="#FF6B00" />
        <rect x="0" y="0" width="120" height="6" rx="4" fill="#003DA5" />
        <text x="60" y="26" textAnchor="middle" fontFamily="Space Grotesk, sans-serif" fontSize="18" fontWeight="700" fill="white" letterSpacing="3">metro</text>
        <rect x="0" y="34" width="120" height="6" rx="4" fill="#003DA5" />
      </svg>
    ),
  },
  {
    name: "Plaza Vea",
    country: "Perú",
    svg: (
      <svg viewBox="0 0 120 40" width="100" height="33" aria-label="Plaza Vea">
        <rect width="120" height="40" rx="4" fill="#DC0018" />
        <rect x="0" y="0" width="120" height="3" fill="#FFC72C" />
        <text x="60" y="24" textAnchor="middle" fontFamily="Space Grotesk, sans-serif" fontSize="15" fontWeight="700" fill="white" letterSpacing="2">Plaza Vea</text>
      </svg>
    ),
  },
  {
    name: "Carrefour",
    country: "Argentina / Brasil",
    svg: (
      <svg viewBox="0 0 120 40" width="100" height="33" aria-label="Carrefour">
        <rect width="120" height="40" rx="4" fill="#003E9E" />
        <polygon points="30,8 60,20 30,32" fill="#E2001A" />
        <polygon points="90,8 60,20 90,32" fill="white" />
        <text x="98" y="10" textAnchor="end" fontFamily="Space Grotesk, sans-serif" fontSize="11" fontWeight="700" fill="white" letterSpacing="1">Carrefour</text>
      </svg>
    ),
  },
  {
    name: "Jumbo",
    country: "Argentina",
    svg: (
      <svg viewBox="0 0 120 40" width="100" height="33" aria-label="Jumbo">
        <rect width="120" height="40" rx="4" fill="#007A33" />
        <ellipse cx="35" cy="18" rx="14" ry="12" fill="white" opacity="0.9" />
        <ellipse cx="35" cy="18" rx="8" ry="7" fill="#007A33" opacity="0.6" />
        <text x="65" y="24" textAnchor="middle" fontFamily="Space Grotesk, sans-serif" fontSize="18" fontWeight="700" fill="white" letterSpacing="2">JUMBO</text>
      </svg>
    ),
  },
  {
    name: "Chedraui",
    country: "México",
    svg: (
      <svg viewBox="0 0 120 40" width="100" height="33" aria-label="Chedraui">
        <rect width="120" height="40" rx="4" fill="#ED1C24" />
        <circle cx="28" cy="20" r="14" fill="white" />
        <text x="28" y="26" textAnchor="middle" fontFamily="serif" fontSize="20" fontWeight="900" fill="#ED1C24" fontStyle="italic">C</text>
        <text x="62" y="26" textAnchor="middle" fontFamily="Space Grotesk, sans-serif" fontSize="14" fontWeight="700" fill="white" letterSpacing="2">CHEDRAUI</text>
      </svg>
    ),
  },
  {
    name: "HEB",
    country: "México",
    svg: (
      <svg viewBox="0 0 120 40" width="100" height="33" aria-label="HEB">
        <rect width="120" height="40" rx="4" fill="#E31837" />
        <text x="60" y="28" textAnchor="middle" fontFamily="Space Grotesk, sans-serif" fontSize="24" fontWeight="900" fill="white" letterSpacing="3">H-E-B</text>
      </svg>
    ),
  },
  {
    name: "Olímpica",
    country: "Colombia",
    svg: (
      <svg viewBox="0 0 120 40" width="100" height="33" aria-label="Olímpica">
        <rect width="120" height="40" rx="4" fill="#003399" />
        <rect x="0" y="0" width="120" height="3" fill="#E31837" />
        <circle cx="30" cy="20" r="10" fill="none" stroke="white" strokeWidth="2" />
        <circle cx="30" cy="20" r="5" fill="#E31837" />
        <text x="58" y="25" textAnchor="middle" fontFamily="Space Grotesk, sans-serif" fontSize="15" fontWeight="700" fill="white" letterSpacing="1">Olímpica</text>
      </svg>
    ),
  },
  {
    name: "Open Food Facts",
    country: "Global · 3M+ productos",
    svg: (
      <svg viewBox="0 0 120 40" width="100" height="33" aria-label="Open Food Facts">
        <rect width="120" height="40" rx="4" fill="#2D9F4D" />
        <g transform="translate(16,8)">
          <rect x="0" y="4" width="6" height="16" rx="1" fill="white" />
          <rect x="10" y="4" width="6" height="16" rx="1" fill="white" />
          <rect x="20" y="4" width="6" height="16" rx="1" fill="white" />
          <circle cx="3" cy="2" r="3" fill="white" />
          <circle cx="13" cy="2" r="3" fill="white" />
          <circle cx="23" cy="2" r="3" fill="white" />
        </g>
        <text x="60" y="27" textAnchor="middle" fontFamily="Space Grotesk, sans-serif" fontSize="9" fontWeight="500" fill="white" letterSpacing="0.5">Open Food Facts</text>
      </svg>
    ),
  },
];

export default function Logos() {
  return (
    <section className="flex flex-col items-center w-full bg-[#0F0F0F] py-10 px-4 sm:py-[48px] sm:px-6 md:px-[120px] gap-6 sm:gap-[32px]">
      <span className="font-ibm-mono text-[10px] sm:text-[11px] text-[#444444] tracking-[2px] sm:tracking-[3px] text-center">
        17 COMERCIOS · 6 LÍNEAS · 5 PAÍSES · 1 API
      </span>

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4 sm:gap-6 md:gap-x-[40px] md:gap-y-[24px] w-full max-w-[1000px]">
        {stores.map((store) => (
          <div key={store.name} className="flex flex-col items-center gap-1.5 sm:gap-2 group">
            <div className="transition-all duration-300 group-hover:scale-105 group-hover:brightness-110 w-full max-w-[90px] sm:max-w-[100px] [&>svg]:w-full [&>svg]:h-auto">
              {store.svg}
            </div>
            <span className="font-ibm-mono text-[8px] sm:text-[9px] text-[#555555] tracking-[1px] text-center leading-tight">
              {store.country}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
