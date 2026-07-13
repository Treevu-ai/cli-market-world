"use client";

import { useState } from "react";
import { API_URL } from "@/lib/api";

const PAGO_METHODS = [
  { value: "Yape", label: "Yape" },
  { value: "Transferencia bancaria", label: "Transferencia bancaria" },
];

export default function AcademyRegisterForm() {
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [telefono, setTelefono] = useState("");
  const [pago, setPago] = useState("Yape");
  const [comentario, setComentario] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [registered, setRegistered] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/v1/taller/registro`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nombre, email, telefono, pago, comentario }),
      });
      const data = await res.json();
      if (!res.ok) {
        const detail = typeof data.detail === "string" ? data.detail : "No se pudo registrar tu cupo.";
        throw new Error(detail);
      }
      setRegistered(true);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Error";
      setError(`${msg} Intenta de nuevo o escríbenos por WhatsApp al +51 902 126 765.`);
    } finally {
      setLoading(false);
    }
  };

  if (registered) {
    return (
      <div className="card-cyber p-8 max-w-[520px] mx-auto text-center">
        <p className="text-lg font-semibold text-[var(--cm-on-surface)] mb-2">Registro confirmado</p>
        <p className="text-sm text-[var(--cm-on-surface-variant)] leading-relaxed">
          Te enviamos los datos de pago a tu correo. Envía tu comprobante por WhatsApp al{" "}
          <strong className="text-[var(--cm-on-surface)]">+51 902 126 765</strong> para asegurar tu cupo.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="card-cyber p-6 md:p-8 max-w-[520px] mx-auto space-y-4 text-left">
      <div>
        <h3 className="text-lg font-semibold text-[var(--cm-on-surface)] text-center">Reserva tu lugar</h3>
        <p className="text-xs text-[var(--cm-on-surface-variant)] text-center mt-2 leading-relaxed">
          Taller · Inteligencia de Mercados · CLI Market
        </p>
      </div>

      <div>
        <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">Nombre completo</label>
        <input
          required
          value={nombre}
          onChange={(e) => setNombre(e.target.value)}
          className="input-cyber"
          placeholder="Tu nombre y apellido"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">Correo electrónico</label>
          <input
            required
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input-cyber"
            placeholder="tu@correo.com"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">WhatsApp</label>
          <input
            required
            type="tel"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            className="input-cyber"
            placeholder="9xx xxx xxx"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">Método de pago preferido</label>
        <select value={pago} onChange={(e) => setPago(e.target.value)} className="input-cyber">
          {PAGO_METHODS.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-xs font-medium text-[var(--cm-on-surface-variant)] mb-1">
          Comentario (opcional)
        </label>
        <textarea
          value={comentario}
          onChange={(e) => setComentario(e.target.value)}
          className="input-cyber min-h-[80px]"
          placeholder="Categoría de tu negocio, dudas puntuales, etc."
        />
      </div>

      {/* Other forms in this codebase use #ffb4ab for errors, tuned for the
          old dark theme — illegible on this card's white background, so a
          properly contrasting red is used here instead. */}
      {error && <p role="alert" className="text-sm text-[#B3261E]">{error}</p>}

      <button type="submit" disabled={loading} className="btn-mint w-full disabled:opacity-50 disabled:cursor-not-allowed">
        {loading ? "Enviando…" : "Confirmar registro →"}
      </button>

      <p className="text-[11px] text-[var(--cm-on-surface-variant)]/70 text-center">
        Al confirmar te enviamos los datos de pago (Yape o transferencia BCP) a tu correo.
      </p>
    </form>
  );
}
