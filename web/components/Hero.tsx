import Image from "next/image";
import InviteButton from "./InviteButton";

export default function Hero() {
  return (
    <section
      id="top"
      className="relative overflow-hidden px-4 pb-24 pt-24 sm:px-6 sm:pb-28 sm:pt-32"
    >
      {/* Obra de fondo */}
      <div className="absolute inset-0 -z-20">
        <Image
          src="/hero-bg.png"
          alt=""
          fill
          priority
          sizes="100vw"
          className="object-cover object-left md:object-center"
        />
      </div>

      {/* Velo para legibilidad + fundido hacia el fondo de la página */}
      <div className="absolute inset-0 -z-10 bg-ink-900/55" />
      <div className="absolute inset-0 -z-10 bg-gradient-to-b from-ink-900/50 via-transparent to-ink-900" />

      <div className="mx-auto max-w-4xl text-center">
        <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/15 bg-black/30 px-4 py-1.5 text-xs font-medium text-slate-200 backdrop-blur-sm">
          <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-glow" />
          Bot de Discord · 100% en español
        </span>

        <h1 className="animate-fade-up text-4xl font-black leading-tight tracking-tight text-white drop-shadow-[0_2px_20px_rgba(0,0,0,0.6)] sm:text-6xl">
          GELDO, el bot{" "}
          <span className="bg-gradient-to-r from-blurple-light to-coin bg-clip-text text-transparent">
            todo-en-uno
          </span>{" "}
          para tu servidor
        </h1>

        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-200 drop-shadow-[0_1px_10px_rgba(0,0,0,0.7)]">
          Economía virtual, niveles, un casino con 5 juegos, moderación, tickets
          y mucho más. Todo aislado por servidor y listo para usar — sin
          configuraciones complicadas.
        </p>

        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <InviteButton>Añadir a Discord</InviteButton>
          <a
            href="#comandos"
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/15 bg-black/30 px-6 py-3 text-sm font-semibold text-slate-100 backdrop-blur-sm transition-all duration-200 hover:border-blurple/60 hover:bg-black/50"
          >
            Ver comandos
          </a>
        </div>
      </div>
    </section>
  );
}
