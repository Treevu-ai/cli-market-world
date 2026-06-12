#!/usr/bin/env python3
"""Mobile audit for all landing pages (overflow + key interactions)."""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "https://cli-market.dev"

OUT_DIR = ROOT / "audit" / f"mobile-pages-{date.today().isoformat()}"

VIEWPORTS = [
    ("320x568", 320, 568),
    ("375x812", 375, 812),
]

PAGES = [
    {"slug": "impact", "path": "/impact"},
    {"slug": "retailers", "path": "/retailers", "modal": "retailer_apply"},
    {"slug": "account", "path": "/account"},
    {"slug": "docs", "path": "/docs"},
    {"slug": "stats", "path": "/stats"},
    {"slug": "scanner", "path": "/scanner"},
    {"slug": "tools", "path": "/tools"},
    {"slug": "legal-privacy", "path": "/legal/privacy"},
    {"slug": "legal-tos", "path": "/legal/tos"},
    {"slug": "legal-dla", "path": "/legal/dla"},
]


def overflow_check(page) -> dict:
    return page.evaluate(
        """() => {
          const doc = document.documentElement;
          const scrollW = Math.max(doc.scrollWidth, document.body?.scrollWidth || 0);
          const clientW = doc.clientWidth;
          return {
            scrollWidth: scrollW,
            clientWidth: clientW,
            overflowPx: Math.max(0, scrollW - clientW),
            hasOverflow: scrollW > clientW + 1,
          };
        }"""
    )


def panel_fits_viewport(page) -> dict | None:
    return page.evaluate(
        """() => {
          const dialogs = [...document.querySelectorAll('[role="dialog"][aria-modal="true"]')]
            .filter((d) => d.getBoundingClientRect().height > 0);
          const d = dialogs.at(-1);
          if (!d) return null;
          const p = d.querySelector('.landing-modal-panel');
          if (!p) return null;
          const r = p.getBoundingClientRect();
          const vh = window.innerHeight;
          return {
            top: Math.round(r.top),
            bottom: Math.round(r.bottom),
            fitsViewport: r.top >= -2 && r.bottom <= vh + 2,
          };
        }"""
    )


def dismiss_cookies(page) -> None:
    try:
        btn = page.get_by_role("button", name=re.compile(r"Entendido|Accept|Aceptar", re.I))
        if btn.count():
            btn.first.click(timeout=3000)
            page.wait_for_timeout(300)
    except Exception:
        pass


def close_top_modal(page) -> None:
    try:
        page.keyboard.press("Escape")
        page.wait_for_timeout(350)
    except Exception:
        pass
    dialog = page.locator('[role="dialog"][aria-modal="true"]').last
    if dialog.count() and dialog.is_visible():
        close_btn = dialog.get_by_role("button", name=re.compile(r"^Cerrar$|^Close$", re.I))
        if close_btn.count():
            close_btn.first.click(timeout=3000)
            page.wait_for_timeout(300)


def add(findings: list, **row) -> None:
    findings.append(row)


def check_mobile_nav(page, vp: str, vp_dir: Path, slug: str, findings: list) -> None:
    menu_btn = page.locator('nav button[aria-label="Menú"], nav button[aria-label="Menu"]')
    if not menu_btn.count():
        add(findings, viewport=vp, page=slug, check="mobile_menu", severity="skip", missing=True)
        return
    menu_btn.first.click()
    page.wait_for_timeout(400)
    ov = overflow_check(page)
    add(
        findings,
        viewport=vp,
        page=slug,
        check="mobile_menu_overflow",
        severity="S0" if ov["hasOverflow"] else "ok",
        **ov,
    )
    cookie = page.locator('[data-cookie-banner="true"]')
    cookie_visible = cookie.count() > 0 and cookie.is_visible()
    add(
        findings,
        viewport=vp,
        page=slug,
        check="cookie_hidden_when_menu_open",
        severity="S1" if cookie_visible else "ok",
        cookieVisible=cookie_visible,
    )
    page.screenshot(path=str(vp_dir / f"{slug}-menu.png"))
    menu_btn.first.click()


