import os
from dotenv import load_dotenv

load_dotenv()


def _requerir(nombre: str) -> str:
    """
    Lee una variable de entorno obligatoria.
    Si no existe, lanza un error claro ANTES de que el bot intente conectarse.
    """
    valor = os.getenv(nombre)
    if not valor:
        raise EnvironmentError(
            f"\n\n❌ Variable de entorno faltante: '{nombre}'\n"
            f"   Agrégala a tu archivo .env y reinicia el bot.\n"
        )
    return valor


def _opcional(nombre: str, default=None) -> str | None:
    """
    Lee una variable de entorno opcional.
    Si no existe, devuelve el valor por defecto sin lanzar error.
    """
    return os.getenv(nombre, default)


# ══════════════════════════════════════════════════════════════════
#  OBLIGATORIAS — el bot no arranca sin estas
# ══════════════════════════════════════════════════════════════════

TOKEN = _requerir("TOKEN")


# ══════════════════════════════════════════════════════════════════
#  APIs EXTERNAS — opcionales
#
#  Si no están en el .env, su valor es None.
#  Cada Cog verifica si son None antes de usar el comando,
#  y avisa al usuario en lugar de crashear.
#
#  Ejemplo de uso en cualquier Cog:
#
#      from utils.config import WEATHER_API_KEY
#
#      @app_commands.command(name="clima")
#      async def clima(self, interaction, ciudad: str):
#          if not WEATHER_API_KEY:
#              await interaction.response.send_message(
#                  "⚠️ /clima no está disponible: falta WEATHER_API_KEY en .env",
#                  ephemeral=True
#              )
#              return
#          # ... aquí usas WEATHER_API_KEY con normalidad
#
# ══════════════════════════════════════════════════════════════════

WEATHER_API_KEY = _opcional("WEATHER_API_KEY")   # openweathermap.org
DEEPL_API_KEY   = _opcional("DEEPL_API_KEY")     # deepl.com/pro-api


# ══════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN GENERAL
# ══════════════════════════════════════════════════════════════════

PREFIX   = _opcional("PREFIX",   default="!")
DB_PATH  = _opcional("DB_PATH",  default="geldo.db")


# ══════════════════════════════════════════════════════════════════
#  VERIFICAR — imprime el estado al arrancar
#
#  Se llama desde main.py una sola vez antes de conectar a Discord.
#  Te muestra exactamente qué funciones están activas y cuáles no,
#  sin tener que abrir el .env a mano.
#
#  Salida de ejemplo:
#
#  ── Configuración cargada ───────────────────────────
#    Prefijo        : !
#    Base de datos  : geldo.db
#    Clima (/clima) : ✅ activo
#    DeepL (/trad.) : ⚠️  inactivo — agrega DEEPL_API_KEY al .env
#  ────────────────────────────────────────────────────
#
# ══════════════════════════════════════════════════════════════════

def verificar():
    print("\n── Configuración cargada ───────────────────────────")
    print(f"  Prefijo        : {PREFIX}")
    print(f"  Base de datos  : {DB_PATH}")
    print(
        f"  Clima (/clima) : "
        f"{'✅ activo' if WEATHER_API_KEY else '⚠️  inactivo — agrega WEATHER_API_KEY al .env'}"
    )
    print(
        f"  DeepL (/trad.) : "
        f"{'✅ activo' if DEEPL_API_KEY else '⚠️  inactivo — agrega DEEPL_API_KEY al .env'}"
    )
    print("────────────────────────────────────────────────────\n")