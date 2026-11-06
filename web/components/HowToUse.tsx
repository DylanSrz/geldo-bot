import InviteButton from "./InviteButton";

const steps = [
  {
    number: "1",
    title: "Invita a GELDO",
    description:
      "Haz clic en «Añadir a Discord» y elige tu servidor. Necesitas permisos de administrador en él.",
  },
  {
    number: "2",
    title: "Configúralo",
    description:
      "Como admin, usa /setup, /setwelcome, /setlogs, /setstaff, /setuptickets y /setupcasino para dejarlo a tu medida.",
  },
  {
    number: "3",
    title: "¡A disfrutar!",
    description:
      "Escribe /help para ver todo. Tus miembros ganan XP escribiendo, reclaman /daily y juegan en el casino desde el primer momento.",
  },
];

export default function HowToUse() {
  return (
    <section
      id="como-usar"
      className="border-y border-ink-700/60 bg-ink-800/30 px-4 py-20 sm:px-6"
    >
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-black text-white sm:text-4xl">
            Empieza en 3 pasos
          </h2>
          <p className="mt-4 text-slate-400">
            Sin instalar nada ni tocar código. En menos de un minuto tu servidor
            estará funcionando.
          </p>
        </div>

        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {steps.map((step) => (
            <div
              key={step.number}
              className="relative rounded-2xl border border-ink-700 bg-ink-800/60 p-7"
            >
              <div className="mb-5 grid h-12 w-12 place-items-center rounded-full bg-blurple text-xl font-black text-white">
                {step.number}
              </div>
              <h3 className="text-lg font-bold text-white">{step.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-400">
                {step.description}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-12 flex justify-center">
          <InviteButton>Empezar ahora</InviteButton>
        </div>
      </div>
    </section>
  );
}
