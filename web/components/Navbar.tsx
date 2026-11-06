import Image from "next/image";
import InviteButton from "./InviteButton";
import { SITE } from "@/lib/config";

const links = [
  { href: "#caracteristicas", label: "Características" },
  { href: "#como-usar", label: "Cómo usar" },
  { href: "#comandos", label: "Comandos" },
  { href: "#faq", label: "FAQ" },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-ink-700/60 bg-ink-900/80 backdrop-blur-md">
      <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <a href="#top" className="flex items-center gap-2.5">
          <Image
            src={SITE.logo}
            alt={`Logo de ${SITE.name}`}
            width={40}
            height={40}
            className="h-10 w-10 object-contain"
            priority
          />
          <span className="text-lg font-extrabold tracking-tight text-white">
            {SITE.name}
          </span>
        </a>

        <ul className="hidden items-center gap-8 md:flex">
          {links.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className="text-sm font-medium text-slate-300 transition-colors hover:text-white"
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <InviteButton className="!px-4 !py-2">Añadir a Discord</InviteButton>
      </nav>
    </header>
  );
}
