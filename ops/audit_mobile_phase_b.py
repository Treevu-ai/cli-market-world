#!/usr/bin/env python3
"""Phase B — interactive mobile checklist (320 + 375px)."""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://cli-market.dev"
OUT_DIR = ROOT / "audit" / f"mobile-phase-b-{date.today().isoformat()}"

VIEWPORTS = [
    ("320x568", 320, 568),
    ("375x812", 375, 812),
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


def touch_target_check(page, selector: str) -> dict:
    return page.evaluate(
        """(sel) => {
          const el = document.querySelector(sel);
          if (!el) return { missing: true };
          const r = el.getBoundingClientRect();
          return {
            width: Math.round(r.width),
            height: Math.round(r.height),
            ok: r.width >= 44 && r.height >= 44,
          };
        }""",
        selector,
    )


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


def dismiss_cookies(page) -> None:
    try:
        btn = page.get_by_role("button", name=re.compile(r"Entendido|Accept|Aceptar", re.I))
        if btn.count():
            btn.first.click(timeout=3000)
            page.wait_for_timeout(300)
    except Exception:
        pass


def add(findings: list, viewport: str, check: str, severity: str, **extra) -> None:
    findings.append({"viewport": viewport, "check": check, "severity": severity, **extra})


def run_story_dots(page, vp: str, vp_dir: Path, findings: list) -> None:
    page.evaluate("document.getElementById('story')?.scrollIntoView({block:'start'})")
    page.wait_for_timeout(1200)

    for i in range(4):
        dot = page.locator(".scroll-story-dot").nth(i)
        if not dot.count():
            add(findings, vp, f"story_dot_{i}", "S0", error="dot missing")
            continue
        dot.click()
        page.wait_for_timeout(700)
        ov = overflow_check(page)
        active = page.locator(".scroll-story-act-active").count()
        add(
            findings,
            vp,
            f"story_act_{i}_overflow",
            "S0" if ov["hasOverflow"] else "ok",
            activeActs=active,
            **ov,
        )
        page.screenshot(path=str(vp_dir / f"story-act-{i}.png"))

    tt = touch_target_check(page, ".scroll-story-dot")
    if tt.get("missing"):
        add(findings, vp, "story_dot_touch", "skip", missing=True)
    else:
        add(
            findings,
            vp,
            "story_dot_touch",
            "S2" if not tt.get("ok") else "ok",
            **tt,
        )


def run_story_scroll(page, vp: str, findings: list) -> None:
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60_000)
    dismiss_cookies(page)
    page.evaluate("document.getElementById('story')?.scrollIntoView({block:'start'})")
    page.wait_for_timeout(500)
    start_y = page.evaluate("() => window.scrollY")
    page.mouse.wheel(0, 900)
    page.wait_for_timeout(600)
    page.mouse.wheel(0, 900)
    page.wait_for_timeout(600)
    end_y = page.evaluate("() => window.scrollY")
    ov = overflow_check(page)
    add(
        findings,
        vp,
        "story_scroll_pin",
        "S1" if end_y <= start_y + 50 else "ok",
        startY=start_y,
        endY=end_y,
        **ov,
    )


def run_use_case_modal(page, vp: str, vp_dir: Path, findings: list) -> None:
    page.evaluate("document.getElementById('casos')?.scrollIntoView({block:'center'})")
    page.wait_for_timeout(600)
    card = page.locator("#casos button[aria-haspopup='dialog']").first
    if not card.count():
        add(findings, vp, "use_case_modal", "skip", missing=True)
        return
    card.click()
    page.wait_for_timeout(500)
    dialog = page.locator("[role='dialog'][aria-labelledby='use-case-demo-title']")
    visible = dialog.count() and dialog.is_visible()
    ov = overflow_check(page)
    add(
        findings,
        vp,
        "use_case_modal",
        "S0" if not visible else ("S0" if ov["hasOverflow"] else "ok"),
        dialogVisible=visible,
        **ov,
    )
    page.screenshot(path=str(vp_dir / "use-case-modal.png"))
    close_top_modal(page)


def run_free_signup_modal(page, vp: str, vp_dir: Path, findings: list) -> None:
    page.route("**/auth/register", lambda route: route.abort("failed"))
    page.evaluate("document.getElementById('pricing')?.scrollIntoView({block:'start'})")
    page.wait_for_timeout(800)
    build_tab = page.locator("#pricing-tab-build")
    if build_tab.count():
        build_tab.click()
        page.wait_for_timeout(400)
    free_btn = page.get_by_role("button", name=re.compile(r"Empezar gratis|Start free", re.I))
    if not free_btn.count():
        add(findings, vp, "free_signup_modal", "skip", missing=True)
        return
    free_btn.first.click()
    page.wait_for_timeout(800)
    dialog = page.locator("[role='dialog']").filter(has=page.get_by_text(re.compile(r"API|gratis|free", re.I)))
    visible = dialog.count() and dialog.first.is_visible()
    ov = overflow_check(page)
    add(
        findings,
        vp,
        "free_signup_modal",
        "S1" if not visible else ("S0" if ov["hasOverflow"] else "ok"),
        dialogVisible=visible,
        **ov,
    )
    page.screenshot(path=str(vp_dir / "free-signup-modal.png"))
    close_top_modal(page)
    page.unroute("**/auth/register")


