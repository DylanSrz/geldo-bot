import Image from "next/image";
import { GITHUB_URL, INVITE_URL, SITE } from "@/lib/config";

export default function Footer() {
  return (
    <footer className="border-t border-ink-700/60 bg-ink-900 px-4 py-10 sm:px-6">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-6 sm:flex-row">
        <div className="flex items-center gap-2.5">
          <Image
            src={SITE.logo}
            alt={`Logo de ${SITE.name}`}
            width={36}
            height={36}
            className="h-9 w-9 object-contain"
          />
          <span className="font-extrabold text-white">{SITE.name}</span>
        </div>

        <nav className="flex items-center gap-6 text-sm text-slate-400">
          <a href="#comandos" className="transition-colors hover:text-white">
            Comandos
          </a>
          <a href="#faq" className="transition-colors hover:text-white">
            FAQ
          </a>
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors hover:text-white"
          >
            GitHub
          </a>
          <a
            href={INVITE_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors hover:text-white"
          >
            Invitar
          </a>
        </nav>
      </div>

      <p className="mt-8 text-center text-sm text-slate-500">
        Hecho con ❤️ para la comunidad de Discord.
      </p>
    </footer>
  );
}
