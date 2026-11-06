// Configuración global del sitio.
//
// Link de invitación OAuth2 del bot. Incluye los scopes bot y
// applications.commands para que se inviten también los comandos slash.
// permissions=8 = Administrador; ajústalo si prefieres permisos más acotados.
export const INVITE_URL =
  "https://discord.com/oauth2/authorize?client_id=1367523930105057300&permissions=8&scope=bot+applications.commands";

export const GITHUB_URL = "https://github.com/DylanSrz/GELDO";

export const SITE = {
  name: "GELDO",
  tagline: "El bot todo-en-uno para tu servidor de Discord",
  description:
    "Economía virtual, niveles, casino, moderación, tickets y mucho más. Todo en español y aislado por servidor.",
  // TODO: coloca el logo real en /public/logo.png
  logo: "/logo.png",
};
