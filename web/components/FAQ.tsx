"use client";

import { useState } from "react";

const faqs = [
  {
    q: "¿GELDO es gratis?",
    a: "Sí. Puedes invitarlo y usar todas sus funciones sin coste. Solo necesitas permisos de administrador en tu servidor para configurarlo.",
  },
  {
    q: "¿La economía y los niveles son por servidor?",
    a: "Sí. Las monedas, la XP y los niveles están completamente aislados por servidor, así que cada comunidad tiene su propia economía sin mezclarse con otras.",
  },
  {
    q: "¿Necesito configurar APIs externas?",
    a: "No es obligatorio. El bot funciona de inmediato. Algunas funciones opcionales como el clima (/clima) y el traductor (/traducir) requieren claves de API gratuitas que el dueño del bot configura por su cuenta.",
  },
  {
    q: "¿Cómo suben de nivel mis miembros?",
    a: "Ganan 10 XP por cada mensaje, con un cooldown de 60 segundos para evitar spam. Al acumular suficiente XP suben de nivel automáticamente. Consulta tu progreso con /nivel.",
  },
  {
    q: "¿Cómo se ganan monedas?",
    a: "Con /daily reclamas 100 monedas cada 24 horas. También puedes recibir transferencias de otros usuarios con /transferir y apostar (o ganar) en el casino.",
  },
  {
    q: "¿Cómo abro un ticket de soporte?",
    a: "Si un administrador configuró el panel con /setuptickets, basta con pulsar el botón «Abrir ticket». Se creará un canal privado visible solo para ti, el staff y los administradores.",
  },
];

export default function FAQ() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section
      id="faq"
      className="border-t border-ink-700/60 bg-ink-800/30 px-4 py-20 sm:px-6"
    >
      <div className="mx-auto max-w-3xl">
        <h2 className="text-center text-3xl font-black text-white sm:text-4xl">
          Preguntas frecuentes
        </h2>

        <div className="mt-12 space-y-3">
          {faqs.map((faq, i) => {
            const isOpen = open === i;
            return (
              <div
                key={faq.q}
                className="overflow-hidden rounded-xl border border-ink-700 bg-ink-800/60"
              >
                <button
                  onClick={() => setOpen(isOpen ? null : i)}
                  className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
                >
                  <span className="font-semibold text-white">{faq.q}</span>
                  <span
                    className={`shrink-0 text-xl text-blurple-light transition-transform duration-200 ${
                      isOpen ? "rotate-45" : ""
                    }`}
                  >
                    +
                  </span>
                </button>
                {isOpen && (
                  <p className="px-5 pb-5 text-sm leading-relaxed text-slate-400">
                    {faq.a}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
