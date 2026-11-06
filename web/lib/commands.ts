// Fuente única de verdad para la lista de comandos y módulos de GELDO.
// Verificado contra README.md y los cogs en /cogs.

export type Command = {
  name: string;
  description: string;
  category: CategoryId;
  staffOnly?: boolean;
};

export type CategoryId =
  | "ayuda"
  | "moderacion"
  | "invitaciones"
  | "economia"
  | "niveles"
  | "casino"
  | "diversion"
  | "utilidad"
  | "pokemon"
  | "mu"
  | "config";

export type Category = {
  id: CategoryId;
  label: string;
  emoji: string;
};

export const CATEGORIES: Category[] = [
  { id: "moderacion", label: "Moderación", emoji: "🛡️" },
  { id: "economia", label: "Economía", emoji: "💰" },
  { id: "niveles", label: "Niveles", emoji: "⭐" },
  { id: "casino", label: "Casino", emoji: "🎰" },
  { id: "diversion", label: "Diversión", emoji: "🎮" },
  { id: "utilidad", label: "Utilidad", emoji: "🌍" },
  { id: "pokemon", label: "Pokémon", emoji: "🔴" },
  { id: "mu", label: "MU Acacias", emoji: "🕹️" },
  { id: "invitaciones", label: "Invitaciones", emoji: "✉️" },
  { id: "config", label: "Configuración", emoji: "⚙️" },
  { id: "ayuda", label: "Ayuda", emoji: "📖" },
];

export const COMMANDS: Command[] = [
  // Ayuda
  {
    name: "/help",
    description:
      "Muestra todos los comandos públicos. Si eres staff o admin, también ves los comandos exclusivos (solo visible para ti).",
    category: "ayuda",
  },

  // Moderación
  {
    name: "/kick @usuario [razón]",
    description: "Expulsa a un usuario del servidor.",
    category: "moderacion",
    staffOnly: true,
  },
  {
    name: "/ban @usuario [razón] [días]",
    description: "Banea a un usuario, con opción de borrar su historial de mensajes.",
    category: "moderacion",
    staffOnly: true,
  },
  {
    name: "/mute @usuario <minutos> [razón]",
    description: "Aplica un timeout nativo de Discord (máximo 28 días).",
    category: "moderacion",
    staffOnly: true,
  },
  {
    name: "/unmute @usuario",
    description: "Quita el timeout a un usuario.",
    category: "moderacion",
    staffOnly: true,
  },
  {
    name: "/warn @usuario <razón>",
    description: "Advierte a un usuario. Al acumular 3 advertencias se expulsa automáticamente.",
    category: "moderacion",
    staffOnly: true,
  },
  {
    name: "/warns @usuario",
    description: "Muestra el historial de advertencias de un usuario.",
    category: "moderacion",
    staffOnly: true,
  },
  {
    name: "/unwarn @usuario",
    description: "Borra todas las advertencias de un usuario.",
    category: "moderacion",
    staffOnly: true,
  },

  // Invitaciones
  {
    name: "/invitaciones @usuario",
    description:
      "Muestra quién invitó al usuario y a cuántas personas ha invitado él. El registro es persistente y sobrevive reinicios.",
    category: "invitaciones",
    staffOnly: true,
  },

  // Economía
  {
    name: "/balance [@usuario]",
    description: "Consulta tus monedas y el estado de tu recompensa diaria (o las de otro usuario).",
    category: "economia",
  },
  {
    name: "/daily",
    description: "Reclama 100 monedas. Tiene un cooldown de 24 horas.",
    category: "economia",
  },
  {
    name: "/transferir @usuario <cantidad>",
    description: "Envía monedas a otro usuario del servidor.",
    category: "economia",
  },
  {
    name: "/top",
    description: "Ranking de los 10 usuarios más ricos del servidor.",
    category: "economia",
  },
  {
    name: "/darmonedas @usuario <cantidad>",
    description: "Da o quita monedas manualmente.",
    category: "economia",
    staffOnly: true,
  },

  // Niveles
  {
    name: "/nivel [@usuario]",
    description: "Muestra el nivel, la XP y la barra de progreso de un usuario.",
    category: "niveles",
  },
  {
    name: "/ranking",
    description: "Top 5 usuarios por nivel en el servidor.",
    category: "niveles",
  },
  {
    name: "/darxp @usuario <cantidad>",
    description: "Otorga XP manualmente a un usuario.",
    category: "niveles",
    staffOnly: true,
  },

  // Casino
  {
    name: "/setupcasino #canal",
    description: "Despliega el panel del casino en un canal. Los jugadores apuestan sus monedas en 5 juegos.",
    category: "casino",
    staffOnly: true,
  },

  // Diversión
  {
    name: "/meme",
    description: "Trae un meme aleatorio de Reddit (filtra contenido NSFW).",
    category: "diversion",
  },
  {
    name: "/chiste",
    description: "Cuenta un chiste aleatorio.",
    category: "diversion",
  },
  {
    name: "/dado [caras]",
    description: "Tira un dado de 2 a 100 caras (por defecto, 6).",
    category: "diversion",
  },
  {
    name: "/coinflip",
    description: "Lanza una moneda: cara o cruz.",
    category: "diversion",
  },
  {
    name: "/8ball <pregunta>",
    description: "Pregúntale a la bola mágica.",
    category: "diversion",
  },
  {
    name: "/trivia",
    description: "Responde una pregunta de trivia con 15 segundos de tiempo límite.",
    category: "diversion",
  },

  // Utilidad
  {
    name: "/clima <ciudad>",
    description: "Clima actual con temperatura, humedad, viento y más.",
    category: "utilidad",
  },
  {
    name: "/traducir <texto> <idioma>",
    description: "Traduce texto con DeepL (8 idiomas disponibles).",
    category: "utilidad",
  },
  {
    name: "/poll <pregunta> <op1> <op2> [op3] [op4]",
    description: "Crea una encuesta con reacciones automáticas (hasta 4 opciones).",
    category: "utilidad",
  },
  {
    name: "/userinfo [@usuario]",
    description: "Información detallada de un usuario (ID, fecha de creación, roles...).",
    category: "utilidad",
  },
  {
    name: "/serverinfo",
    description: "Información del servidor (miembros, canales, roles, fecha de creación).",
    category: "utilidad",
  },

  // Pokémon
  {
    name: "/poke <nombre|número>",
    description: "Ficha completa de un Pokémon: sprite oficial, tipos, habilidades y stats.",
    category: "pokemon",
  },

  // MU Acacias
  {
    name: "/estado",
    description: "Estado en tiempo real de MU Acacias: jugadores online, dueño del Castle Siege y guild dominante.",
    category: "mu",
  },

  // Configuración
  {
    name: "/setup",
    description: "Muestra la configuración actual del servidor.",
    category: "config",
    staffOnly: true,
  },
  {
    name: "/setwelcome #canal [mensaje]",
    description:
      "Configura el canal de bienvenida. Admite placeholders: {usuario}, {nombre}, {servidor}, {miembros}.",
    category: "config",
    staffOnly: true,
  },
  {
    name: "/setlogs #canal",
    description: "Configura el canal de logs de moderación y eventos de entrada/salida.",
    category: "config",
    staffOnly: true,
  },
  {
    name: "/setmute @rol",
    description: "Configura el rol de mute (para compatibilidad con bots externos).",
    category: "config",
    staffOnly: true,
  },
  {
    name: "/setstaff @rol",
    description: "Configura el rol de staff con acceso a comandos exclusivos.",
    category: "config",
    staffOnly: true,
  },
  {
    name: "/setuptickets #canal [@staff]",
    description: "Despliega el panel de tickets en un canal.",
    category: "config",
    staffOnly: true,
  },
  {
    name: "/cerrarticket",
    description: "Cierra el ticket del canal actual.",
    category: "config",
    staffOnly: true,
  },
  {
    name: "/resetconfig",
    description: "Restablece toda la configuración del servidor.",
    category: "config",
    staffOnly: true,
  },
];

