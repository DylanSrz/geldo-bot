import aiosqlite
import time
from utils.config import DB_PATH

# ══════════════════════════════════════════════════════════════════
#  INICIALIZACIÓN — crea todas las tablas si no existen
#  Llamar una sola vez al arrancar el bot, desde main.py
# ══════════════════════════════════════════════════════════════════


async def init_db():
    """Crea todas las tablas necesarias. Seguro de llamar varias veces."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Mejora de rendimiento: escrituras en memoria, flush cada 1000ms
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA synchronous=NORMAL")

        # ── Configuración por servidor ─────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guilds (
                guild_id          TEXT PRIMARY KEY,
                prefix            TEXT    DEFAULT '!',
                welcome_channel   TEXT    DEFAULT NULL,
                log_channel       TEXT    DEFAULT NULL,
                mute_role         TEXT    DEFAULT NULL,
                welcome_message   TEXT    DEFAULT NULL,
                staff_role        TEXT    DEFAULT NULL,
                casino_channel    TEXT    DEFAULT NULL
            )
        """)

        # ── Niveles y XP por usuario por servidor ──────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS levels (
                guild_id    TEXT    NOT NULL,
                user_id     TEXT    NOT NULL,
                xp          INTEGER DEFAULT 0,
                nivel       INTEGER DEFAULT 1,
                last_xp_at  INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
        """)

        # ── Economía virtual ───────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS economy (
                guild_id      TEXT    NOT NULL,
                user_id       TEXT    NOT NULL,
                coins         INTEGER DEFAULT 0,
                last_daily    INTEGER DEFAULT 0,
                total_earned  INTEGER DEFAULT 0,
                PRIMARY KEY (guild_id, user_id)
            )
        """)

        # ── Advertencias de moderación ─────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    TEXT    NOT NULL,
                user_id     TEXT    NOT NULL,
                mod_id      TEXT    NOT NULL,
                reason      TEXT    NOT NULL,
                created_at  INTEGER NOT NULL
            )
        """)

        # ── Tickets de soporte ─────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id    TEXT    NOT NULL,
                user_id     TEXT    NOT NULL,
                channel_id  TEXT    NOT NULL,
                status      TEXT    DEFAULT 'open',
                opened_at   INTEGER NOT NULL,
                closed_at   INTEGER DEFAULT NULL
            )
        """)

        # ── Registro de invitaciones ───────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS invites (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id     TEXT    NOT NULL,
                user_id      TEXT    NOT NULL,
                inviter_id   TEXT    DEFAULT NULL,
                invite_code  TEXT    DEFAULT NULL,
                joined_at    INTEGER NOT NULL
            )
        """)

        await db.commit()
    print("✅ Base de datos inicializada correctamente.")


# ══════════════════════════════════════════════════════════════════
#  GUILDS — configuración por servidor
# ══════════════════════════════════════════════════════════════════


async def get_guild(guild_id: int) -> dict | None:
    """Devuelve la config del servidor, o None si no existe."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM guilds WHERE guild_id = ?", (str(guild_id),)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def ensure_guild(guild_id: int):
    """Crea la fila del servidor si no existe. Llamar antes de leer config."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO guilds (guild_id) VALUES (?)", (str(guild_id),)
        )
        await db.commit()


async def set_guild_config(guild_id: int, campo: str, valor: str | None):
    """Actualiza un campo de configuración. Pasar None para limpiar."""
    campos_validos = {
        "prefix",
        "welcome_channel",
        "log_channel",
        "mute_role",
        "welcome_message",
        "staff_role",
        "casino_channel",
    }
    if campo not in campos_validos:
        raise ValueError(f"Campo inválido: {campo}")

    await ensure_guild(guild_id)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE guilds SET {campo} = ? WHERE guild_id = ?", (valor, str(guild_id))
        )
        await db.commit()


# ══════════════════════════════════════════════════════════════════
#  LEVELS — XP y niveles
# ══════════════════════════════════════════════════════════════════

XP_POR_MENSAJE = 10
XP_COOLDOWN_SEG = 60  # segundos entre mensajes que dan XP


async def get_user_level(guild_id: int, user_id: int) -> dict | None:
    """Devuelve los datos de nivel del usuario, o None si no existe."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM levels WHERE guild_id = ? AND user_id = ?",
            (str(guild_id), str(user_id)),
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def add_xp(guild_id: int, user_id: int) -> dict:
    """
    Añade XP al usuario respetando el cooldown.
    Devuelve dict con: xp, nivel, subio_nivel (bool).
    """
    ahora = int(time.time())

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        await db.execute(
            """
            INSERT OR IGNORE INTO levels (guild_id, user_id)
            VALUES (?, ?)
        """,
            (str(guild_id), str(user_id)),
        )

        async with db.execute(
            "SELECT * FROM levels WHERE guild_id = ? AND user_id = ?",
            (str(guild_id), str(user_id)),
        ) as cursor:
            datos = dict(await cursor.fetchone())

        if ahora - datos["last_xp_at"] < XP_COOLDOWN_SEG:
            return {"xp": datos["xp"], "nivel": datos["nivel"], "subio_nivel": False}

        nuevo_xp = datos["xp"] + XP_POR_MENSAJE
        nivel_actual = datos["nivel"]
        xp_para_subir = nivel_actual * 100
        subio_nivel = False

        if nuevo_xp >= xp_para_subir:
            nivel_actual += 1
            nuevo_xp = 0
            subio_nivel = True

        await db.execute(
            """
            UPDATE levels
            SET xp = ?, nivel = ?, last_xp_at = ?
            WHERE guild_id = ? AND user_id = ?
        """,
            (nuevo_xp, nivel_actual, ahora, str(guild_id), str(user_id)),
        )
        await db.commit()

        return {"xp": nuevo_xp, "nivel": nivel_actual, "subio_nivel": subio_nivel}


