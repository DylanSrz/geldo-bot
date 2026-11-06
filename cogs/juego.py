import discord
from discord import app_commands
from discord.ext import commands
import aiohttp

API_URL_ACACIAS = "https://api.muacacias.net/DiscordStats"


class Juego(commands.Cog):
    """Comandos del servidor de juego MU Acacias."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()

    # ══════════════════════════════════════════════════════════════
    #  /estado
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="estado", description="Muestra el estado actual del servidor MU Acacias"
    )
    async def estado(self, interaction: discord.Interaction):
        await interaction.response.defer()

        async with self.session.get(
            API_URL_ACACIAS, timeout=aiohttp.ClientTimeout(total=5)
        ) as resp:
            if resp.status != 200:
                await interaction.followup.send(
                    "❌ No se pudo conectar con el servidor del juego.", ephemeral=True
                )
                return
            datos = await resp.json()

        embed = discord.Embed(
            title="📊 Estado del servidor MU Acacias", color=discord.Color.green()
        )
        embed.add_field(
            name="👑 Dueño Castle Siege", value=datos.get("CsOwner", "N/A"), inline=True
        )
        embed.add_field(
            name="🛡️ Master Guild", value=datos.get("GuildO", "N/A"), inline=True
        )
        embed.add_field(
            name="🟢 Jugadores online", value=datos.get("Online", "N/A"), inline=True
        )
        embed.set_footer(text="Datos de api.muacacias.net")
        embed.timestamp = discord.utils.utcnow()

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Juego(bot))
