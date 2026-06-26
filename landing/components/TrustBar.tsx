"use client";

import { useLang } from "@/lib/LanguageContext";

function LogoClaude() {
  return (
    <svg height="18" viewBox="0 0 24 24" fill="currentColor" aria-label="Claude" role="img">
      <path d="M13.82 3.52h3.6L24 20h-3.6l-1.42-3.95H9.02L7.6 20H4l6.17-16.48h3.65zm-.95 9.83 2.12-5.79 2.12 5.79h-4.24z" />
    </svg>
  );
}

function LogoOpenAI() {
  return (
    <svg height="18" viewBox="0 0 24 24" fill="currentColor" aria-label="ChatGPT" role="img">
      <path d="M22.28 10.19a6.01 6.01 0 0 0-.52-4.93 6.08 6.08 0 0 0-6.56-2.92 6.08 6.08 0 0 0-4.31-1.59 6.08 6.08 0 0 0-5.8 4.21 6.08 6.08 0 0 0-4.05 2.94 6.08 6.08 0 0 0 .75 7.12 6.01 6.01 0 0 0 .52 4.93 6.08 6.08 0 0 0 6.56 2.91 6.08 6.08 0 0 0 4.31 1.6 6.08 6.08 0 0 0 5.8-4.21 6.08 6.08 0 0 0 4.05-2.94 6.08 6.08 0 0 0-.75-7.12zm-9.28 13.06a4.5 4.5 0 0 1-2.89-1.04l.14-.08 4.8-2.77a.79.79 0 0 0 .4-.69V11.9l2.03 1.17a.07.07 0 0 1 .04.06v5.6a4.51 4.51 0 0 1-4.52 4.52zm-9.7-4.14a4.5 4.5 0 0 1-.54-3.02l.14.08 4.8 2.77a.79.79 0 0 0 .79 0l5.86-3.38v2.34a.08.08 0 0 1-.03.06L9.3 20.73a4.51 4.51 0 0 1-6.01-1.62zm-1.26-10.46A4.5 4.5 0 0 1 4.39 6.68v5.72a.79.79 0 0 0 .4.69l5.85 3.38-2.03 1.17a.08.08 0 0 1-.07 0L3.21 14.1a4.51 4.51 0 0 1-.17-5.45zm16.65 3.87-5.85-3.38 2.03-1.17a.08.08 0 0 1 .07 0l5.29 3.05a4.51 4.51 0 0 1-.7 8.14v-5.72a.79.79 0 0 0-.84-.92zm2.02-3.04-.14-.08-4.8-2.77a.79.79 0 0 0-.79 0L8.93 10.8V8.46a.08.08 0 0 1 .03-.06l5.28-3.05a4.51 4.51 0 0 1 6.27 4.67zm-12.7 4.17-2.03-1.17a.08.08 0 0 1-.04-.06V7.62a4.51 4.51 0 0 1 7.4-3.46l-.14.08-4.8 2.77a.79.79 0 0 0-.4.69l.01 6.65zm1.1-2.37 2.61-1.5 2.61 1.5v3l-2.61 1.5-2.61-1.5v-3z" />
    </svg>
  );
}

function LogoCursor() {
  return (
    <svg height="18" viewBox="0 0 24 24" fill="currentColor" aria-label="Cursor" role="img">
      <path d="M13.27 22.31 4 4l18.31 9.27-8.54 1.5-0.5 7.54z" />
      <path d="M4 4l9.27 18.31.5-7.54 7.54-.5z" fillOpacity=".35" />
    </svg>
  );
}

function LogoLangChain() {
  return (
    <svg height="18" viewBox="0 0 24 24" fill="currentColor" aria-label="LangChain" role="img">
      <path d="M15 4a5 5 0 0 1 0 10h-2a5 5 0 0 1 0-10h2zm0 2h-2a3 3 0 0 0 0 6h2a3 3 0 0 0 0-6zM9 10a5 5 0 0 1 0 10H7a5 5 0 0 1 0-10h2zm0 2H7a3 3 0 0 0 0 6h2a3 3 0 0 0 0-6z" />
    </svg>
  );
}

