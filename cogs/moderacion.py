import discord
from discord import app_commands
from discord.ext import commands
from utils import db
import time


class Moderacion(commands.Cog):
    """Comandos de moderación: kick, ban, mute, warn, unwarn."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    # ══════════════════════════════════════════════════════════════
    #  HELPER — embed de acción de moderación
    # ══════════════════════════════════════════════════════════════

    def _embed_mod(
        self,
        titulo: str,
        color: discord.Color,
        usuario: discord.Member,
        mod: discord.Member,
        razon: str,
        extra: dict | None = None
    ) -> discord.Embed:
        """Genera un embed estándar para todas las acciones de moderación."""
        embed = discord.Embed(title=titulo, color=color)
        embed.add_field(name="👤 Usuario", value=usuario.mention,  inline=True)
        embed.add_field(name="🛡️ Por",     value=mod.mention,      inline=True)
        embed.add_field(name="📋 Razón",   value=razon,            inline=False)
        if extra:
            for nombre, valor in extra.items():
                embed.add_field(name=nombre, value=valor, inline=True)
        embed.set_footer(text=f"ID: {usuario.id}")
        embed.timestamp = discord.utils.utcnow()
        return embed


    async def _log(self, guild: discord.Guild, embed: discord.Embed):
        """Envía el embed al canal de logs si está configurado."""
        config = await db.get_guild(guild.id)
        if not config or not config.get("log_channel"):
            return
        canal = guild.get_channel(int(config["log_channel"]))
        if canal:
            await canal.send(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /kick
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(name="kick", description="Expulsa a un usuario del servidor")
    @app_commands.describe(
        usuario="Usuario a expulsar",
        razon="Motivo de la expulsión"
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        razon: str = "Sin razón especificada"
    ):
        # Evitamos que alguien expulse a un mod o al propio bot
        if usuario.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "❌ No puedes expulsar a alguien con un rol igual o superior al tuyo.",
                ephemeral=True
            )
            return

        await usuario.kick(reason=razon)

        embed = self._embed_mod(
            "👢 Usuario expulsado", discord.Color.orange(),
            usuario, interaction.user, razon
        )
        await interaction.response.send_message(embed=embed)
        await self._log(interaction.guild, embed)

    @kick.error
    async def kick_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ No tienes permisos para expulsar usuarios.", ephemeral=True
            )


    # ══════════════════════════════════════════════════════════════
    #  /ban
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(name="ban", description="Banea a un usuario del servidor")
    @app_commands.describe(
        usuario="Usuario a banear",
        razon="Motivo del baneo",
        borrar_mensajes="Días de mensajes a borrar (0-7)"
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        razon: str = "Sin razón especificada",
        borrar_mensajes: app_commands.Range[int, 0, 7] = 0
    ):
        if usuario.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "❌ No puedes banear a alguien con un rol igual o superior al tuyo.",
                ephemeral=True
            )
            return

        await usuario.ban(reason=razon, delete_message_days=borrar_mensajes)

        embed = self._embed_mod(
            "🔨 Usuario baneado", discord.Color.red(),
            usuario, interaction.user, razon,
            extra={"🗑️ Mensajes borrados": f"{borrar_mensajes} día(s)"}
        )
        await interaction.response.send_message(embed=embed)
        await self._log(interaction.guild, embed)

    @ban.error
    async def ban_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ No tienes permisos para banear usuarios.", ephemeral=True
            )


    # ══════════════════════════════════════════════════════════════
    #  /mute
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="mute",
        description="Silencia a un usuario temporalmente"
    )
    @app_commands.describe(
        usuario="Usuario a silenciar",
        minutos="Duración en minutos (máx. 40320 = 28 días)",
        razon="Motivo del silencio"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        minutos: app_commands.Range[int, 1, 40320],
        razon: str = "Sin razón especificada"
    ):
        if usuario.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "❌ No puedes silenciar a alguien con un rol igual o superior.",
                ephemeral=True
            )
            return

        from datetime import timedelta
        await usuario.timeout(timedelta(minutes=minutos), reason=razon)

        # Formato legible de duración
        if minutos < 60:
            duracion = f"{minutos} minuto(s)"
        elif minutos < 1440:
            duracion = f"{minutos // 60}h {minutos % 60}m"
        else:
            duracion = f"{minutos // 1440} día(s)"

        embed = self._embed_mod(
            "🔇 Usuario silenciado", discord.Color.yellow(),
            usuario, interaction.user, razon,
            extra={"⏱️ Duración": duracion}
        )
        await interaction.response.send_message(embed=embed)
        await self._log(interaction.guild, embed)

    @mute.error
    async def mute_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ No tienes permisos para silenciar usuarios.", ephemeral=True
            )


    # ══════════════════════════════════════════════════════════════
    #  /unmute
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(name="unmute", description="Quita el silencio a un usuario")
    @app_commands.describe(usuario="Usuario a des-silenciar")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        if not usuario.is_timed_out():
            await interaction.response.send_message(
                f"**{usuario.display_name}** no está silenciado.", ephemeral=True
            )
            return

        await usuario.timeout(None)
        await interaction.response.send_message(
            f"✅ Se quitó el silencio a {usuario.mention}."
        )


    # ══════════════════════════════════════════════════════════════
    #  /warn
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(name="warn", description="Advierte a un usuario")
    @app_commands.describe(
        usuario="Usuario a advertir",
        razon="Motivo de la advertencia"
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        razon: str
    ):
        # Guardamos en BD — persiste entre reinicios
        total = await db.add_warning(
            interaction.guild.id, usuario.id, interaction.user.id, razon
        )

        embed = self._embed_mod(
            "⚠️ Advertencia", discord.Color.yellow(),
            usuario, interaction.user, razon,
            extra={"📊 Total warns": f"{total} / 3"}
        )
        await interaction.response.send_message(embed=embed)
        await self._log(interaction.guild, embed)

        # Acción automática al llegar a 3 warns
        if total >= 3:
            try:
                await usuario.kick(reason="3 advertencias acumuladas")
                await db.clear_warnings(interaction.guild.id, usuario.id)
                embed_kick = discord.Embed(
                    description=(
                        f"👢 {usuario.mention} fue expulsado automáticamente "
                        f"por acumular **3 advertencias**."
                    ),
                    color=discord.Color.red()
                )
                await interaction.channel.send(embed=embed_kick)
                await self._log(interaction.guild, embed_kick)
            except discord.Forbidden:
                await interaction.channel.send(
                    f"⚠️ {usuario.mention} acumuló 3 advertencias pero no pude expulsarlo "
                    f"(sin permisos o rol superior al bot)."
                )

    @warn.error
    async def warn_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ No tienes permisos para advertir usuarios.", ephemeral=True
            )


    # ══════════════════════════════════════════════════════════════
    #  /warns <usuario>
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="warns",
        description="Muestra el historial de advertencias de un usuario"
    )
    @app_commands.describe(usuario="Usuario a consultar")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warns(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        lista = await db.get_warnings(interaction.guild.id, usuario.id)

        if not lista:
            await interaction.response.send_message(
                f"✅ **{usuario.display_name}** no tiene advertencias.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"⚠️ Advertencias de {usuario.display_name}",
            color=discord.Color.yellow()
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)

        for i, w in enumerate(lista, 1):
            # Convertimos el timestamp a fecha legible
            fecha = f"<t:{w['created_at']}:R>"   # formato relativo de Discord
            mod   = interaction.guild.get_member(int(w["mod_id"]))
            mod_nombre = mod.display_name if mod else f"ID {w['mod_id']}"
            embed.add_field(
                name=f"Warn #{i} — {fecha}",
                value=f"**Razón:** {w['reason']}\n**Mod:** {mod_nombre}",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


    # ══════════════════════════════════════════════════════════════
    #  /unwarn <usuario>
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="unwarn",
        description="Borra todas las advertencias de un usuario"
    )
    @app_commands.describe(usuario="Usuario al que limpiar los warns")
    @app_commands.checks.has_permissions(kick_members=True)
    async def unwarn(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        total = await db.count_warnings(interaction.guild.id, usuario.id)

        if total == 0:
            await interaction.response.send_message(
                f"**{usuario.display_name}** no tiene advertencias que borrar.",
                ephemeral=True
            )
            return

        await db.clear_warnings(interaction.guild.id, usuario.id)
        await interaction.response.send_message(
            f"✅ Se borraron **{total}** advertencia(s) de {usuario.mention}."
        )


    # ══════════════════════════════════════════════════════════════
    #  EVENTO — mensaje eliminado
    # ══════════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        contenido = message.content or "*[Contenido no disponible — mensaje no estaba en caché]*"

        embed = discord.Embed(title="🗑️ Mensaje eliminado", color=discord.Color.red())
        embed.add_field(name="👤 Autor",     value=message.author.mention,  inline=True)
        embed.add_field(name="📍 Canal",     value=message.channel.mention, inline=True)
        embed.add_field(name="💬 Contenido", value=contenido[:1024],        inline=False)

        if message.attachments:
            nombres = "\n".join(a.filename for a in message.attachments)
            embed.add_field(name="📎 Adjuntos", value=nombres, inline=False)

        embed.set_footer(text=f"ID mensaje: {message.id} | ID usuario: {message.author.id}")
        embed.timestamp = discord.utils.utcnow()

        await self._log(message.guild, embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list[discord.Message]):
        if not messages:
            return
        guild = messages[0].guild
        canal = messages[0].channel

        embed = discord.Embed(
            title="🗑️ Purge de mensajes",
            description=f"Se eliminaron **{len(messages)} mensajes** en {canal.mention}",
            color=discord.Color.dark_red()
        )
        embed.timestamp = discord.utils.utcnow()
        await self._log(guild, embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderacion(bot))