# 🤖 GELDO — Discord Bot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![discord.py](https://img.shields.io/badge/discord.py-2.x-5865F2?style=for-the-badge&logo=discord&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-WAL-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Bot multifuncional para Discord con arquitectura modular basada en Cogs.**  
Economía virtual, moderación, niveles, tickets, rastreo de invitaciones, Pokémon y más — todo por servidor.

</div>

> Esta es la versión pública del proyecto, publicada con un historial nuevo. El bot se despliega desde un repositorio privado.

---

## 📋 Tabla de contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Comandos](#-comandos)
- [Despliegue](#-despliegue)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Base de datos](#-base-de-datos)
- [Contribuciones](#-contribuciones)

---

## ✨ Características

| Módulo | Descripción |
|---|---|
| 🛡️ **Moderación** | Kick, ban, mute con timeout nativo, sistema de advertencias persistente con auto-kick al llegar a 3 warns |
| 💰 **Economía** | Monedas virtuales por servidor, daily, transferencias, ranking top 10 |
| 🎰 **Casino** | Paneles con botones persistentes: Blackjack, tragamonedas, ruleta, coinflip y Texas Hold'em, con las monedas del servidor |
| ⭐ **Niveles** | XP por mensaje con cooldown anti-spam, barra de progreso, leaderboard |
| 🎫 **Tickets** | Sistema con botones persistentes, canales privados por usuario, cierre automático |
| ✉️ **Invitaciones** | Rastreo de quién invitó a cada miembro, registro persistente en BD, comando `/invitaciones` exclusivo para staff |
| 🎮 **Diversión** | Memes, chistes, dados, coinflip, 8-ball, trivia en tiempo real |
| 🌍 **Utilidad** | Clima (OpenWeatherMap), traducción (DeepL), encuestas, userinfo, serverinfo |
| 🔴 **Pokémon** | Ficha completa con sprites, stats, tipos y habilidades (PokéAPI) |
| 🕹️ **MU Acacias** | Estado en tiempo real del servidor de juego (jugadores online, Castle Siege) |
| ⚙️ **Setup** | Panel de configuración por servidor con preview en tiempo real |
| 📖 **Ayuda** | Comando `/help` con vista pública y vista exclusiva para staff |

---

## 🏗️ Arquitectura

GELDO sigue una arquitectura **Cog-based** de `discord.py 2.x`, con persistencia en SQLite usando `aiosqlite` en modo WAL para operaciones no bloqueantes.

```
main.py
├── utils/
│   ├── config.py       # Validación de variables de entorno al arrancar
│   └── db.py           # Capa de acceso a datos (SQLite WAL)
└── cogs/
    ├── ayuda.py        # Comando /help con vista pública y staff
    ├── bienvenida.py   # Eventos on_member_join / on_member_remove + rastreo de invitaciones
    ├── moderacion.py   # Kick, ban, mute, warn
    ├── niveles.py      # XP y niveles por servidor
    ├── economia.py     # Monedas virtuales por servidor
    ├── tickets.py      # Sistema de tickets con Views persistentes
    ├── diversion.py    # Memes, trivia, dados, etc.
    ├── utilidad.py     # Clima, traducción, encuestas
    ├── pokemon.py      # Integración con PokéAPI
    ├── juego.py        # Estado del servidor MU Acacias
    └── setup.py        # Configuración del bot por servidor
```

**Decisiones de diseño clave:**
- La economía y los niveles son **por servidor** (no globales), garantizando aislamiento entre comunidades.
- Las Views de tickets usan `custom_id` fijo para **persistencia entre reinicios**.
- Los comandos slash se sincronizan dentro de `on_ready` para evitar errores de timing.
- Las APIs externas son **opcionales**: el bot arranca sin ellas y avisa al usuario en el comando.
- El rastreo de invitaciones combina un **cache en memoria** (para detección en tiempo real) con **persistencia en BD** (para consultas históricas).

---

## 📦 Requisitos

- Python **3.10** o superior
- Cuenta de desarrollador en [Discord](https://discord.com/developers/applications)
- (Opcional) API key de [OpenWeatherMap](https://openweathermap.org/api)
- (Opcional) API key de [DeepL Free](https://www.deepl.com/pro-api)

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/DylanSrz/geldo-bot.git
cd geldo-bot
```

### 2. Crear y activar el entorno virtual

```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar el entorno

```bash
cp .env.example .env
```

Edita `.env` con tus valores (ver [Configuración](#-configuración)).

### 5. Ejecutar el bot

```bash
python main.py
```

---

## ⚙️ Configuración

Copia `.env.example` como `.env` y rellena los valores:

```env
# ── Obligatorio ──────────────────────────────────────────────────
TOKEN=tu_token_de_discord

# ── APIs opcionales ──────────────────────────────────────────────
WEATHER_API_KEY=tu_key_openweathermap
DEEPL_API_KEY=tu_key_deepl:fx

# ── Configuración general ────────────────────────────────────────
PREFIX=!
DB_PATH=geldo.db
LOG_LEVEL=INFO
```

> ⚠️ **Nunca subas `.env` al repositorio.** Ya está incluido en `.gitignore`.

Al arrancar, el bot imprime un resumen de las APIs disponibles:

```
── Configuración cargada ───────────────────────────
  Prefijo        : !
  Base de datos  : geldo.db
  Clima (/clima) : ✅ activo
  DeepL (/trad.) : ⚠️  inactivo — agrega DEEPL_API_KEY al .env
────────────────────────────────────────────────────
```

### Configuración en Discord (por servidor)

Una vez el bot esté en tu servidor, usa los comandos de setup como administrador:

| Comando | Descripción |
|---|---|
| `/setup` | Ver la configuración actual del servidor |
| `/setwelcome #canal [mensaje]` | Canal de bienvenida con placeholders opcionales |
| `/setlogs #canal` | Canal para logs de moderación y eventos de entrada/salida |
| `/setmute @rol` | Rol de mute (para compatibilidad con bots externos) |
| `/setstaff @rol` | Rol de staff con acceso a comandos exclusivos |
| `/setuptickets #canal` | Despliega el panel de tickets en un canal |
| `/resetconfig` | Restablece toda la configuración del servidor |

**Placeholders disponibles para el mensaje de bienvenida:**
`{usuario}` `{nombre}` `{servidor}` `{miembros}`

---

## 📖 Comandos

### 📖 Ayuda

| Comando | Descripción |
|---|---|
| `/help` | Muestra todos los comandos públicos. Si eres staff o admin, también muestra los comandos exclusivos de moderación (solo visible para ti) |

### 🛡️ Moderación *(requiere permisos de staff)*

| Comando | Permisos | Descripción |
|---|---|---|
| `/kick @usuario [razón]` | Kick Members | Expulsa a un usuario |
| `/ban @usuario [razón] [días]` | Ban Members | Banea a un usuario |
| `/mute @usuario <minutos> [razón]` | Moderate Members | Timeout nativo de Discord (máx. 28 días) |
| `/unmute @usuario` | Moderate Members | Quita el timeout |
| `/warn @usuario <razón>` | Kick Members | Advierte a un usuario (auto-kick a los 3) |
| `/warns @usuario` | Kick Members | Ver historial de advertencias |
| `/unwarn @usuario` | Kick Members | Borrar todas las advertencias |

### ✉️ Invitaciones *(solo staff y admins)*

| Comando | Descripción |
|---|---|
| `/invitaciones @usuario` | Muestra quién invitó al usuario y a cuántas personas ha invitado él. El registro es persistente — sobrevive reinicios del bot |

> El canal de logs también notifica automáticamente quién invitó a cada nuevo miembro al entrar al servidor, y muestra esa información cuando un miembro sale.

### 💰 Economía

| Comando | Descripción |
|---|---|
| `/balance [@usuario]` | Ver monedas y estado del daily |
| `/daily` | Reclamar 100 monedas (cooldown de 24h) |
| `/transferir @usuario <cantidad>` | Transferir monedas a otro usuario |
| `/top` | Ranking de los 10 usuarios más ricos |
| `/darmonedas @usuario <cantidad>` | *(Admin)* Dar o quitar monedas manualmente |

### ⭐ Niveles

| Comando | Descripción |
|---|---|
| `/nivel [@usuario]` | Ver nivel, XP y barra de progreso |
| `/ranking` | Top 5 usuarios por nivel en el servidor |
| `/darxp @usuario <cantidad>` | *(Admin)* Otorgar XP manualmente |

> Los mensajes otorgan **10 XP** con un cooldown de **60 segundos** por usuario.

### 🎫 Tickets

| Comando | Descripción |
|---|---|
| `/setuptickets #canal [@staff]` | *(Admin)* Despliega el panel de tickets |
| `/cerrarticket` | Cierra el ticket del canal actual |

El sistema crea un canal privado por usuario dentro de la categoría **Tickets**. Los tickets se cierran y eliminan automáticamente tras 5 segundos de confirmación. Solo el dueño del ticket, el staff o un administrador puede cerrarlo.

### 🎮 Diversión

| Comando | Descripción |
|---|---|
| `/meme` | Meme aleatorio de Reddit |
| `/chiste` | Chiste aleatorio |
| `/dado [caras]` | Tira un dado de 2 a 100 caras (defecto: 6) |
| `/coinflip` | Cara o cruz |
| `/8ball <pregunta>` | Bola mágica |
| `/trivia` | Pregunta de trivia con 15 segundos para responder |

### 🌍 Utilidad

| Comando | Descripción |
|---|---|
| `/clima <ciudad>` | Clima actual con temperatura, humedad, viento y más |
| `/traducir <texto> <idioma>` | Traducción con DeepL (8 idiomas disponibles) |
| `/poll <pregunta> <op1> <op2> [op3] [op4]` | Encuesta con reacciones automáticas |
| `/userinfo [@usuario]` | Información detallada de un usuario |
| `/serverinfo` | Información del servidor |

### 🔴 Pokémon

| Comando | Descripción |
|---|---|
| `/poke <nombre\|número>` | Ficha completa: sprite, stats, tipos, habilidades |

### 🕹️ MU Acacias

| Comando | Descripción |
|---|---|
| `/estado` | Jugadores online, dueño del Castle Siege y guild dominante |

---

## 🚢 Despliegue

GELDO incluye un workflow de GitHub Actions para despliegue automático en una VM de Oracle (o cualquier servidor Linux) vía SSH.

### Configurar los secretos en GitHub

Ve a **Settings → Secrets and variables → Actions** y añade:

| Secreto | Valor |
|---|---|
| `SSH_HOST` | IP pública de tu VM |
| `SSH_USER` | Usuario SSH (ej. `geldo`) |
| `SSH_PRIVATE_KEY` | Contenido de tu clave privada RSA |
| `SSH_PORT` | Puerto SSH (normalmente `22`) |

### Configurar el servicio systemd en la VM

Crea el archivo `/etc/systemd/system/geldo-bot.service`:

```ini
[Unit]
Description=GELDO Discord Bot
After=network.target

[Service]
Type=simple
User=geldo
WorkingDirectory=/home/geldo/GELDO
ExecStart=/home/geldo/GELDO/venv/bin/python main.py
Restart=always
RestartSec=5
EnvironmentFile=/home/geldo/GELDO/.env

[Install]
WantedBy=multi-user.target
```

Luego habilítalo:

```bash
sudo systemctl daemon-reload
sudo systemctl enable geldo-bot.service
sudo systemctl start geldo-bot.service
```

Cada push a `main` desplegará automáticamente los cambios, instalará dependencias y reiniciará el servicio.

> ⚠️ El archivo `.env` debe existir manualmente en la VM. Para que el deploy nunca lo sobreescriba, ejecuta una vez: `git update-index --skip-worktree .env`

---

## 📁 Estructura del proyecto

```
GELDO/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD → Oracle VM vía SSH
├── cogs/
│   ├── ayuda.py                # Comando /help con vista pública y staff
│   ├── bienvenida.py           # Bienvenida + rastreo de invitaciones
│   ├── diversion.py
│   ├── economia.py
│   ├── juego.py
│   ├── moderacion.py
│   ├── niveles.py
│   ├── pokemon.py
│   ├── setup.py
│   ├── tickets.py
│   └── utilidad.py
├── utils/
│   ├── config.py               # Carga y validación de variables de entorno
│   └── db.py                   # Capa de base de datos (aiosqlite + WAL)
├── .env                        # Variables de entorno (NO subir al repo)
├── .env.example                # Plantilla de configuración
├── .gitignore
├── main.py                     # Punto de entrada
├── requirements.txt
└── README.md
```

---

## 🗄️ Base de datos

GELDO usa **SQLite** en modo WAL (`Write-Ahead Logging`) para operaciones asíncronas no bloqueantes. El archivo se crea automáticamente al iniciar el bot.

### Esquema

```sql
guilds        -- Configuración por servidor (canales, roles, mensajes)
levels        -- XP y nivel por (guild_id, user_id)
economy       -- Monedas y daily por (guild_id, user_id)
warnings      -- Advertencias de moderación con timestamp
tickets       -- Registro de tickets abiertos y cerrados
invites       -- Historial de invitaciones: quién invitó a quién y cuándo
```

Todas las tablas usan `guild_id` como parte de la clave primaria, garantizando **aislamiento total entre servidores**.

---

## 🤝 Contribuciones

1. Haz fork del repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Commitea tus cambios: `git commit -m "feat: descripción del cambio"`
4. Haz push a tu rama: `git push origin feature/nueva-funcionalidad`
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT**. Consulta el archivo `LICENSE` para más detalles.

---

<div align="center">

Hecho con ❤️ para la comunidad de Discord

</div>