function LogoVercel() {
  return (
    <svg height="16" viewBox="0 0 24 24" fill="currentColor" aria-label="Vercel AI" role="img">
      <path d="M24 22.525H0L12 1.475z" />
    </svg>
  );
}

function LogoHuggingFace() {
  return (
    <svg height="18" viewBox="0 0 24 24" fill="currentColor" aria-label="Hugging Face" role="img">
      <path d="M12 2a10 10 0 1 0 0 20A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 0-16 8 8 0 0 1 0 16zm-3-9a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm6 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm-5.5 3.5c.69.69 1.62 1 2.5 1s1.81-.31 2.5-1a.5.5 0 0 0-.71-.71c-.49.49-1.13.71-1.79.71s-1.3-.22-1.79-.71a.5.5 0 0 0-.71.71z" />
    </svg>
  );
}

function LogoMistral() {
  return (
    <svg height="16" viewBox="0 0 24 24" fill="currentColor" aria-label="Mistral" role="img">
      <rect x="0" y="0" width="6" height="6" />
      <rect x="9" y="0" width="6" height="6" />
      <rect x="18" y="0" width="6" height="6" />
      <rect x="9" y="9" width="6" height="6" />
      <rect x="18" y="9" width="6" height="6" />
      <rect x="18" y="18" width="6" height="6" />
    </svg>
  );
}

function LogoGemini() {
  return (
    <svg height="18" viewBox="0 0 24 24" fill="currentColor" aria-label="Gemini" role="img">
      <path d="M12 2C12 2 9.33 8.67 2 12c7.33 3.33 10 10 10 10s2.67-6.67 10-10C14.67 8.67 12 2 12 2z" />
    </svg>
  );
}

function LogoGitHubCopilot() {
  return (
    <svg height="18" viewBox="0 0 24 24" fill="currentColor" aria-label="GitHub Copilot" role="img">
      <path d="M9.75 14.5a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0zm9 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0zM12 2C6.477 2 2 6.477 2 12c0 2.304.82 4.418 2.176 6.075.386-1.378 1.608-2.325 3.074-2.325.876 0 1.676.347 2.25.91V16a2.5 2.5 0 0 0 5 0v-.34c.574-.563 1.374-.91 2.25-.91 1.466 0 2.688.947 3.074 2.325A9.955 9.955 0 0 0 22 12c0-5.523-4.477-10-10-10z" />
    </svg>
  );
}

const TOOLS = [
  { name: "Claude", icon: <LogoClaude /> },
  { name: "ChatGPT", icon: <LogoOpenAI /> },
  { name: "Cursor", icon: <LogoCursor /> },
  { name: "LangChain", icon: <LogoLangChain /> },
  { name: "Vercel AI", icon: <LogoVercel /> },
  { name: "Hugging Face", icon: <LogoHuggingFace /> },
  { name: "Mistral", icon: <LogoMistral /> },
  { name: "Gemini", icon: <LogoGemini /> },
  { name: "GitHub Copilot", icon: <LogoGitHubCopilot /> },
];

export default function TrustBar() {
  const { lang } = useLang();
  const isES = lang === "es";
  const items = [...TOOLS, ...TOOLS];

  return (
    <div className="border-b border-[var(--cm-hairline-soft)] bg-[var(--cm-surface-low)]">
      <div
        className="w-full py-4 overflow-hidden"
        aria-label={isES ? "Herramientas compatibles" : "Compatible tools"}
      >
        <div className="flex items-center gap-6">
          <span className="text-[11px] font-mono uppercase tracking-widest text-[var(--cm-text-secondary)] shrink-0 pl-6 whitespace-nowrap">
            {isES ? "Integra con" : "Integrates with"}
          </span>
          <div className="overflow-hidden flex-1 min-w-0 mask-fade-x">
            <div className="trust-marquee-track flex items-center gap-10 w-max">
              {items.map((tool, i) => (
                <div
                  key={`${tool.name}-${i}`}
                  className="flex items-center gap-2 text-[var(--cm-text-secondary)] hover:text-[var(--cm-mint)] transition-colors cursor-default select-none shrink-0"
                >
                  {tool.icon}
                  <span className="text-sm font-semibold whitespace-nowrap">{tool.name}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
