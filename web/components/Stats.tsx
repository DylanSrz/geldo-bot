import { COMMANDS } from "@/lib/commands";

const stats = [
  { value: `${COMMANDS.length}+`, label: "Comandos" },
  { value: "11", label: "Módulos" },
  { value: "5", label: "Juegos de casino" },
  { value: "100%", label: "En español" },
];

export default function Stats() {
  return (
    <section className="border-y border-ink-700/60 bg-ink-800/40 px-4 py-10 sm:px-6">
      <div className="mx-auto grid max-w-4xl grid-cols-2 gap-8 sm:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="text-center">
            <div className="text-3xl font-black text-white sm:text-4xl">
              {stat.value}
            </div>
            <div className="mt-1 text-sm text-slate-400">{stat.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
