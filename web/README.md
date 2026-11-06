# GELDO — Landing page

Página web de presentación del bot de Discord **GELDO**, construida con
**Next.js 14 (App Router)**, **React** y **Tailwind CSS**.

## Desarrollo local

```bash
cd web
npm install
npm run dev
```

Abre [http://localhost:3000](http://localhost:3000).

## Build de producción

```bash
npm run build
npm run start
```

## Configuración antes de publicar

Edita `lib/config.ts`:

- **`INVITE_URL`** — reemplaza el placeholder con el link de invitación OAuth2
  real del bot. Se genera en el [Discord Developer Portal](https://discord.com/developers/applications)
  → tu aplicación → **OAuth2 → URL Generator** (scopes: `bot` y
  `applications.commands`).
- **`GITHUB_URL`** — repositorio del proyecto (ya apunta a `DylanSrz/GELDO`).

Coloca también los assets en `public/`:

- `public/logo.png` — logo o avatar del bot.
- `public/og-image.png` — imagen de previsualización para redes (1200×630 px,
  opcional pero recomendada).

La lista de comandos y los módulos viven en `lib/commands.ts` — es la única
fuente de datos del sitio. Si añades o cambias un comando del bot, actualízalo
ahí.

## Despliegue en Vercel

1. Importa el repositorio `DylanSrz/GELDO` en [Vercel](https://vercel.com).
2. En la configuración del proyecto, establece **Root Directory = `web`**.
3. Framework preset: **Next.js** (se detecta automáticamente).
4. Despliega. Cada push a la rama configurada actualizará el sitio.

> El bot de Python (raíz del repo) y la web (`web/`) son independientes: Vercel
> solo construye la carpeta `web/` y no interfiere con el despliegue del bot.

## Estructura

```
web/
├── app/            # Layout, página principal y estilos globales
├── components/     # Secciones de la landing (Hero, Features, Commands, FAQ…)
├── lib/            # config.ts (links/branding) y commands.ts (datos)
└── public/         # logo.png, og-image.png
```
