import discord
from discord import app_commands
from discord.ext import commands
from utils import db
import aiosqlite
import time


class Economia(commands.Cog):
    """Sistema de economía virtual por servidor."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    # ══════════════════════════════════════════════════════════════
    #  /balance [usuario]
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="balance",
        description="Muestra tu balance de monedas o el de otro usuario"
    )
    @app_commands.describe(usuario="Usuario a consultar (deja vacío para verte a ti)")
    async def balance(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member | None = None
    ):
        objetivo = usuario or interaction.user
        eco      = await db.get_economy(interaction.guild.id, objetivo.id)

        ahora     = int(time.time())
        siguiente = eco["last_daily"] + db.DAILY_COOLDOWN

        if ahora >= siguiente:
            estado_daily = "✅ Disponible ahora"
        else:
            estado_daily = f"<t:{siguiente}:R>"

        embed = discord.Embed(
            title=f"💰 Balance de {objetivo.display_name}",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=objetivo.display_avatar.url)
        embed.add_field(
            name="🪙 Monedas actuales",
            value=f"**{eco['coins']:,}**",
            inline=True
        )
        embed.add_field(
            name="📈 Total ganado",
            value=f"{eco['total_earned']:,}",
            inline=True
        )
        embed.add_field(
            name="🎁 Próximo /daily",
            value=estado_daily,
            inline=False
        )
        embed.set_footer(text=f"Economía de {interaction.guild.name}")
        await interaction.response.send_message(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /daily
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="daily",
        description="Reclama tus monedas diarias"
    )
    async def daily(self, interaction: discord.Interaction):
        resultado = await db.claim_daily(interaction.guild.id, interaction.user.id)

        if not resultado["exito"]:
            siguiente = int(time.time()) + resultado["segundos_restantes"]
            embed = discord.Embed(
                description=(
                    f"⏳ Ya reclamaste tu daily hoy.\n"
                    f"Vuelve <t:{siguiente}:R>."
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="🎁 ¡Daily reclamado!",
            description=(
                f"{interaction.user.mention} recibió "
                f"**{db.DAILY_COINS:,} 🪙**\n"
                f"Balance actual: **{resultado['coins']:,} 🪙**"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="Vuelve mañana para reclamar de nuevo")
        await interaction.response.send_message(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /transferir <usuario> <cantidad>
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="transferir",
        description="Transfiere monedas a otro usuario"
    )
    @app_commands.describe(
        usuario="Usuario que recibirá las monedas",
        cantidad="Cantidad a transferir"
    )
    async def transferir(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        cantidad: int
    ):
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ No puedes transferirte monedas a ti mismo.",
                ephemeral=True
            )
            return

        if usuario.bot:
            await interaction.response.send_message(
                "❌ No puedes transferir monedas a un bot.",
                ephemeral=True
            )
            return

        if cantidad <= 0:
            await interaction.response.send_message(
                "❌ La cantidad debe ser mayor que 0.",
                ephemeral=True
            )
            return

        eco_origen = await db.get_economy(interaction.guild.id, interaction.user.id)

        if eco_origen["coins"] < cantidad:
            await interaction.response.send_message(
                f"❌ No tienes suficientes monedas. "
                f"Tienes **{eco_origen['coins']:,} 🪙**",
                ephemeral=True
            )
            return

        # Restamos al origen y sumamos al destino
        await db.add_coins(interaction.guild.id, interaction.user.id, -cantidad)
        await db.add_coins(interaction.guild.id, usuario.id, cantidad)

        eco_origen  = await db.get_economy(interaction.guild.id, interaction.user.id)
        eco_destino = await db.get_economy(interaction.guild.id, usuario.id)

        embed = discord.Embed(
            title="💸 Transferencia exitosa",
            color=discord.Color.green()
        )
        embed.add_field(
            name="📤 Enviaste",
            value=f"**{cantidad:,} 🪙** a {usuario.mention}",
            inline=False
        )
        embed.add_field(
            name="💰 Tu nuevo balance",
            value=f"{eco_origen['coins']:,} 🪙",
            inline=True
        )
        embed.add_field(
            name=f"💰 Balance de {usuario.display_name}",
            value=f"{eco_destino['coins']:,} 🪙",
            inline=True
        )
        await interaction.response.send_message(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /top
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="top",
        description="Muestra el ranking de los usuarios más ricos del servidor"
    )
    async def top(self, interaction: discord.Interaction):
        await interaction.response.defer()

        async with aiosqlite.connect(db.DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute("""
                SELECT user_id, coins, total_earned
                FROM economy
                WHERE guild_id = ?
                ORDER BY coins DESC
                LIMIT 10
            """, (str(interaction.guild.id),)) as cursor:
                rows = await cursor.fetchall()
                ranking = [dict(r) for r in rows]

        if not ranking:
            await interaction.followup.send(
                "❌ Aún no hay datos de economía en este servidor.",
                ephemeral=True
            )
            return

        medallas    = ["🥇", "🥈", "🥉"]
        descripcion = ""

        for i, entrada in enumerate(ranking):
            miembro = interaction.guild.get_member(int(entrada["user_id"]))
            nombre  = miembro.display_name if miembro else f"Usuario desconocido"
            medalla = medallas[i] if i < 3 else f"`{i+1}.`"
            descripcion += f"{medalla} **{nombre}** — {entrada['coins']:,} 🪙\n"

        embed = discord.Embed(
            title=f"🏆 Ranking de economía — {interaction.guild.name}",
            description=descripcion,
            color=discord.Color.gold()
        )
        embed.set_footer(text="Top 10 usuarios con más monedas")
        await interaction.followup.send(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /darmonedas <usuario> <cantidad> — solo admins
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="darmonedas",
        description="Da o quita monedas a un usuario (solo administradores)"
    )
    @app_commands.describe(
        usuario="Usuario objetivo",
        cantidad="Cantidad (negativo para quitar)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def darmonedas(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        cantidad: int
    ):
        if cantidad == 0:
            await interaction.response.send_message(
                "❌ La cantidad no puede ser 0.", ephemeral=True
            )
            return

        await db.add_coins(interaction.guild.id, usuario.id, cantidad)
        eco = await db.get_economy(interaction.guild.id, usuario.id)

        accion = "dieron" if cantidad > 0 else "quitaron"
        embed  = discord.Embed(
            description=(
                f"✅ Se le {accion} **{abs(cantidad):,} 🪙** "
                f"a {usuario.mention}.\n"
                f"Balance actual: **{eco['coins']:,} 🪙**"
            ),
            color=discord.Color.green() if cantidad > 0 else discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

    @darmonedas.error
    async def darmonedas_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Solo los administradores pueden usar este comando.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Economia(bot))