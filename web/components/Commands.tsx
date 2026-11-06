"use client";

import { useMemo, useState } from "react";
import { CATEGORIES, COMMANDS, type CategoryId } from "@/lib/commands";

type Filter = CategoryId | "all";

export default function Commands() {
  const [filter, setFilter] = useState<Filter>("all");
  const [query, setQuery] = useState("");

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return COMMANDS.filter((cmd) => {
      const matchesCategory = filter === "all" || cmd.category === filter;
      const matchesQuery =
        q === "" ||
        cmd.name.toLowerCase().includes(q) ||
        cmd.description.toLowerCase().includes(q);
      return matchesCategory && matchesQuery;
    });
  }, [filter, query]);

  return (
    <section id="comandos" className="px-4 py-20 sm:px-6">
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-black text-white sm:text-4xl">
            Explora los comandos
          </h2>
          <p className="mt-4 text-slate-400">
            Filtra por categoría o busca lo que necesites. Los comandos marcados
            como <span className="font-semibold text-coin">Staff</span> requieren
            permisos.
          </p>
        </div>

        {/* Buscador */}
        <div className="mx-auto mt-10 max-w-md">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar comando…"
            className="w-full rounded-xl border border-ink-600 bg-ink-800 px-4 py-3 text-sm text-white placeholder-slate-500 outline-none transition-colors focus:border-blurple"
          />
        </div>

        {/* Filtros por categoría */}
        <div className="mt-6 flex flex-wrap justify-center gap-2">
          <FilterChip
            active={filter === "all"}
            onClick={() => setFilter("all")}
          >
            Todos
          </FilterChip>
          {CATEGORIES.map((cat) => (
            <FilterChip
              key={cat.id}
              active={filter === cat.id}
              onClick={() => setFilter(cat.id)}
            >
              <span>{cat.emoji}</span> {cat.label}
            </FilterChip>
          ))}
        </div>

        {/* Lista */}
        <div className="mt-10 grid gap-3 sm:grid-cols-2">
          {visible.map((cmd) => (
            <div
              key={cmd.name}
              className="rounded-xl border border-ink-700 bg-ink-800/50 p-4 transition-colors hover:border-blurple/40"
            >
              <div className="flex items-center justify-between gap-3">
                <code className="font-mono text-sm font-semibold text-blurple-light">
                  {cmd.name}
                </code>
                {cmd.staffOnly && (
                  <span className="shrink-0 rounded-md bg-coin/15 px-2 py-0.5 text-xs font-semibold text-coin">
                    Staff
                  </span>
                )}
              </div>
              <p className="mt-2 text-sm leading-relaxed text-slate-400">
                {cmd.description}
              </p>
            </div>
          ))}
        </div>

        {visible.length === 0 && (
          <p className="mt-10 text-center text-slate-500">
            No se encontraron comandos para tu búsqueda.
          </p>
        )}
      </div>
    </section>
  );
}

function FilterChip({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className={`inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium transition-colors ${
        active
          ? "bg-blurple text-white"
          : "border border-ink-600 bg-ink-800/60 text-slate-300 hover:border-blurple/50 hover:text-white"
      }`}
    >
      {children}
    </button>
  );
}