def run_billing_modal(page, vp: str, vp_dir: Path, findings: list) -> None:
    page.evaluate("document.getElementById('pricing')?.scrollIntoView({block:'start'})")
    page.wait_for_timeout(600)
    pro_btn = page.locator("#pro-checkout button, #pro-checkout .btn-mint").first
    if not pro_btn.count():
        pro_btn = page.get_by_role("button", name=re.compile(r"Pro", re.I)).first
    if not pro_btn.count():
        add(findings, vp, "billing_modal", "skip", missing=True)
        return
    pro_btn.click()
    page.wait_for_timeout(700)
    dialog = page.locator("[role='dialog'][aria-modal='true']").last
    visible = dialog.count() and dialog.is_visible()
    ov = overflow_check(page)
    panel = page.evaluate(
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
    severity = "ok"
    if not visible:
        severity = "S1"
    elif ov["hasOverflow"]:
        severity = "S0"
    elif panel and not panel.get("fitsViewport"):
        severity = "S1"
    add(findings, vp, "billing_modal", severity, dialogVisible=visible, panel=panel, **ov)
    page.screenshot(path=str(vp_dir / "billing-modal.png"))
    close_top_modal(page)


def run_faq_expand(page, vp: str, vp_dir: Path, findings: list) -> None:
    page.evaluate("document.getElementById('faq')?.scrollIntoView({block:'start'})")
    page.wait_for_timeout(500)
    items = page.locator("#faq details summary")
    if items.count() < 2:
        add(findings, vp, "faq_expand", "skip", missing=True)
        return
    items.nth(1).click()
    page.wait_for_timeout(400)
    ov = overflow_check(page)
    add(findings, vp, "faq_expand", "S0" if ov["hasOverflow"] else "ok", **ov)
    page.screenshot(path=str(vp_dir / "faq-expanded.png"))


def run_reduced_motion(page, vp: str, findings: list) -> None:
    page.emulate_media(reduced_motion="reduce")
    page.goto(BASE_URL, wait_until="domcontentloaded", timeout=60_000)
    dismiss_cookies(page)
    page.wait_for_timeout(800)
    static = page.evaluate(
        """() => {
          const pin = document.querySelector('.scroll-story-pin');
          const stat = document.querySelector('.scroll-story-static');
          if (!pin || !stat) return { missing: true };
          const pinDisplay = getComputedStyle(pin).display;
          const statDisplay = getComputedStyle(stat).display;
          const acts = document.querySelectorAll('.scroll-story-static-act').length;
          return {
            pinHidden: pinDisplay === 'none',
            staticVisible: statDisplay !== 'none',
            staticActCount: acts,
          };
        }"""
    )
    ok = static.get("pinHidden") and static.get("staticVisible") and static.get("staticActCount", 0) >= 4
    add(findings, vp, "reduced_motion_story", "S1" if not ok else "ok", **static)
    page.emulate_media(reduced_motion="no-preference")


def run_viewport(page, name: str, width: int, height: int, findings: list) -> None:
    vp_dir = OUT_DIR / name
    vp_dir.mkdir(parents=True, exist_ok=True)

    page.set_viewport_size({"width": width, "height": height})
    page.goto(BASE_URL, wait_until="networkidle", timeout=90_000)
    dismiss_cookies(page)
    page.wait_for_timeout(1000)

    run_story_dots(page, name, vp_dir, findings)
    run_story_scroll(page, name, findings)
    run_use_case_modal(page, name, vp_dir, findings)
    run_free_signup_modal(page, name, vp_dir, findings)
    run_billing_modal(page, name, vp_dir, findings)
    run_faq_expand(page, name, vp_dir, findings)
    run_reduced_motion(page, name, findings)


def write_report(findings: list) -> int:
    issues = [f for f in findings if f.get("severity") not in ("ok", "skip")]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "phase": "B",
        "url": BASE_URL,
        "date": date.today().isoformat(),
        "viewports": [v[0] for v in VIEWPORTS],
        "issue_count": len(issues),
        "issues": issues,
        "findings": findings,
    }
    (OUT_DIR / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        f"# Mobile audit Phase B — {BASE_URL}",
        "",
        f"**Fecha:** {date.today().isoformat()}",
        f"**Issues:** {len(issues)}",
        "",
        "## Checklist",
        "- Scroll story dots (4 acts) + overflow",
        "- Scroll pin progression",
        "- Use case demo modal",
        "- Free signup modal (register fail)",
        "- Pro billing modal",
        "- FAQ expand",
        "- prefers-reduced-motion static story",
        "",
    ]
    for sev in ("S0", "S1", "S2"):
        items = [i for i in issues if i.get("severity") == sev]
        if items:
            lines.append(f"### {sev} ({len(items)})")
            for it in items:
                lines.append(f"- `{it.get('viewport')}` · **{it.get('check')}**: {it}")
            lines.append("")
    if not issues:
        lines.append("_Sin issues en checklist interactivo._")
    lines.extend(["", "## Artefactos", f"- `{OUT_DIR.relative_to(ROOT).as_posix()}/`"])
    (OUT_DIR / "report.md").write_text("\n".join(lines), encoding="utf-8")
    return 1 if any(i.get("severity") == "S0" for i in issues) else 0


def main() -> int:
    findings: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(locale="es-PE")
        page = context.new_page()
        for name, w, h in VIEWPORTS:
            print(f"-> Phase B {name} @ {BASE_URL}")
            try:
                run_viewport(page, name, w, h, findings)
            except Exception as exc:
                add(findings, name, "run_error", "S0", error=str(exc))
                print(f"  ERROR: {exc}", file=sys.stderr)
        browser.close()

    code = write_report(findings)
    issues = [f for f in findings if f.get("severity") not in ("ok", "skip")]
    print(f"Report: {OUT_DIR / 'report.md'}")
    print(f"Issues: {len(issues)}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
