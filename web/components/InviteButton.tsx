import { INVITE_URL } from "@/lib/config";

type Props = {
  children?: React.ReactNode;
  variant?: "primary" | "ghost";
  className?: string;
};

const DiscordIcon = () => (
  <svg
    viewBox="0 0 24 24"
    fill="currentColor"
    className="h-5 w-5"
    aria-hidden="true"
  >
    <path d="M20.317 4.369A19.79 19.79 0 0 0 16.558 3c-.2.36-.43.84-.59 1.225a18.27 18.27 0 0 0-5.937 0C9.87 3.84 9.633 3.36 9.43 3a19.74 19.74 0 0 0-3.76 1.369C2.39 9.046 1.578 13.6 1.984 18.09a19.93 19.93 0 0 0 6.073 3.06c.49-.67.927-1.382 1.304-2.13a12.93 12.93 0 0 1-2.05-.99c.172-.127.34-.26.502-.395a14.23 14.23 0 0 0 12.18 0c.164.14.332.272.502.395-.654.388-1.34.72-2.052.99.377.748.814 1.46 1.304 2.13a19.9 19.9 0 0 0 6.073-3.06c.476-5.21-.812-9.72-3.403-13.72ZM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.42 0-1.333.955-2.42 2.157-2.42 1.21 0 2.176 1.095 2.157 2.42 0 1.335-.955 2.42-2.157 2.42Zm7.96 0c-1.183 0-2.157-1.085-2.157-2.42 0-1.333.955-2.42 2.157-2.42 1.21 0 2.176 1.095 2.157 2.42 0 1.335-.946 2.42-2.157 2.42Z" />
  </svg>
);

export default function InviteButton({
  children = "Añadir a Discord",
  variant = "primary",
  className = "",
}: Props) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 text-sm font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blurple-light focus:ring-offset-2 focus:ring-offset-ink-900";
  const styles =
    variant === "primary"
      ? "bg-blurple text-white shadow-lg shadow-blurple/30 hover:bg-blurple-dark hover:shadow-blurple/40 hover:-translate-y-0.5"
      : "border border-ink-600 bg-ink-700/50 text-slate-100 hover:border-blurple/60 hover:bg-ink-600";

  return (
    <a
      href={INVITE_URL}
      target="_blank"
      rel="noopener noreferrer"
      className={`${base} ${styles} ${className}`}
    >
      <DiscordIcon />
      {children}
    </a>
  );
}
