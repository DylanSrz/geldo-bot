import discord
from discord import app_commands
from discord.ext import commands
import aiohttp


class Pokemon(commands.Cog):
    """Comandos relacionados con Pokémon usando la PokéAPI."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()


    # ══════════════════════════════════════════════════════════════
    #  /poke <nombre>
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="poke",
        description="Muestra información y sprite de un Pokémon"
    )
    @app_commands.describe(pokemon="Nombre o número del Pokémon, ej: pikachu o 25")
    async def poke(self, interaction: discord.Interaction, pokemon: str):
        await interaction.response.defer()

        nombre = pokemon.strip().lower()
        url    = f"https://pokeapi.co/api/v2/pokemon/{nombre}"

        async with self.session.get(url) as resp:
            if resp.status == 404:
                await interaction.followup.send(
                    f"❌ No encontré el Pokémon **{pokemon}**. "
                    f"Verifica el nombre o número.",
                    ephemeral=True
                )
                return

            if resp.status != 200:
                await interaction.followup.send(
                    "❌ Error al conectar con la PokéAPI. Intenta más tarde.",
                    ephemeral=True
                )
                return

            data = await resp.json()

        # ── Extraemos los datos ────────────────────────────────────
        nombre_oficial = data["name"].capitalize()
        numero         = data["id"]
        altura         = data["height"] / 10        # decímetros → metros
        peso           = data["weight"] / 10        # hectogramos → kg
        tipos          = " / ".join(
            t["type"]["name"].capitalize()
            for t in data["types"]
        )
        habilidades    = ", ".join(
            a["ability"]["name"].capitalize()
            for a in data["abilities"]
            if not a["is_hidden"]           # solo habilidades normales
        )
        habilidad_oculta = next(
            (a["ability"]["name"].capitalize()
             for a in data["abilities"] if a["is_hidden"]),
            "Ninguna"
        )

        # Stats base
        stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
        barra_hp = "🟥" * (stats.get("hp", 0) // 20)

        # Sprite oficial
        sprite = (
            data["sprites"]["other"]["official-artwork"]["front_default"]
            or data["sprites"]["front_default"]
        )

        embed = discord.Embed(
            title=f"#{numero} — {nombre_oficial}",
            color=discord.Color.red()
        )
        embed.set_image(url=sprite)
        embed.add_field(name="🏷️ Tipo",             value=tipos,            inline=True)
        embed.add_field(name="📏 Altura",            value=f"{altura} m",   inline=True)
        embed.add_field(name="⚖️ Peso",              value=f"{peso} kg",    inline=True)
        embed.add_field(name="✨ Habilidades",        value=habilidades,     inline=True)
        embed.add_field(name="🔮 Hab. oculta",       value=habilidad_oculta,inline=True)
        embed.add_field(
            name="❤️ HP base",
            value=f"{stats.get('hp', '?')} {barra_hp}",
            inline=False
        )
        embed.add_field(name="⚔️ Ataque",   value=str(stats.get("attack", "?")),          inline=True)
        embed.add_field(name="🛡️ Defensa",  value=str(stats.get("defense", "?")),         inline=True)
        embed.add_field(name="💨 Velocidad", value=str(stats.get("speed", "?")),           inline=True)
        embed.set_footer(text="Datos de PokéAPI • pokeapi.co")

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Pokemon(bot))