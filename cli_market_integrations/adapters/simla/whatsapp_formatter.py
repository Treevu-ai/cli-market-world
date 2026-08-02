"""WhatsApp formatter — verbatim from simla-cli-market-prototype."""
from typing import Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

EMOJIS = {"search":"🔍","compare":"📊","optimize":"🛒","history":"📈","alert":"🔔","error":"❌","success":"✅","info":"ℹ️","price":"💰","store":"🏪","savings":"💵","warning":"⚠️"}


def _fmt_price(p) -> str:
    try: return f"{p:,.2f}"
    except: return str(p)

def _fmt_date(s: str) -> str:
    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"]:
        try: return datetime.strptime(s, fmt).strftime("%d/%m/%Y")
        except: pass
    return s

def _bold(t: str) -> str: return f"*{t}*"


class WhatsAppFormatter:
    def format_search_result(self, r: Dict) -> str:
        if r.get("error"): return self.format_api_error(r["error"], "buscar ese producto")
        prods = r.get("products", [])
        if not prods: return f"{EMOJIS['error']} No encontré ese producto en los retailers peruanos."
        p = prods[0]
        msg = f"{EMOJIS['search']} *{_bold(p.get('name','Producto'))}*\n\n{EMOJIS['price']} Mejor precio: S/ {_fmt_price(p.get('price',0))}\n{EMOJIS['store']} En: {_bold(p.get('store','Tienda'))}\n"
        if p.get("last_updated"): msg += f"📅 Actualizado: {_fmt_date(p['last_updated'])}\n"
        if len(prods) > 1: msg += f"\n_{len(prods)-1} opciones más disponibles_\n¿Quieres que compare con otras tiendas?"
        return msg

    def format_compare_result(self, r: Dict) -> str:
        if r.get("error"): return self.format_api_error(r["error"], "comparar precios")
        comps = r.get("comparisons", [])
        if not comps: return f"{EMOJIS['error']} No encontré precios para comparar."
        msg = f"{EMOJIS['compare']} *Comparación de precios:*\n\n"
        for i, c in enumerate(comps[:5], 1): msg += f"{i}. {EMOJIS['store']} {c.get('store','Tienda')}: S/ {_fmt_price(c.get('price',0))}\n"
        if r.get("best_price"):
            b = r["best_price"]; msg += f"\n{EMOJIS['success']} *Mejor opción:* {b.get('store','Tienda')}\n{EMOJIS['price']} S/ {_fmt_price(b.get('price',0))}\n"
            if len(comps) > 1:
                exp = max(comps, key=lambda x: x.get("price",0)); sav = exp.get("price",0)-b.get("price",0)
                if sav > 0: msg += f"{EMOJIS['savings']} Ahorro: S/ {_fmt_price(sav)}\n"
        return msg

    def format_optimize_result(self, r: Dict) -> str:
        if r.get("error"): return self.format_api_error(r["error"], "optimizar tu canasta")
        recs = r.get("recommendations", [])
        if not recs: return f"{EMOJIS['error']} No pude optimizar tu canasta."
        msg = f"{EMOJIS['optimize']} *Optimización de canasta:*\n\n"
        for rec in recs:
            msg += f"• {_bold(rec.get('product','Producto'))}\n  {EMOJIS['price']} S/ {_fmt_price(rec.get('optimized_price',0))} en {rec.get('store','Tienda')}\n"
            if rec.get("savings",0) > 0: msg += f"  {EMOJIS['savings']} Ahorro: S/ {_fmt_price(rec['savings'])}\n"
        if r.get("total_savings"): msg += f"\n{EMOJIS['savings']} *Ahorro total: S/ {_fmt_price(r['total_savings'])}*\n"
        if r.get("recommended_store"): msg += f"\n{EMOJIS['store']} *Mejor opción: {r['recommended_store']}*\n"
        return msg

    def format_history_result(self, r: Dict) -> str:
        if r.get("error"): return self.format_api_error(r["error"], "obtener el historial de precios")
        hist = r.get("history", [])
        if not hist: return f"{EMOJIS['error']} No hay historial disponible para este producto."
        msg = f"{EMOJIS['history']} *Historial de precios:*\n\n"
        for i, e in enumerate(hist[:5], 1): msg += f"{i}. {_fmt_date(e.get('date','?'))}: S/ {_fmt_price(e.get('price',0))} ({e.get('store','Tienda')})\n"
        if len(hist) >= 2:
            fp, lp = hist[-1].get("price",0), hist[0].get("price",0)
            if lp > fp: msg += f"\n📈 Subió: S/ {_fmt_price(lp-fp)} en el período"
            elif lp < fp: msg += f"\n📉 Bajó: S/ {_fmt_price(fp-lp)} en el período"
            else: msg += "\n➡️ Estable en el período"
        return msg

    def format_alert_confirmation(self, product: str, threshold: float) -> str:
        return f"{EMOJIS['alert']} *Alerta configurada:*\n\nProducto: {_bold(product)}\nTe avisaré cuando el precio baje de S/ {_fmt_price(threshold)}\n\n{EMOJIS['info']} Te notificaré por este chat cuando haya cambios."

    def format_error(self, message: str) -> str:
        return f"{EMOJIS['error']} {message}"

    def format_api_error(self, code: str, action: str = "completar la consulta") -> str:
        c = (code or "").lower()
        if "429" in c or "too many" in c or "rate" in c:
            return f"{EMOJIS['warning']} Demasiadas consultas en poco tiempo. Esperá un minuto e intentá de nuevo."
        if "403" in c or "401" in c:
            return f"{EMOJIS['error']} No tengo permiso para {action} (canasta exige Pro+)."
        if "timeout" in c:
            return f"{EMOJIS['warning']} La consulta tardó demasiado. Intentá de nuevo en unos segundos."
        return self.format_error(f"No pude {action}. Intentá con otro nombre o más tarde.")


whatsapp_formatter = WhatsAppFormatter()
