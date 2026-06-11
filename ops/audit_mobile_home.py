#!/usr/bin/env python3
"""Mobile-first audit for cli-market.dev home (Phase A — read-only)."""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://cli-market.dev"
OUT_DIR = ROOT / "audit" / f"mobile-{date.today().isoformat()}"

VIEWPORTS = [
    ("320x568", 320, 568),
    ("375x812", 375, 812),
    ("390x844", 390, 844),
    ("768x1024", 768, 1024),
    ("1280x800", 1280, 800),
]

SECTIONS = [
    "hero",
    "story",
    "hero-playground-mobile",
    "casos",
    "coverage",
    "how",
    "api",
    "intelligence",
    "pricing",
    "faq",
    "contact",
    "about",
]


def overflow_check(page) -> dict:
    return page.evaluate(
        """() => {
          const doc = document.documentElement;
          const body = document.body;
          const scrollW = Math.max(doc.scrollWidth, body?.scrollWidth || 0);
          const clientW = doc.clientWidth;
          return {
            scrollWidth: scrollW,
            clientWidth: clientW,
            overflowPx: Math.max(0, scrollW - clientW),
            hasOverflow: scrollW > clientW + 1,
          };
        }"""
    )


def section_overflow(page, section_id: str) -> dict | None:
    return page.evaluate(
        """(id) => {
          const el = document.getElementById(id);
          if (!el) return null;
          const r = el.getBoundingClientRect();
          const vw = document.documentElement.clientWidth;
          return {
            id,
            left: Math.round(r.left),
            right: Math.round(r.right),
            width: Math.round(r.width),
            overflowsLeft: r.left < -1,
            overflowsRight: r.right > vw + 1,
            overflowPx: Math.max(0, r.right - vw, -r.left),
          };
        }""",
        section_id,
    )


def dismiss_cookies(page) -> None:
    try:
        btn = page.get_by_role("button", name=re.compile(r"Aceptar|Accept|Entendido", re.I))
        if btn.count() > 0:
            btn.first.click(timeout=3000)
            page.wait_for_timeout(400)
    except Exception:
        pass


def run_viewport(page, name: str, width: int, height: int, findings: list) -> None:
    page.set_viewport_size({"width": width, "height": height})
    page.goto(BASE_URL, wait_until="networkidle", timeout=90_000)
    page.wait_for_timeout(1500)
    dismiss_cookies(page)

    vp_dir = OUT_DIR / name
    vp_dir.mkdir(parents=True, exist_ok=True)

    global_ov = overflow_check(page)
    findings.append(
        {
            "viewport": name,
            "check": "page_overflow",
            "severity": "S0" if global_ov["hasOverflow"] else "ok",
            **global_ov,
        }
    )

    for sid in SECTIONS:
        page.evaluate(f"document.getElementById('{sid}')?.scrollIntoView({{block:'start'}})")
        page.wait_for_timeout(600)
        so = section_overflow(page, sid)
        if so is None:
            findings.append({"viewport": name, "check": f"section_{sid}", "severity": "skip", "missing": True})
            continue
        bad = so["overflowsLeft"] or so["overflowsRight"]
        findings.append(
            {
                "viewport": name,
                "check": f"section_{sid}",
                "severity": "S0" if bad else "ok",
                **so,
            }
        )
        if bad:
            page.screenshot(path=str(vp_dir / f"overflow-{sid}.png"))

    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60_000)
    dismiss_cookies(page)
    page.wait_for_timeout(800)
    page.screenshot(path=str(vp_dir / "full-page.png"), full_page=True)

    if width < 768:
        menu_btn = page.locator('nav button[aria-label="Menú"], nav button[aria-label="Menu"]')
        if menu_btn.count():
            menu_btn.first.click()
            page.wait_for_timeout(500)
            menu_ov = overflow_check(page)
            findings.append(
                {
                    "viewport": name,
                    "check": "mobile_menu_open",
                    "severity": "S1" if menu_ov["hasOverflow"] else "ok",
                    **menu_ov,
                }
            )
            cookie_banner = page.locator('[data-cookie-banner="true"]')
            cookie_visible = cookie_banner.count() > 0 and cookie_banner.is_visible()
            findings.append(
                {
                    "viewport": name,
                    "check": "cookie_hidden_when_menu_open",
                    "severity": "S1" if cookie_visible else "ok",
                    "cookieVisible": cookie_visible,
                }
            )
            page.screenshot(path=str(vp_dir / "mobile-menu-open.png"))
            menu_btn.first.click()

        paths_btn = page.get_by_role("button", name=re.compile(r"Intelligence|Retailers", re.I))
        if paths_btn.count():
            paths_btn.first.click()
            page.wait_for_timeout(400)
            findings.append(
                {
                    "viewport": name,
                    "check": "hero_paths_expanded",
                    "severity": "ok",
                    "expanded": True,
                }
            )
            page.screenshot(path=str(vp_dir / "hero-paths-expanded.png"))

    page.evaluate("document.getElementById('pricing')?.scrollIntoView({block:'start'})")
    page.wait_for_timeout(800)
    procure_tab = page.locator("#pricing-tab-procure")
    if procure_tab.count():
        procure_tab.click()
        page.wait_for_timeout(600)
        po = overflow_check(page)
        findings.append(
            {
                "viewport": name,
                "check": "pricing_procure_tab",
                "severity": "S0" if po["hasOverflow"] else "ok",
                **po,
            }
        )
        page.screenshot(path=str(vp_dir / "pricing-procure.png"))


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    findings: list[dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale="es-PE")
        page = context.new_page()

        for name, w, h in VIEWPORTS:
            print(f"-> {name} @ {BASE_URL}")
            try:
                run_viewport(page, name, w, h, findings)
            except Exception as exc:
                findings.append({"viewport": name, "check": "run_error", "severity": "S0", "error": str(exc)})
                print(f"  ERROR: {exc}", file=sys.stderr)

        browser.close()

    issues = [f for f in findings if f.get("severity") not in ("ok", "skip")]
    report = {
        "url": BASE_URL,
        "date": date.today().isoformat(),
        "viewports": [v[0] for v in VIEWPORTS],
        "issue_count": len(issues),
        "issues": issues,
        "findings": findings,
    }
    report_path = OUT_DIR / "report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = [
        f"# Mobile audit — {BASE_URL}",
        f"",
        f"**Fecha:** {date.today().isoformat()}",
        f"**Issues:** {len(issues)}",
        f"",
        "## Resumen por severidad",
        f"",
    ]
    for sev in ("S0", "S1", "S2"):
        items = [i for i in issues if i.get("severity") == sev]
        if items:
            md_lines.append(f"### {sev} ({len(items)})")
            for it in items:
                md_lines.append(f"- `{it.get('viewport')}` · {it.get('check')}: {it}")
            md_lines.append("")

    if not issues:
        md_lines.append("_Sin overflow horizontal detectado en viewports probados._")

    md_lines.extend(["", "## Artefactos", f"- `{OUT_DIR.relative_to(ROOT).as_posix()}/`"])
    (OUT_DIR / "report.md").write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Report: {report_path}")
    print(f"Issues: {len(issues)}")
    return 1 if any(i.get("severity") == "S0" for i in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
