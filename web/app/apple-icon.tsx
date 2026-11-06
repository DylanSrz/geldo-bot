import { ImageResponse } from "next/og";
import { readFileSync } from "fs";
import { join } from "path";

// Apple touch icon (pantalla de inicio en iOS): logo sobre fondo oscuro.
export const runtime = "nodejs";
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
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
          justifyContent: "center",
          background:
            "radial-gradient(circle at 50% 42%, #2a1850 0%, #0b0c14 75%)",
        }}
      >
        <img
          src={logoSrc}
          width={152}
          height={152}
          style={{ width: 152, height: 152, objectFit: "contain" }}
        />
      </div>
    ),
    { ...size },
  );
}
