import { ImageResponse } from "next/og";
import { readFileSync } from "fs";
import { join } from "path";
import { SITE } from "@/lib/config";

// Imagen Open Graph generada dinámicamente (preview al compartir el link).
export const runtime = "nodejs";
export const alt = `${SITE.name} — ${SITE.tagline}`;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  const logoData = readFileSync(join(process.cwd(), "public/logo.png"));
  const logoSrc = `data:image/png;base64,${logoData.toString("base64")}`;
  const bgData = readFileSync(join(process.cwd(), "public/hero-bg.png"));
  const bgSrc = `data:image/png;base64,${bgData.toString("base64")}`;

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          gap: 56,
          padding: 72,
          position: "relative",
        }}
      >
        {/* Ilustración de fondo */}
        <img
          src={bgSrc}
          width={1200}
          height={630}
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: 1200,
            height: 630,
            objectFit: "cover",
            objectPosition: "left center",
          }}
        />
        {/* Velos para legibilidad */}
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: "rgba(11,12,20,0.45)",
            display: "flex",
          }}
        />
        <div
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage:
              "linear-gradient(to right, rgba(11,12,20,0.15), rgba(11,12,20,0.75))",
            display: "flex",
          }}
        />

        {/* Logo */}
        <img
          src={logoSrc}
          width={360}
          height={360}
          style={{
            width: 360,
            height: 360,
            objectFit: "contain",
            filter: "drop-shadow(0 10px 30px rgba(0,0,0,0.55))",
          }}
        />

        {/* Texto */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            flex: 1,
          }}
        >
          <div
            style={{
              display: "flex",
              fontSize: 26,
              color: "#cbd0db",
              letterSpacing: 2,
              marginBottom: 12,
            }}
          >
            BOT DE DISCORD · 100% EN ESPAÑOL
          </div>

          <div
            style={{
              display: "flex",
              fontSize: 132,
              fontWeight: 800,
              color: "#ffffff",
              lineHeight: 1,
              letterSpacing: -4,
            }}
          >
            {SITE.name}
          </div>

          <div
            style={{
              display: "flex",
              fontSize: 40,
              color: "#e2e8f0",
              marginTop: 20,
              maxWidth: 600,
              lineHeight: 1.2,
            }}
          >
            {SITE.tagline}
          </div>

          {/* Pills de funciones */}
          <div style={{ display: "flex", gap: 14, marginTop: 36 }}>
            {["Economía", "Niveles", "Casino", "Moderación"].map((label) => (
              <div
                key={label}
                style={{
                  display: "flex",
                  padding: "10px 22px",
                  borderRadius: 9999,
                  backgroundColor: "rgba(88,101,242,0.28)",
                  border: "1px solid rgba(137,148,245,0.6)",
                  color: "#e8eaff",
                  fontSize: 26,
                }}
              >
                {label}
              </div>
            ))}
          </div>
        </div>

        {/* URL en la esquina inferior */}
        <div
          style={{
            position: "absolute",
            bottom: 40,
            right: 72,
            display: "flex",
            fontSize: 24,
            color: "#aab2c0",
          }}
        >
          geldo.vercel.app
        </div>
      </div>
    ),
    { ...size },
  );
}
