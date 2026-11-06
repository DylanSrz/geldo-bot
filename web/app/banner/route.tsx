import { ImageResponse } from "next/og";
import { readFileSync } from "fs";
import { join } from "path";
import { SITE } from "@/lib/config";

// Cartel/banner 680x240 (17:6) — p. ej. para el App Directory de Discord.
export const runtime = "nodejs";
export const dynamic = "force-static";

export function GET() {
  const logoData = readFileSync(join(process.cwd(), "public/logo.png"));
  const logoSrc = `data:image/png;base64,${logoData.toString("base64")}`;

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          gap: 28,
          padding: 28,
          backgroundColor: "#0b0c14",
          position: "relative",
        }}
      >
        {/* Resplandor */}
        <div
          style={{
            position: "absolute",
            top: -160,
            left: 60,
            width: 460,
            height: 360,
            backgroundImage:
              "radial-gradient(closest-side, rgba(88,101,242,0.5), rgba(11,12,20,0))",
            display: "flex",
          }}
        />

        {/* Logo */}
        <img
          src={logoSrc}
          width={196}
          height={196}
          style={{
            width: 196,
            height: 196,
            objectFit: "contain",
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
              fontSize: 14,
              color: "#9aa3b2",
              letterSpacing: 1.5,
              marginBottom: 6,
            }}
          >
            BOT DE DISCORD · 100% EN ESPAÑOL
          </div>

          <div
            style={{
              display: "flex",
              fontSize: 68,
              fontWeight: 800,
              color: "#ffffff",
              lineHeight: 1,
              letterSpacing: -2,
            }}
          >
            {SITE.name}
          </div>

          <div
            style={{
              display: "flex",
              fontSize: 22,
              color: "#cbd5e1",
              marginTop: 10,
              lineHeight: 1.2,
            }}
          >
            {SITE.tagline}
          </div>

          {/* Pills */}
          <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
            {["Economía", "Niveles", "Casino", "Moderación"].map((label) => (
              <div
                key={label}
                style={{
                  display: "flex",
                  padding: "5px 12px",
                  borderRadius: 9999,
                  backgroundColor: "rgba(88,101,242,0.16)",
                  border: "1px solid rgba(88,101,242,0.4)",
                  color: "#c7ccff",
                  fontSize: 15,
                }}
              >
                {label}
              </div>
            ))}
          </div>
        </div>
      </div>
    ),
    { width: 680, height: 240 },
  );
}
