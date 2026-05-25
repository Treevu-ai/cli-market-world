import { useLang } from "@/lib/LanguageContext";

export default function UseCases() {
  const { t } = useLang();
  const cases = [
    { tKey: "case_agents", titleKey: "case_agents_title", descKey: "case_agents_desc", icon: "🤖" },
    { tKey: "case_fintech", titleKey: "case_fintech_title", descKey: "case_fintech_desc", icon: "📊" },
    { tKey: "case_ecom", titleKey: "case_ecom_title", descKey: "case_ecom_desc", icon: "🛒" },
    { tKey: "case_devs", titleKey: "case_devs_title", descKey: "case_devs_desc", icon: "💻" },
  ];
  return (
    <section id="usecases" className="relative flex flex-col w-full bg-black py-16 px-6 lg:px-12 md:py-[80px] gap-8">
      <div className="flex flex-col gap-3 max-w-[600px]">
        <span className="inline-flex items-center gap-3 text-sm font-mono text-white/40"><span className="w-8 h-px bg-[#3cffd0]/40"/>{t("usecases_label")}</span>
        <h2 className="text-[clamp(1.5rem,3vw,3rem)] font-grotesk font-bold text-white leading-[1.05]">{t("usecases_title")}</h2>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-[900px]">
        {cases.map((c) => (
          <div key={c.tKey} className="bg-[#131313] border border-[#2d2d2d] p-6 flex flex-col gap-4">
            <span className="text-2xl">{c.icon}</span>
            <h3 className="font-grotesk text-base font-bold text-white">{t(c.titleKey)}</h3>
            <p className="text-[#888] text-sm font-sans leading-relaxed">{t(c.descKey)}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
