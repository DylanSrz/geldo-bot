import discord
from discord import app_commands
from discord.ext import commands
from utils import db
from cogs.minijuegos import PanelCasino


class Setup(commands.Cog):
    """Configuración del bot por servidor."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    # ══════════════════════════════════════════════════════════════
    #  /setup — muestra la configuración actual
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="setup",
        description="Muestra la configuración actual del bot en este servidor"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        await db.ensure_guild(interaction.guild.id)
        config = await db.get_guild(interaction.guild.id)

        # ── Resolvemos los IDs a menciones legibles ────────────────
        def canal(field):
            if not config.get(field):
                return "❌ No configurado"
            c = interaction.guild.get_channel(int(config[field]))
            return c.mention if c else "⚠️ Canal eliminado"

        def rol(field):
            if not config.get(field):
                return "❌ No configurado"
            r = interaction.guild.get_role(int(config[field]))
            return r.mention if r else "⚠️ Rol eliminado"

        embed = discord.Embed(
            title=f"⚙️ Configuración de {interaction.guild.name}",
            color=discord.Color.blue()
        )
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)

        embed.add_field(
            name="👋 Canal de bienvenida",
            value=canal("welcome_channel"),
            inline=True
        )
        embed.add_field(
            name="📋 Canal de logs",
            value=canal("log_channel"),
            inline=True
        )
        embed.add_field(
            name="🔇 Rol de mute",
            value=rol("mute_role"),
            inline=True
        )
        embed.add_field(
            name="🛡️ Rol de staff",
            value=rol("staff_role"),
            inline=True
        )
        embed.add_field(
            name="💬 Prefijo",
            value=f"`{config.get('prefix', '!')}`",
            inline=True
        )
        embed.add_field(
            name="📝 Mensaje de bienvenida",
            value=(
                f"```{config['welcome_message']}```"
                if config.get("welcome_message")
                else "❌ No configurado (usa el mensaje por defecto)"
            ),
            inline=False
        )
        embed.set_footer(
            text="Usa /setwelcome, /setlogs, /setmute, /setstaff para configurar"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @setup.error
    async def setup_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Solo los administradores pueden ver la configuración.",
                ephemeral=True
            )


    # ══════════════════════════════════════════════════════════════
    #  /setwelcome <canal> [mensaje]
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="setwelcome",
        description="Configura el canal y mensaje de bienvenida"
    )
    @app_commands.describe(
        canal="Canal donde se enviarán las bienvenidas",
        mensaje="Mensaje personalizado. Placeholders: {usuario} {nombre} {servidor} {miembros}"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setwelcome(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel,
        mensaje: str | None = None
    ):
        await db.set_guild_config(interaction.guild.id, "welcome_channel", str(canal.id))
        if mensaje:
            await db.set_guild_config(interaction.guild.id, "welcome_message", mensaje)

        preview = mensaje or f"¡Esperamos que disfrutes tu estadía en **{interaction.guild.name}**! 🎉"
        preview = (
            preview
            .replace("{usuario}",  interaction.user.mention)
            .replace("{nombre}",   interaction.user.display_name)
            .replace("{servidor}", interaction.guild.name)
            .replace("{miembros}", str(interaction.guild.member_count))
        )

        embed = discord.Embed(
            title="✅ Canal de bienvenida configurado",
            color=discord.Color.green()
        )
        embed.add_field(name="📢 Canal",        value=canal.mention, inline=True)
        embed.add_field(name="👁️ Vista previa", value=preview,       inline=False)
        embed.set_footer(
            text="Placeholders: {usuario} {nombre} {servidor} {miembros}"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @setwelcome.error
    async def setwelcome_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Solo los administradores pueden configurar la bienvenida.",
                ephemeral=True
            )


    # ══════════════════════════════════════════════════════════════
    #  /setlogs <canal>
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="setlogs",
        description="Configura el canal de logs de moderación"
    )
    @app_commands.describe(canal="Canal donde se enviarán los logs")
    @app_commands.checks.has_permissions(administrator=True)
    async def setlogs(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):
        await db.set_guild_config(interaction.guild.id, "log_channel", str(canal.id))

        embed = discord.Embed(
            title="✅ Canal de logs configurado",
            color=discord.Color.green()
        )
        embed.add_field(name="📋 Canal", value=canal.mention, inline=True)
        embed.set_footer(
            text="Aquí llegarán los logs de kicks, bans, warns y salidas"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @setlogs.error
    async def setlogs_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Solo los administradores pueden configurar los logs.",
                ephemeral=True
            )


    # ══════════════════════════════════════════════════════════════
    #  /setmute <rol>
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="setmute",
        description="Configura el rol de mute del servidor"
    )
    @app_commands.describe(rol="Rol que se asignará al silenciar usuarios")
    @app_commands.checks.has_permissions(administrator=True)
    async def setmute(
        self,
        interaction: discord.Interaction,
        rol: discord.Role
    ):
        await db.set_guild_config(interaction.guild.id, "mute_role", str(rol.id))

        embed = discord.Embed(
            title="✅ Rol de mute configurado",
            color=discord.Color.green()
        )
        embed.add_field(name="🔇 Rol", value=rol.mention, inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @setmute.error
    async def setmute_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Solo los administradores pueden configurar el rol de mute.",
                ephemeral=True
            )


    # ══════════════════════════════════════════════════════════════
    #  /setstaff <rol>
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="setstaff",
        description="Configura el rol de staff para el sistema de tickets"
    )
    @app_commands.describe(rol="Rol que podrá ver y responder tickets")
    @app_commands.checks.has_permissions(administrator=True)
    async def setstaff(
        self,
        interaction: discord.Interaction,
        rol: discord.Role
    ):
        await db.set_guild_config(interaction.guild.id, "staff_role", str(rol.id))

        embed = discord.Embed(
            title="✅ Rol de staff configurado",
            color=discord.Color.green()
        )
        embed.add_field(name="🛡️ Rol", value=rol.mention, inline=True)
        embed.set_footer(text="Este rol podrá ver y responder todos los tickets")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @setstaff.error
    async def setstaff_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Solo los administradores pueden configurar el rol de staff.",
                ephemeral=True
            )


    # ══════════════════════════════════════════════════════════════
    #  /resetconfig
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="resetconfig",
        description="Restablece toda la configuración del servidor a los valores por defecto"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def resetconfig(self, interaction: discord.Interaction):

        # Pedimos confirmación antes de borrar todo
        embed = discord.Embed(
            title="⚠️ ¿Estás seguro?",
            description=(
                "Esto borrará **toda** la configuración del servidor:\n"
                "canal de bienvenida, logs, rol de mute, rol de staff "
                "y mensaje de bienvenida.\n\n"
                "Esta acción **no se puede deshacer**."
            ),
            color=discord.Color.orange()
        )
        await interaction.response.send_message(
            embed=embed,
            view=ConfirmarReset(interaction.user.id),
            ephemeral=True
        )

    @resetconfig.error
    async def resetconfig_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Solo los administradores pueden resetear la configuración.",
                ephemeral=True
            )

    # ══════════════════════════════════════════════════════════════════
    #  /setupcasino <canal>
    # ══════════════════════════════════════════════════════════════════

    @app_commands.command(
        name="setupcasino",
        description="Despliega el panel del casino en un canal"
    )
    @app_commands.describe(canal="Canal donde aparecerá el panel del casino")
    @app_commands.checks.has_permissions(administrator=True)
    async def setupcasino(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):
        await db.set_guild_config(interaction.guild.id, "casino_channel", str(canal.id))

        embed = discord.Embed(
            title="🎰 Casino configurado",
            description=(
                "El panel del casino ha sido enviado a "
                f"{canal.mention}.\n\n"
                "Los usuarios podrán jugar **Blackjack**, "
                "**Tragamonedas**, **Ruleta** y **Coinflip** "
                "directamente desde ese canal."
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(text="Usa /setupcasino nuevamente para mover el panel")
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Enviamos el panel al canal configurado
        panel_embed = discord.Embed(
            title="🎰 Bienvenido al Casino",
            description=(
                "¡Prueba tu suerte apostando tus monedas!\n\n"
                "🃏 **Blackjack** — Plántate o pide carta. Llega a 21 sin pasarte.\n"
                "🎰 **Tragamonedas** — Gira los carretes y busca el jackpot.\n"
                "🎡 **Ruleta** — Apuesta al número, color o par/impar.\n"
                "🪙 **Coinflip** — Cara o cruz, dobla o pierdes.\n\n"
                "📌 Solo puedes tener **una partida activa** a la vez.\n"
                "⏱️ Las partidas se borran automáticamente a los **5 minutos**."
            ),
            color=discord.Color.gold()
        )
        if interaction.guild.icon:
            panel_embed.set_thumbnail(url=interaction.guild.icon.url)
        panel_embed.set_footer(text=interaction.guild.name)

        await canal.send(embed=panel_embed, view=PanelCasino())

    @setupcasino.error
    async def setupcasino_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Solo los administradores pueden configurar el casino.",
                ephemeral=True
            )


# ══════════════════════════════════════════════════════════════════
#  VIEW — confirmación para /resetconfig
# ══════════════════════════════════════════════════════════════════

class ConfirmarReset(discord.ui.View):

    def __init__(self, admin_id: int):
        super().__init__(timeout=30)
        self.admin_id = admin_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Solo el admin que ejecutó el comando puede confirmar
        if interaction.user.id != self.admin_id:
            await interaction.response.send_message(
                "❌ Solo quien ejecutó el comando puede confirmar.",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Sí, resetear", style=discord.ButtonStyle.danger)
    async def confirmar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        for campo in [
            "welcome_channel", "log_channel",
            "mute_role", "staff_role", "welcome_message", "casino_channel"
        ]:
            await db.set_guild_config(interaction.guild.id, campo, None)

        await interaction.response.edit_message(
            embed=discord.Embed(
                description="✅ Configuración restablecida correctamente.",
                color=discord.Color.green()
            ),
            view=None
        )

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancelar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            embed=discord.Embed(
                description="❌ Reset cancelado.",
                color=discord.Color.red()
            ),
            view=None
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))