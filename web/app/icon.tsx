import { ImageResponse } from "next/og";
import { readFileSync } from "fs";
import { join } from "path";

// Favicon generado a partir del logo (optimizado, pequeño).
export const runtime = "nodejs";
export const size = { width: 96, height: 96 };
export const contentType = "image/png";

export default function Icon() {
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
        }}
      >
        <img
          src={logoSrc}
          width={96}
          height={96}
          style={{ width: 96, height: 96, objectFit: "contain" }}
        />
      </div>
    ),
    { ...size },
  );
}
