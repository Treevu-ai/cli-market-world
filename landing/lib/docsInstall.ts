import { MARKET_STATS } from "@/lib/marketStats";

export type PrereqLevel = "cli" | "session" | "paid" | "mcp";

const PY = "3.11+";

export function prereqSteps(level: PrereqLevel, isES: boolean): string[] {
  const pip = MARKET_STATS.pipInstallCmd;
  const ver = MARKET_STATS.packageVersion;

  switch (level) {
    case "cli":
      return isES
        ? [
            `# Python ${PY}`,
            pip,
            `market --version   # esperado: cli-market-world ${ver}`,
          ]
        : [
            `# Python ${PY}`,
            pip,
            `market --version   # expected: cli-market-world ${ver}`,
          ];
    case "session":
      return isES
        ? [
            `# Python ${PY}`,
            pip,
            "market init        # cuenta free + readiness %",
            "# o: market register && market login",
          ]
        : [
            `# Python ${PY}`,
            pip,
            "market init        # free account + readiness %",
            "# or: market register && market login",
          ];
    case "paid":
      return isES
        ? [
            `# Python ${PY}`,
            pip,
            "market register    # sk-... (guárdela)",
            "market upgrade --plan starter   # o pro | pro_founding",
          ]
        : [
            `# Python ${PY}`,
            pip,
            "market register    # sk-... (save it now)",
            "market upgrade --plan starter   # or pro | pro_founding",
          ];
    case "mcp":
      return isES
        ? [
            `# Python ${PY}`,
            pip,
            "market init",
            "market mcp-setup --ide cursor   # cursor | claude | windsurf | vscode",
          ]
        : [
            `# Python ${PY}`,
            pip,
            "market init",
            "market mcp-setup --ide cursor   # cursor | claude | windsurf | vscode",
          ];
  }
}

export function prereqLabel(isES: boolean): string {
  return isES ? "Requisitos previos" : "Prerequisites";
}