async def get_leaderboard(guild_id: int, limit: int = 5) -> list[dict]:
    """Devuelve los top N usuarios del servidor ordenados por nivel y XP."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT user_id, xp, nivel
            FROM levels
            WHERE guild_id = ?
            ORDER BY nivel DESC, xp DESC
            LIMIT ?
        """,
            (str(guild_id), limit),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


# ══════════════════════════════════════════════════════════════════
#  ECONOMY — monedas virtuales
# ══════════════════════════════════════════════════════════════════

DAILY_COINS = 100
DAILY_COOLDOWN = 86400  # 24 horas en segundos


async def get_economy(guild_id: int, user_id: int) -> dict:
    """Devuelve la economía del usuario, creándola si no existe."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute(
            "INSERT OR IGNORE INTO economy (guild_id, user_id) VALUES (?, ?)",
            (str(guild_id), str(user_id)),
        )
        await db.commit()
        async with db.execute(
            "SELECT * FROM economy WHERE guild_id = ? AND user_id = ?",
            (str(guild_id), str(user_id)),
        ) as cursor:
            return dict(await cursor.fetchone())


async def add_coins(guild_id: int, user_id: int, cantidad: int):
    """Añade (o resta si es negativo) monedas al usuario."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO economy (guild_id, user_id) VALUES (?, ?)",
            (str(guild_id), str(user_id)),
        )
        await db.execute(
            """
            UPDATE economy
            SET coins = coins + ?,
                total_earned = total_earned + MAX(0, ?)
            WHERE guild_id = ? AND user_id = ?
        """,
            (cantidad, cantidad, str(guild_id), str(user_id)),
        )
        await db.commit()


async def claim_daily(guild_id: int, user_id: int) -> dict:
    """
    Intenta reclamar el daily. Devuelve:
      { "exito": True,  "coins": <nuevo total> }
      { "exito": False, "segundos_restantes": <int> }
    """
    ahora = int(time.time())
    eco = await get_economy(guild_id, user_id)
    diff = ahora - eco["last_daily"]

    if diff < DAILY_COOLDOWN:
        return {"exito": False, "segundos_restantes": DAILY_COOLDOWN - diff}

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE economy
            SET coins        = coins + ?,
                total_earned = total_earned + ?,
                last_daily   = ?
            WHERE guild_id = ? AND user_id = ?
        """,
            (DAILY_COINS, DAILY_COINS, ahora, str(guild_id), str(user_id)),
        )
        await db.commit()

    eco_nuevo = await get_economy(guild_id, user_id)
    return {"exito": True, "coins": eco_nuevo["coins"]}


# ══════════════════════════════════════════════════════════════════
#  WARNINGS — sistema de advertencias persistente
# ══════════════════════════════════════════════════════════════════


async def add_warning(guild_id: int, user_id: int, mod_id: int, reason: str) -> int:
    """Añade una advertencia y devuelve el total acumulado del usuario."""
    ahora = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO warnings (guild_id, user_id, mod_id, reason, created_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (str(guild_id), str(user_id), str(mod_id), reason, ahora),
        )
        await db.commit()

    return await count_warnings(guild_id, user_id)


async def count_warnings(guild_id: int, user_id: int) -> int:
    """Devuelve el número de advertencias activas del usuario."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT COUNT(*) FROM warnings
            WHERE guild_id = ? AND user_id = ?
        """,
            (str(guild_id), str(user_id)),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0]


async def get_warnings(guild_id: int, user_id: int) -> list[dict]:
    """Devuelve todas las advertencias del usuario."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT * FROM warnings
            WHERE guild_id = ? AND user_id = ?
            ORDER BY created_at DESC
        """,
            (str(guild_id), str(user_id)),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]


async def clear_warnings(guild_id: int, user_id: int):
    """Borra todas las advertencias del usuario (tras expulsión, etc.)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM warnings WHERE guild_id = ? AND user_id = ?",
            (str(guild_id), str(user_id)),
        )
        await db.commit()


# ══════════════════════════════════════════════════════════════════
#  INVITES — registro de quién invitó a quién
# ══════════════════════════════════════════════════════════════════


async def save_invite(
    guild_id: int, user_id: int, inviter_id: int | None, invite_code: str | None
):
    """
    Guarda el registro de entrada de un miembro con su invitador.
    inviter_id e invite_code pueden ser None si no se pudo detectar.
    """
    ahora = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO invites (guild_id, user_id, inviter_id, invite_code, joined_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                str(guild_id),
                str(user_id),
                str(inviter_id) if inviter_id else None,
                invite_code,
                ahora,
            ),
        )
        await db.commit()


async def get_invite_info(guild_id: int, user_id: int) -> dict | None:
    """
    Devuelve el registro de entrada más reciente de un usuario.
    Útil para el comando /invitaciones <usuario>.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT * FROM invites
            WHERE guild_id = ? AND user_id = ?
            ORDER BY joined_at DESC
            LIMIT 1
        """,
            (str(guild_id), str(user_id)),
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def get_invited_by(guild_id: int, inviter_id: int) -> list[dict]:
    """
    Devuelve todos los usuarios que fueron invitados por inviter_id.
    Útil para ver cuántas personas ha traído alguien al servidor.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT * FROM invites
            WHERE guild_id = ? AND inviter_id = ?
            ORDER BY joined_at DESC
        """,
            (str(guild_id), str(inviter_id)),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