// Módulos destacados para la sección de características.
export type Feature = {
  emoji: string;
  title: string;
  description: string;
};

export const FEATURES: Feature[] = [
  {
    emoji: "🛡️",
    title: "Moderación",
    description:
      "Kick, ban, mute con timeout nativo y un sistema de advertencias persistente con auto-kick a las 3 warns. Logs automáticos de cada acción.",
  },
  {
    emoji: "💰",
    title: "Economía virtual",
    description:
      "Monedas por servidor, recompensa diaria, transferencias entre usuarios y ranking de los más ricos. Todo aislado por comunidad.",
  },
  {
    emoji: "⭐",
    title: "Niveles y XP",
    description:
      "Tus miembros ganan XP escribiendo (10 XP por mensaje, anti-spam). Barra de progreso, subidas de nivel y leaderboard.",
  },
  {
    emoji: "🎰",
    title: "Casino con 5 juegos",
    description:
      "Blackjack, tragamonedas, ruleta, coinflip y póker Texas Hold'em. Apuestan sus monedas desde un panel siempre activo.",
  },
  {
    emoji: "🎫",
    title: "Tickets de soporte",
    description:
      "Canales privados por usuario con botones persistentes que sobreviven reinicios. Cierre automático y permisos para staff.",
  },
  {
    emoji: "✉️",
    title: "Rastreo de invitaciones",
    description:
      "Sabe quién invitó a cada miembro y cuántas personas ha traído cada usuario. Registro histórico persistente.",
  },
  {
    emoji: "🎮",
    title: "Diversión",
    description:
      "Memes, chistes, dados, coinflip, bola mágica y trivia con temporizador para mantener viva la comunidad.",
  },
  {
    emoji: "🌍",
    title: "Utilidades",
    description:
      "Clima en tiempo real, traductor con DeepL (8 idiomas), encuestas con reacciones e info de usuarios y del servidor.",
  },
  {
    emoji: "🔴",
    title: "Pokémon y más",
    description:
      "Fichas completas de Pokémon con sprites, tipos, habilidades y stats, además del estado en tiempo real del servidor MU Acacias.",
  },
  {
    emoji: "⚙️",
    title: "Configuración por servidor",
    description:
      "Canales de bienvenida y logs, roles de staff y mute, paneles de tickets y casino. Cada servidor a tu medida.",
  },
];
