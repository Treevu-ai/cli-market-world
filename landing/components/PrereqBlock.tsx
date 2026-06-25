import { prereqLabel, prereqSteps, type PrereqLevel } from "@/lib/docsInstall";

function CodeBlock({ children }: { children: string }) {
  return (
    <div className="code-block-cyber p-4">
      <pre className="code-snippet text-[var(--cm-mint)]/90 whitespace-pre-wrap">{children}</pre>
    </div>
  );
}

export default function PrereqBlock({
  level,
  isES,
  compact,
}: {
  level: PrereqLevel;
  isES: boolean;
  compact?: boolean;
}) {
  if (compact) {
    return (
      <p className="text-xs text-[var(--cm-on-surface-variant)]/70 mb-6">
        {isES ? "Requisitos previos: ver " : "Prerequisites: see "}
        <a href="#quickstart" className="text-[var(--cm-mint)] underline hover:no-underline">
          Quickstart
        </a>
        .
      </p>
    );
  }
  return (
    <div className="mb-6 rounded-lg border border-[var(--cm-outline-variant)]/30 bg-[var(--cm-surface-low)]/30 px-4 py-3 text-left">
      <p className="font-label-caps text-[10px] text-[var(--cm-mint)]/80 mb-2 tracking-widest">{prereqLabel(isES)}</p>
      <CodeBlock>{prereqSteps(level, isES).join("\n")}</CodeBlock>
    </div>
  );
}
