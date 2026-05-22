"use client";
export function AnimatedSphere() {
  return (
    <div className="relative w-full h-full">
      <div className="absolute inset-0 rounded-full animate-[spin_30s_linear_infinite] opacity-20"
        style={{background:"radial-gradient(circle at 30% 30%, rgba(0,255,136,0.15) 0%, transparent 50%), radial-gradient(circle at 70% 60%, rgba(255,214,0,0.1) 0%, transparent 40%), radial-gradient(circle at 50% 50%, rgba(96,165,250,0.08) 0%, transparent 60%)"}}/>
      <div className="absolute inset-0 rounded-full animate-[spin_25s_linear_infinite_reverse] opacity-15"
        style={{background:"radial-gradient(circle at 60% 40%, rgba(0,255,136,0.1) 0%, transparent 45%), radial-gradient(circle at 40% 70%, rgba(255,107,53,0.08) 0%, transparent 40%)"}}/>
    </div>
  );
}
export function NoiseOverlay() {
  return <div className="fixed inset-0 z-[1] pointer-events-none opacity-[0.015]" style={{backgroundImage:"url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",backgroundSize:"256px 256px"}}/>;
}
