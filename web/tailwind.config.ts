import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta inspirada en Discord
        blurple: {
          DEFAULT: "#5865F2",
          dark: "#4752c4",
          light: "#7984f5",
        },
        ink: {
          900: "#0b0c14",
          800: "#13141f",
          700: "#1e1f2b",
          600: "#2a2c3a",
        },
        coin: "#f5c542", // dorado casino/economía
        emerald: {
          glow: "#22c55e",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "hero-glow":
          "radial-gradient(60% 60% at 50% 0%, rgba(88,101,242,0.25) 0%, rgba(11,12,20,0) 70%)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.6s ease-out both",
      },
    },
  },
  plugins: [],
};

export default config;
