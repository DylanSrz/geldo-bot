import discord
from discord import app_commands
from discord.ext import commands
from utils import db


class Bienvenida(commands.Cog):
    """Bienvenida automática y configuración del sistema de entrada/salida."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Cache de invitaciones: { guild_id: { invite_code: uses } }
        self._invite_cache: dict[int, dict[str, int]] = {}

    # ══════════════════════════════════════════════════════════════
    #  HELPERS — caché de invitaciones
    # ══════════════════════════════════════════════════════════════

    async def _find_inviter(
        self, guild: discord.Guild
    ) -> tuple[discord.Member | None, str | None]:
        """
        Compara el snapshot guardado con el estado actual de las invitaciones.
        Devuelve (inviter, invite_code) de la invitación que aumentó su contador.
        Si no se puede determinar, devuelve (None, None).
        """
        old = self._invite_cache.get(guild.id, {})

        try:
            new_invites = await guild.invites()
        except discord.Forbidden:
            return None, None

        new = {inv.code: inv.uses for inv in new_invites}
        self._invite_cache[guild.id] = new

        for inv in new_invites:
            if inv.uses > old.get(inv.code, 0) and inv.inviter:
                return inv.inviter, inv.code

        return None, None

    # ══════════════════════════════════════════════════════════════
    #  on_ready — precargamos invitaciones de todos los servidores
    # ══════════════════════════════════════════════════════════════

    async def _cargar_invites(self, guild: discord.Guild):
        try:
            invites = await guild.invites()
            self._invite_cache[guild.id] = {inv.code: inv.uses for inv in invites}
        except discord.Forbidden:
            self._invite_cache[guild.id] = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self._cargar_invites(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self._cargar_invites(guild)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite):
        if invite.guild:
            self._invite_cache.setdefault(invite.guild.id, {})[invite.code] = (
                invite.uses or 0
            )

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite):
        if invite.guild:
            self._invite_cache.get(invite.guild.id, {}).pop(invite.code, None)

    # ══════════════════════════════════════════════════════════════
    #  EVENTO — nuevo miembro
    # ══════════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild

        await db.ensure_guild(guild.id)
        config = await db.get_guild(guild.id)

        # ── Detectamos al invitador ────────────────────────────────
        inviter, inv_code = await self._find_inviter(guild)

        # ── Guardamos en la BD para consultas futuras ──────────────
        await db.save_invite(
            guild_id=guild.id,
            user_id=member.id,
            inviter_id=inviter.id if inviter else None,
            invite_code=inv_code,
        )

        # ── Mensaje en canal de bienvenida ─────────────────────────
        canal_id = config.get("welcome_channel") if config else None

        if canal_id:
            canal = guild.get_channel(int(canal_id))
            if canal:
                mensaje = config.get("welcome_message") or (
                    f"¡Esperamos que disfrutes tu estadía en " f"**{guild.name}**! 🎉"
                )
                mensaje = (
                    mensaje.replace("{usuario}", member.mention)
                    .replace("{nombre}", member.display_name)
                    .replace("{servidor}", guild.name)
                    .replace("{miembros}", str(guild.member_count))
                )

                embed = discord.Embed(
                    title=f"👋 ¡Bienvenido/a, {member.display_name}!",
                    description=mensaje,
                    color=discord.Color.green(),
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.add_field(
                    name="📊 Miembros",
                    value=f"Eres el miembro número **{guild.member_count}**",
                    inline=False,
                )
                embed.set_footer(
                    text=f"Cuenta creada: {member.created_at.strftime('%d/%m/%Y')}"
                )
                await canal.send(embed=embed)

        # ── DM al nuevo miembro ────────────────────────────────────
        try:
            embed_dm = discord.Embed(
                title=f"👋 ¡Hola, {member.display_name}!",
                description=(
                    f"Bienvenido/a a **{guild.name}**.\n"
                    f"¡Esperamos que la pases genial! 🎉"
                ),
                color=discord.Color.blurple(),
            )
            embed_dm.set_thumbnail(url=guild.icon.url if guild.icon else None)
            await member.send(embed=embed_dm)
        except discord.Forbidden:
            pass

        # ── Log de entrada en canal de logs ───────────────────────
        log_id = config.get("log_channel") if config else None
        if not log_id:
            return

        log_canal = guild.get_channel(int(log_id))
        if not log_canal:
            return

        embed_log = discord.Embed(
            title="📥 Nuevo miembro",
            description=f"{member.mention} (**{member.display_name}**) se unió al servidor.",
            color=discord.Color.green(),
        )
        embed_log.set_thumbnail(url=member.display_avatar.url)
        embed_log.add_field(
            name="📊 Miembros ahora", value=str(guild.member_count), inline=True
        )
        embed_log.add_field(
            name="📅 Cuenta creada",
            value=f"<t:{int(member.created_at.timestamp())}:R>",
            inline=True,
        )

        if inviter:
            embed_log.add_field(
                name="✉️ Invitado por",
                value=f"{inviter.mention} (`{inviter}`) · código `{inv_code}`",
                inline=False,
            )
        else:
            embed_log.add_field(
                name="✉️ Invitado por",
                value="Invitador es desconocido (vanity URL o invitación no rastreable)",
                inline=False,
            )

        embed_log.set_footer(text=f"ID: {member.id}")
        embed_log.timestamp = discord.utils.utcnow()
        await log_canal.send(embed=embed_log)

    # ══════════════════════════════════════════════════════════════
    #  EVENTO — miembro sale del servidor
    # ══════════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        config = await db.get_guild(member.guild.id)
        canal_id = config.get("log_channel") if config else None

        if not canal_id:
            return

        canal = member.guild.get_channel(int(canal_id))
        if not canal:
            return

        # Recuperamos de la BD quién lo invitó originalmente
        invite_info = await db.get_invite_info(member.guild.id, member.id)

        embed = discord.Embed(
            title="📤 Miembro salió",
            description=f"{member.mention} (**{member.display_name}**) salió del servidor.",
            color=discord.Color.red(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(
            name="📊 Miembros ahora", value=str(member.guild.member_count), inline=True
        )

        # Roles que tenía al salir
        roles = [r.mention for r in member.roles[1:]]
        embed.add_field(
            name="🎭 Roles que tenía",
            value=", ".join(roles) if roles else "Ninguno",
            inline=False,
        )

        # Mostramos quién lo invitó originalmente
        if invite_info and invite_info.get("inviter_id"):
            inviter_obj = member.guild.get_member(int(invite_info["inviter_id"]))
            inviter_texto = (
                inviter_obj.mention
                if inviter_obj
                else f"ID {invite_info['inviter_id']}"
            )
            embed.add_field(
                name="✉️ Fue invitado por", value=inviter_texto, inline=False
            )

        embed.set_footer(text=f"ID: {member.id}")
        embed.timestamp = discord.utils.utcnow()
        await canal.send(embed=embed)

    # ══════════════════════════════════════════════════════════════
    #  /invitaciones <usuario>
    #  Solo accesible para el rol de staff configurado en el servidor
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="invitaciones",
        description="Muestra quién invitó a un usuario y a quiénes ha invitado él",
    )
    @app_commands.describe(usuario="Usuario a consultar")
    async def invitaciones(
        self, interaction: discord.Interaction, usuario: discord.Member
    ):
        # ── Verificamos si quien ejecuta el comando es staff o admin ─
        config = await db.get_guild(interaction.guild.id)
        rol_id = config.get("staff_role") if config else None
        rol_staff = interaction.guild.get_role(int(rol_id)) if rol_id else None

        es_admin = interaction.user.guild_permissions.administrator
        es_staff = rol_staff in interaction.user.roles if rol_staff else False

        if not (es_admin or es_staff):
            await interaction.response.send_message(
                "❌ Solo el staff del servidor puede usar este comando.", ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        # ── Quién invitó a este usuario ────────────────────────────
        invite_info = await db.get_invite_info(interaction.guild.id, usuario.id)

        embed = discord.Embed(
            title=f"✉️ Invitaciones — {usuario.display_name}",
            color=discord.Color.blurple(),
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)

        if invite_info and invite_info.get("inviter_id"):
            inviter_obj = interaction.guild.get_member(int(invite_info["inviter_id"]))
            inviter_texto = (
                inviter_obj.mention
                if inviter_obj
                else f"ID {invite_info['inviter_id']}"
            )
            codigo = invite_info.get("invite_code") or "desconocido"
            fecha = f"<t:{invite_info['joined_at']}:F>"
            embed.add_field(
                name="📥 Fue invitado por",
                value=f"{inviter_texto} · código `{codigo}` · {fecha}",
                inline=False,
            )
        else:
            embed.add_field(
                name="📥 Fue invitado por",
                value="Desconocido (entró antes de que el bot rastreara invitaciones, "
                "o por vanity URL)",
                inline=False,
            )

        # ── A quiénes ha invitado este usuario ─────────────────────
        invitados = await db.get_invited_by(interaction.guild.id, usuario.id)

        if invitados:
            lineas = []
            for entrada in invitados[:10]:  # máximo 10 para no saturar el embed
                miembro = interaction.guild.get_member(int(entrada["user_id"]))
                nombre = miembro.mention if miembro else f"ID {entrada['user_id']}"
                fecha = f"<t:{entrada['joined_at']}:R>"
                lineas.append(f"• {nombre} — {fecha}")

            embed.add_field(
                name=f"📤 Ha invitado a ({len(invitados)} en total)",
                value="\n".join(lineas),
                inline=False,
            )
        else:
            embed.add_field(
                name="📤 Ha invitado a", value="Nadie registrado aún.", inline=False
            )

        embed.set_footer(text=f"ID: {usuario.id}")
        embed.timestamp = discord.utils.utcnow()
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Bienvenida(bot))
