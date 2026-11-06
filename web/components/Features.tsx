import { FEATURES } from "@/lib/commands";

export default function Features() {
  return (
    <section id="caracteristicas" className="px-4 py-20 sm:px-6">
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-black text-white sm:text-4xl">
            Todo lo que tu comunidad necesita
          </h2>
          <p className="mt-4 text-slate-400">
            Un solo bot reemplaza a media docena. Cada módulo funciona de forma
            independiente y se configura a tu gusto.
          </p>
        </div>

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature) => (
            <div
              key={feature.title}
              className="group rounded-2xl border border-ink-700 bg-ink-800/50 p-6 transition-all duration-200 hover:-translate-y-1 hover:border-blurple/50 hover:bg-ink-700/60"
            >
              <div className="mb-4 grid h-12 w-12 place-items-center rounded-xl bg-ink-700 text-2xl transition-colors group-hover:bg-blurple/20">
                {feature.emoji}
              </div>
              <h3 className="text-lg font-bold text-white">{feature.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-400">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