def check_retailer_modal(page, vp: str, vp_dir: Path, slug: str, findings: list) -> None:
    btn = page.get_by_role("button", name=re.compile(r"Listar|Apply|Integrar|Solicitar|gratis|free", re.I))
    if not btn.count():
        btn = page.locator("button.btn-mint").first
    if not btn.count():
        add(findings, viewport=vp, page=slug, check="retailer_apply_modal", severity="skip", missing=True)
        return
    btn.first.click()
    page.wait_for_timeout(600)
    ov = overflow_check(page)
    panel = panel_fits_viewport(page)
    visible = page.locator('[role="dialog"][aria-modal="true"]').last.is_visible()
    severity = "ok"
    if not visible:
        severity = "S1"
    elif ov["hasOverflow"]:
        severity = "S0"
    elif panel and not panel.get("fitsViewport"):
        severity = "S1"
    add(
        findings,
        viewport=vp,
        page=slug,
        check="retailer_apply_modal",
        severity=severity,
        dialogVisible=visible,
        panel=panel,
        **ov,
    )
    page.screenshot(path=str(vp_dir / f"{slug}-modal.png"))
    close_top_modal(page)


def audit_page(page, vp: str, width: int, height: int, spec: dict, findings: list) -> None:
    slug = spec["slug"]
    path = spec["path"]
    url = f"{BASE_URL}{path}"

    vp_dir = OUT_DIR / vp
    vp_dir.mkdir(parents=True, exist_ok=True)

    page.set_viewport_size({"width": width, "height": height})
    page.goto(url, wait_until="networkidle", timeout=90_000)
    page.wait_for_timeout(1200)
    dismiss_cookies(page)

    ov = overflow_check(page)
    add(
        findings,
        viewport=vp,
        page=slug,
        check="page_overflow",
        severity="S0" if ov["hasOverflow"] else "ok",
        url=url,
        **ov,
    )
    if ov["hasOverflow"]:
        page.screenshot(path=str(vp_dir / f"{slug}-overflow.png"))

    page.screenshot(path=str(vp_dir / f"{slug}-full.png"), full_page=True)

    if width < 768:
        check_mobile_nav(page, vp, vp_dir, slug, findings)

    if spec.get("modal") == "retailer_apply":
        check_retailer_modal(page, vp, vp_dir, slug, findings)


def write_report(findings: list) -> int:
    issues = [f for f in findings if f.get("severity") not in ("ok", "skip")]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "base_url": BASE_URL,
        "date": date.today().isoformat(),
        "pages": [p["slug"] for p in PAGES],
        "viewports": [v[0] for v in VIEWPORTS],
        "issue_count": len(issues),
        "issues": issues,
        "findings": findings,
    }
    (OUT_DIR / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Mobile audit — all pages",
        "",
        f"**Base:** {BASE_URL}",
        f"**Fecha:** {date.today().isoformat()}",
        f"**Issues:** {len(issues)}",
        "",
    ]
    by_page: dict[str, list] = {}
    for issue in issues:
        by_page.setdefault(issue.get("page", "?"), []).append(issue)

    for slug, items in sorted(by_page.items()):
        lines.append(f"## `{slug}`")
        for it in items:
            lines.append(f"- `{it.get('viewport')}` · **{it.get('check')}** ({it.get('severity')}): {it}")
        lines.append("")

    if not issues:
        lines.append("_Sin issues en páginas secundarias._")

    lines.extend(["", "## Artefactos", f"- `{OUT_DIR.relative_to(ROOT).as_posix()}/`"])
    (OUT_DIR / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return 1 if any(i.get("severity") == "S0" for i in issues) else 0


def main() -> int:
    findings: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale="es-PE")
        page = context.new_page()

        for vp_name, w, h in VIEWPORTS:
            for spec in PAGES:
                print(f"-> {vp_name} {spec['path']}")
                try:
                    audit_page(page, vp_name, w, h, spec, findings)
                except Exception as exc:
                    add(
                        findings,
                        viewport=vp_name,
                        page=spec["slug"],
                        check="run_error",
                        severity="S0",
                        error=str(exc),
                    )
                    print(f"  ERROR: {exc}", file=sys.stderr)

        browser.close()

    code = write_report(findings)
    issues = [f for f in findings if f.get("severity") not in ("ok", "skip")]
    print(f"Report: {OUT_DIR / 'report.md'}")
    print(f"Issues: {len(issues)}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
