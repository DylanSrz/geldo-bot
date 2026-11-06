import discord
from discord import app_commands
from discord.ext import commands
from utils import db


class Ayuda(commands.Cog):
    """Comando de ayuda — lista todos los comandos del bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    # ══════════════════════════════════════════════════════════════
    #  /help
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="help",
        description="Muestra todos los comandos disponibles del bot"
    )
    async def help(self, interaction: discord.Interaction):

        # ── Embed público — visible para todos ────────────────────
        embed_publico = discord.Embed(
            title="📖 Comandos de GELDO",
            description="Aquí están todos los comandos disponibles para los miembros del servidor.",
            color=discord.Color.blurple()
        )
        if interaction.guild.icon:
            embed_publico.set_thumbnail(url=interaction.guild.icon.url)

        embed_publico.add_field(
            name="🎮 Diversión",
            value=(
                "`/meme` — Trae un meme aleatorio\n"
                "`/chiste` — Cuenta un chiste aleatorio\n"
                "`/dado [caras]` — Tira un dado (2-100 caras)\n"
                "`/coinflip` — Lanza una moneda\n"
                "`/8ball <pregunta>` — Pregúntale a la bola mágica\n"
                "`/trivia` — Responde una pregunta en 15 segundos"
            ),
            inline=False
        )

        embed_publico.add_field(
            name="💰 Economía",
            value=(
                "`/balance [usuario]` — Consulta tus monedas\n"
                "`/daily` — Reclama tus monedas diarias\n"
                "`/transferir <usuario> <cantidad>` — Envía monedas\n"
                "`/top` — Ranking de los más ricos del servidor"
            ),
            inline=False
        )

        embed_publico.add_field(
            name="⭐ Niveles",
            value=(
                "`/nivel [usuario]` — Consulta tu nivel y XP\n"
                "`/ranking` — Top 5 usuarios con más nivel"
            ),
            inline=False
        )

        embed_publico.add_field(
            name="🔍 Utilidad",
            value=(
                "`/clima <ciudad>` — Clima actual de una ciudad\n"
                "`/traducir <texto> <idioma>` — Traduce un texto\n"
                "`/poll <pregunta> <op1> <op2>` — Crea una encuesta\n"
                "`/userinfo [usuario]` — Info de un usuario\n"
                "`/serverinfo` — Info del servidor"
            ),
            inline=False
        )

        embed_publico.add_field(
            name="🐾 Pokémon",
            value="`/poke <nombre>` — Info y sprite de un Pokémon",
            inline=False
        )

        embed_publico.add_field(
            name="🎮 MU Acacias",
            value="`/estado` — Estado actual del servidor de juego",
            inline=False
        )

        embed_publico.add_field(
            name="🎫 Tickets",
            value=(
                "`/setuptickets <canal>` — Abre el panel de tickets\n"
                "Presiona el botón **Abrir ticket** en el canal configurado"
            ),
            inline=False
        )

        embed_publico.set_footer(text="GELDO Bot • Usa /help para ver este menú")
        embed_publico.timestamp = discord.utils.utcnow()

        # Enviamos el embed público visible para todos
        await interaction.response.send_message(embed=embed_publico)

        # ── Verificamos si es staff o admin ───────────────────────
        config    = await db.get_guild(interaction.guild.id)
        rol_id    = config.get("staff_role") if config else None
        rol_staff = interaction.guild.get_role(int(rol_id)) if rol_id else None

        es_admin = interaction.user.guild_permissions.administrator
        es_staff = rol_staff in interaction.user.roles if rol_staff else False

        if not (es_admin or es_staff):
            return   # no mostramos el embed de staff a usuarios normales

        # ── Embed de staff — solo visible para staff/admins ───────
        embed_staff = discord.Embed(
            title="🛡️ Comandos de Staff",
            description="Estos comandos son exclusivos para el equipo de moderación y administración.",
            color=discord.Color.red()
        )

        embed_staff.add_field(
            name="⚙️ Configuración del servidor",
            value=(
                "`/setup` — Ver la configuración actual\n"
                "`/setwelcome <canal> [mensaje]` — Canal de bienvenida\n"
                "`/setlogs <canal>` — Canal de logs\n"
                "`/setmute <rol>` — Rol de mute\n"
                "`/setstaff <rol>` — Rol de staff\n"
                "`/resetconfig` — Restablecer toda la configuración"
            ),
            inline=False
        )

        embed_staff.add_field(
            name="🔨 Moderación",
            value=(
                "`/kick <usuario> [razón]` — Expulsar usuario\n"
                "`/ban <usuario> [razón]` — Banear usuario\n"
                "`/mute <usuario> <minutos> [razón]` — Silenciar usuario\n"
                "`/unmute <usuario>` — Quitar silencio\n"
                "`/warn <usuario> <razón>` — Advertir usuario\n"
                "`/warns <usuario>` — Ver advertencias de un usuario\n"
                "`/unwarn <usuario>` — Borrar advertencias"
            ),
            inline=False
        )

        embed_staff.add_field(
            name="✉️ Invitaciones",
            value="`/invitaciones <usuario>` — Ver quién invitó a un usuario y a quiénes ha invitado",
            inline=False
        )

        embed_staff.add_field(
            name="🎫 Tickets",
            value=(
                "`/setuptickets <canal> [rol_staff]` — Configurar panel de tickets\n"
                "`/cerrarticket` — Cerrar el ticket del canal actual"
            ),
            inline=False
        )

        embed_staff.add_field(
            name="💰 Economía (admin)",
            value="`/darmonedas <usuario> <cantidad>` — Dar o quitar monedas",
            inline=False
        )

        embed_staff.add_field(
            name="⭐ Niveles (admin)",
            value="`/darxp <usuario> <cantidad>` — Dar XP manualmente",
            inline=False
        )

        embed_staff.set_footer(text="Solo visible para staff y administradores")
        embed_staff.timestamp = discord.utils.utcnow()

        # Enviamos el embed de staff como followup ephemeral
        await interaction.followup.send(embed=embed_staff, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Ayuda(bot))