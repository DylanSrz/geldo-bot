import InviteButton from "./InviteButton";

export default function CTA() {
  return (
    <section className="px-4 py-24 sm:px-6">
      <div className="mx-auto max-w-4xl overflow-hidden rounded-3xl border border-blurple/30 bg-gradient-to-br from-blurple/20 via-ink-800 to-ink-800 px-6 py-16 text-center">
        <h2 className="text-3xl font-black text-white sm:text-4xl">
          Dale vida a tu servidor con GELDO
        </h2>
        <p className="mx-auto mt-4 max-w-xl text-slate-300">
          Economía, niveles, casino, moderación y soporte en un solo bot. Gratis
          y en español.
        </p>
        <div className="mt-8 flex justify-center">
          <InviteButton>Añadir a Discord</InviteButton>
        </div>
      </div>
    </section>
  );
}
