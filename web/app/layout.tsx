import type { Metadata } from "next";
import { Analytics } from "@vercel/analytics/next";
import "./globals.css";
import { SITE } from "@/lib/config";

export const metadata: Metadata = {
  metadataBase: new URL("https://geldo.vercel.app"),
  title: `${SITE.name} — ${SITE.tagline}`,
  description: SITE.description,
  keywords: [
    "bot de discord",
    "discord bot",
    "GELDO",
    "economía discord",
    "niveles discord",
    "casino discord",
    "moderación discord",
    "tickets discord",
  ],
  openGraph: {
    title: `${SITE.name} — ${SITE.tagline}`,
    description: SITE.description,
    type: "website",
    locale: "es_ES",
  },
  twitter: {
    card: "summary_large_image",
    title: `${SITE.name} — ${SITE.tagline}`,
    description: SITE.description,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  );
}
