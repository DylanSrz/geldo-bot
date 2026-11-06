import discord
from discord import app_commands
from discord.ext import commands
from utils import db
import aiosqlite
import datetime
import time


# ══════════════════════════════════════════════════════════════════
#  VIEWS PERSISTENTES
#  Estas clases se registran al arrancar el bot para que los botones
#  sigan funcionando aunque el bot se reinicie.
# ══════════════════════════════════════════════════════════════════

class BotonAbrirTicket(discord.ui.View):
    """Botón permanente que aparece en el canal de tickets."""

    def __init__(self):
        # timeout=None → el botón nunca expira
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Abrir ticket",
        style=discord.ButtonStyle.primary,
        emoji="🎫",
        custom_id="ticket:abrir"   # ID fijo para persistencia entre reinicios
    )
    async def abrir_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True)

        guild  = interaction.guild
        usuario = interaction.user

        # Verificamos si el usuario ya tiene un ticket abierto
        async with aiosqlite.connect(db.DB_PATH) as conn:
            async with conn.execute("""
                SELECT channel_id FROM tickets
                WHERE guild_id = ? AND user_id = ? AND status = 'open'
            """, (str(guild.id), str(usuario.id))) as cursor:
                existente = await cursor.fetchone()

        if existente:
            canal_existente = guild.get_channel(int(existente[0]))
            if canal_existente:
                await interaction.followup.send(
                    f"❌ Ya tienes un ticket abierto: {canal_existente.mention}",
                    ephemeral=True
                )
                return

        # Leemos la configuración del servidor para el rol de soporte
        config   = await db.get_guild(guild.id)
        rol_id   = config.get("staff_role") if config else None
        rol_staff = guild.get_role(int(rol_id)) if rol_id else None

        # ── Creamos el canal privado del ticket ────────────────────
        # Permisos base: nadie puede ver el canal
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            usuario: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True
            )
        }

        # Rol de staff puede ver todos los tickets (los admins bypasean por permiso)
        if rol_staff:
            overwrites[rol_staff] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            )

        # Buscamos o creamos la categoría "Tickets"
        categoria = discord.utils.get(guild.categories, name="Tickets")
        if not categoria:
            categoria = await guild.create_category("Tickets")

        nombre_canal = f"ticket-{usuario.display_name.lower().replace(' ', '-')}"
        canal = await guild.create_text_channel(
            name=nombre_canal,
            category=categoria,
            overwrites=overwrites,
            topic=f"Ticket de {usuario} · Abierto el {discord.utils.utcnow().strftime('%d/%m/%Y %H:%M')}"
        )

        # Guardamos en la BD
        async with aiosqlite.connect(db.DB_PATH) as conn:
            await conn.execute("""
                INSERT INTO tickets (guild_id, user_id, channel_id, status, opened_at)
                VALUES (?, ?, ?, 'open', ?)
            """, (str(guild.id), str(usuario.id), str(canal.id), int(time.time())))
            await conn.commit()

        # ── Mensaje de bienvenida dentro del ticket ────────────────
        embed = discord.Embed(
            title=f"🎫 Ticket de {usuario.display_name}",
            description=(
                f"Hola {usuario.mention}, bienvenido a tu ticket.\n"
                f"Describe tu problema o consulta y el equipo de soporte "
                f"te atenderá lo antes posible."
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(
            text="Cuando se resuelva tu problema, presiona Cerrar ticket."
        )
        embed.timestamp = discord.utils.utcnow()

        await canal.send(
            content=f"{usuario.mention}" + (f" | {rol_staff.mention}" if rol_staff else ""),
            embed=embed,
            view=BotonCerrarTicket()
        )

        await interaction.followup.send(
            f"✅ Tu ticket fue creado: {canal.mention}",
            ephemeral=True
        )


class BotonCerrarTicket(discord.ui.View):
    """Botón para cerrar el ticket dentro del canal."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Cerrar ticket",
        style=discord.ButtonStyle.danger,
        emoji="🔒",
        custom_id="ticket:cerrar"
    )
    async def cerrar_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        canal  = interaction.channel
        guild  = interaction.guild
        usuario = interaction.user

        # Solo el dueño del ticket, admins o staff pueden cerrarlo
        es_admin = usuario.guild_permissions.administrator
        config   = await db.get_guild(guild.id)
        rol_id   = config.get("staff_role") if config else None
        rol_staff = guild.get_role(int(rol_id)) if rol_id else None
        es_staff  = rol_staff in usuario.roles if rol_staff else False

        # Verificamos si el usuario es el dueño del ticket
        async with aiosqlite.connect(db.DB_PATH) as conn:
            async with conn.execute("""
                SELECT user_id FROM tickets
                WHERE channel_id = ? AND status = 'open'
            """, (str(canal.id),)) as cursor:
                ticket = await cursor.fetchone()

        es_dueno = ticket and str(usuario.id) == ticket[0]

        if not (es_admin or es_staff or es_dueno):
            await interaction.response.send_message(
                "❌ No tienes permiso para cerrar este ticket.",
                ephemeral=True
            )
            return

        # Confirmación antes de cerrar
        await interaction.response.send_message(
            embed=discord.Embed(
                description="🔒 Cerrando ticket en 5 segundos...",
                color=discord.Color.red()
            )
        )

        # Actualizamos el estado en la BD
        async with aiosqlite.connect(db.DB_PATH) as conn:
            await conn.execute("""
                UPDATE tickets
                SET status = 'closed', closed_at = ?
                WHERE channel_id = ?
            """, (int(time.time()), str(canal.id)))
            await conn.commit()

        # Esperamos y borramos el canal
        await discord.utils.sleep_until(
            discord.utils.utcnow() + datetime.timedelta(seconds=5)
        )
        await canal.delete(reason=f"Ticket cerrado por {usuario}")


# ══════════════════════════════════════════════════════════════════
#  COG
# ══════════════════════════════════════════════════════════════════

class Tickets(commands.Cog):
    """Sistema de tickets de soporte con botones."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # Registramos las views persistentes para que los botones
        # sigan funcionando después de un reinicio del bot
        self.bot.add_view(BotonAbrirTicket())
        self.bot.add_view(BotonCerrarTicket())


    # ══════════════════════════════════════════════════════════════
    #  /setuptickets <canal> [rol_staff]
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="setuptickets",
        description="Envía el panel de tickets a un canal"
    )
    @app_commands.describe(
        canal="Canal donde aparecerá el botón de tickets",
        rol_staff="Rol que podrá ver y responder tickets (opcional)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setuptickets(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel,
        rol_staff: discord.Role | None = None
    ):
        await db.ensure_guild(interaction.guild.id)

        # Guardamos el rol de staff en la BD (reutilizamos el campo staff_role
        # o puedes agregar un campo staff_role — ver nota abajo)
        if rol_staff:
            await db.set_guild_config(
                interaction.guild.id, "staff_role", str(rol_staff.id)
            )

        embed = discord.Embed(
            title="🎫 Sistema de tickets",
            description=(
                "¿Necesitas ayuda o tienes alguna consulta?\n\n"
                "Presiona el botón de abajo para abrir un ticket privado "
                "con el equipo de soporte.\n\n"
                "📌 Solo puedes tener **un ticket abierto** a la vez."
            ),
            color=discord.Color.blue()
        )
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(text=interaction.guild.name)

        await canal.send(embed=embed, view=BotonAbrirTicket())

        await interaction.response.send_message(
            f"✅ Panel de tickets enviado a {canal.mention}.",
            ephemeral=True
        )

    @setuptickets.error
    async def setuptickets_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Solo los administradores pueden configurar los tickets.",
                ephemeral=True
            )


    # ══════════════════════════════════════════════════════════════
    #  /cerrarticket — alternativa por comando
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="cerrarticket",
        description="Cierra el ticket del canal actual"
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def cerrarticket(self, interaction: discord.Interaction):
        canal = interaction.channel

        async with aiosqlite.connect(db.DB_PATH) as conn:
            async with conn.execute("""
                SELECT user_id FROM tickets
                WHERE channel_id = ? AND status = 'open'
            """, (str(canal.id),)) as cursor:
                ticket = await cursor.fetchone()

        if not ticket:
            await interaction.response.send_message(
                "❌ Este canal no es un ticket activo.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=discord.Embed(
                description="🔒 Cerrando ticket en 5 segundos...",
                color=discord.Color.red()
            )
        )

        async with aiosqlite.connect(db.DB_PATH) as conn:
            await conn.execute("""
                UPDATE tickets
                SET status = 'closed', closed_at = ?
                WHERE channel_id = ?
            """, (int(time.time()), str(canal.id)))
            await conn.commit()

        await discord.utils.sleep_until(
            discord.utils.utcnow() + datetime.timedelta(seconds=5)
        )
        await canal.delete(reason=f"Ticket cerrado por {interaction.user}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Tickets(bot))