import discord
from discord import app_commands
from discord.ext import commands
from utils import db


class Niveles(commands.Cog):
    """Sistema de XP y niveles por servidor."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot


    # ══════════════════════════════════════════════════════════════
    #  EVENTO — XP por mensaje
    # ══════════════════════════════════════════════════════════════

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignoramos bots y mensajes fuera de servidores
        if message.author.bot or not message.guild:
            return

        resultado = await db.add_xp(message.guild.id, message.author.id)

        if resultado["subio_nivel"]:
            embed = discord.Embed(
                description=(
                    f"🎉 {message.author.mention} subió al "
                    f"**nivel {resultado['nivel']}** ⭐"
                ),
                color=discord.Color.gold()
            )
            await message.channel.send(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /nivel [usuario]
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="nivel",
        description="Muestra el nivel y XP de un usuario"
    )
    @app_commands.describe(usuario="Usuario a consultar (deja vacío para verte a ti)")
    async def nivel(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member | None = None
    ):
        objetivo = usuario or interaction.user
        datos    = await db.get_user_level(interaction.guild.id, objetivo.id)

        if not datos:
            await interaction.response.send_message(
                f"**{objetivo.display_name}** aún no tiene XP. "
                f"¡Empieza a chatear! 💬",
                ephemeral=True
            )
            return

        xp        = datos["xp"]
        nivel     = datos["nivel"]
        xp_meta   = nivel * 100
        progreso  = int((xp / xp_meta) * 10)
        barra     = "🟩" * progreso + "⬛" * (10 - progreso)

        embed = discord.Embed(
            title=f"⭐ Nivel de {objetivo.display_name}",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=objetivo.display_avatar.url)
        embed.add_field(name="🏆 Nivel",    value=str(nivel),              inline=True)
        embed.add_field(name="✨ XP",       value=f"{xp} / {xp_meta}",    inline=True)
        embed.add_field(name="📊 Progreso", value=barra,                   inline=False)
        await interaction.response.send_message(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /ranking
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="ranking",
        description="Top 5 usuarios con más nivel en este servidor"
    )
    async def ranking(self, interaction: discord.Interaction):
        await interaction.response.defer()

        top = await db.get_leaderboard(interaction.guild.id, limit=5)

        if not top:
            await interaction.followup.send(
                "❌ Aún no hay datos de XP en este servidor.",
                ephemeral=True
            )
            return

        medallas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        embed    = discord.Embed(
            title="🏆 Ranking de niveles",
            color=discord.Color.gold()
        )

        for i, entrada in enumerate(top):
            miembro = interaction.guild.get_member(int(entrada["user_id"]))
            nombre  = miembro.display_name if miembro else "Usuario desconocido"
            embed.add_field(
                name=f"{medallas[i]} {nombre}",
                value=f"Nivel **{entrada['nivel']}** • {entrada['xp']} XP",
                inline=False
            )

        await interaction.followup.send(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /darxp <usuario> <cantidad>  — solo admins
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="darxp",
        description="Da XP manualmente a un usuario (solo administradores)"
    )
    @app_commands.describe(
        usuario="Usuario que recibirá el XP",
        cantidad="Cantidad de XP a dar"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def darxp(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        cantidad: int
    ):
        if cantidad <= 0:
            await interaction.response.send_message(
                "La cantidad debe ser mayor que 0.", ephemeral=True
            )
            return

        import aiosqlite

        async with aiosqlite.connect(db.DB_PATH) as conn:
            conn.row_factory = aiosqlite.Row
            await conn.execute(
                "INSERT OR IGNORE INTO levels (guild_id, user_id) VALUES (?, ?)",
                (str(interaction.guild.id), str(usuario.id))
            )
            async with conn.execute(
                "SELECT xp, nivel FROM levels WHERE guild_id = ? AND user_id = ?",
                (str(interaction.guild.id), str(usuario.id))
            ) as cursor:
                datos = dict(await cursor.fetchone())

            nuevo_xp = datos["xp"] + cantidad
            nivel = datos["nivel"]

            # Recalcular niveles si el XP supera el umbral
            while nuevo_xp >= nivel * 100:
                nuevo_xp -= nivel * 100
                nivel += 1

            await conn.execute(
                "UPDATE levels SET xp = ?, nivel = ? WHERE guild_id = ? AND user_id = ?",
                (nuevo_xp, nivel, str(interaction.guild.id), str(usuario.id))
            )
            await conn.commit()

        await interaction.response.send_message(
            f"✅ Se le dieron **{cantidad} XP** a {usuario.mention}. "
            f"Ahora tiene {nuevo_xp} XP (nivel {nivel})."
        )

    @darxp.error
    async def darxp_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Solo los administradores pueden usar este comando.",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(Niveles(bot))