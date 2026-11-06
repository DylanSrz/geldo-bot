import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import random


class Diversion(commands.Cog):
    """Comandos de entretenimiento: memes, chistes, dados, trivia."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()


    # ══════════════════════════════════════════════════════════════
    #  /meme
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(name="meme", description="Trae un meme aleatorio")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer()

        subs = ["memes", "dankmemes", "LatinoPeopleTwitter"]
        sub  = random.choice(subs)

        async with self.session.get(
            f"https://meme-api.com/gimme/{sub}"
        ) as resp:
            if resp.status != 200:
                await interaction.followup.send(
                    "❌ No pude obtener un meme ahora. Intenta más tarde.",
                    ephemeral=True
                )
                return
            data = await resp.json()

        # La API a veces devuelve posts NSFW — los filtramos
        if data.get("nsfw", False):
            await interaction.followup.send(
                "⚠️ El meme obtenido era inapropiado, intenta de nuevo.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=data["title"],
            color=discord.Color.orange()
        )
        embed.set_image(url=data["url"])
        embed.set_footer(
            text=f"👍 {data['ups']}  •  r/{data['subreddit']}"
        )
        await interaction.followup.send(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /chiste
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(name="chiste", description="Cuenta un chiste aleatorio")
    async def chiste(self, interaction: discord.Interaction):
        chistes = [
            "¿Qué le dice un bit al otro?\n— Nos vemos en el bus 🚌",
            "¿Por qué los programadores confunden Halloween con Navidad?\n— Porque Oct 31 = Dec 25 🎃",
            "¿Cómo se despide un químico?\n— ¡Ácido un placer conocerte! 🧪",
            "¿Qué hace una abeja en el gimnasio?\n— ¡Zum-ba! 🐝",
            "¿Por qué el libro de matemáticas estaba triste?\n— Tenía demasiados problemas 📚",
            "¿Qué le dijo el 0 al 8?\n— Lindo cinturón 🤣",
            "¿Cómo se llama el campeón de buceo japonés?\n— Tokofondo 🏊",
            "¿Qué le dijo el océano a la playa?\n— Nada 🌊",
        ]
        embed = discord.Embed(
            description=f"😂 {random.choice(chistes)}",
            color=discord.Color.yellow()
        )
        await interaction.response.send_message(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /dado [caras]
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="dado",
        description="Tira un dado (por defecto de 6 caras)"
    )
    @app_commands.describe(caras="Número de caras del dado (2-100)")
    async def dado(
        self,
        interaction: discord.Interaction,
        caras: app_commands.Range[int, 2, 100] = 6
    ):
        resultado = random.randint(1, caras)
        porcentaje = resultado / caras

        # Color según qué tan alto fue el resultado
        if porcentaje >= 0.8:
            color = discord.Color.green()
        elif porcentaje >= 0.4:
            color = discord.Color.yellow()
        else:
            color = discord.Color.red()

        embed = discord.Embed(
            title=f"🎲 Dado de {caras} caras",
            description=f"Resultado: **{resultado}**",
            color=color
        )
        await interaction.response.send_message(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /coinflip
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="coinflip",
        description="Lanza una moneda: cara o cruz"
    )
    async def coinflip(self, interaction: discord.Interaction):
        resultado = random.choice([("🪙 ¡CARA!", discord.Color.gold()),
                                   ("🪙 ¡CRUZ!", discord.Color.greyple())])
        embed = discord.Embed(
            description=resultado[0],
            color=resultado[1]
        )
        await interaction.response.send_message(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /8ball <pregunta>
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="8ball",
        description="Hazle una pregunta a la bola mágica"
    )
    @app_commands.describe(pregunta="Tu pregunta para la bola mágica")
    async def ball8(self, interaction: discord.Interaction, pregunta: str):
        respuestas = [
            ("✅ Sí, definitivamente.",        discord.Color.green()),
            ("✅ Todo apunta a que sí.",        discord.Color.green()),
            ("✅ Sin duda alguna.",             discord.Color.green()),
            ("🤔 Pregunta de nuevo más tarde.", discord.Color.yellow()),
            ("🤔 No puedo predecirlo ahora.",   discord.Color.yellow()),
            ("🤔 Mejor no te digo...",          discord.Color.yellow()),
            ("❌ No cuentes con ello.",          discord.Color.red()),
            ("❌ La respuesta es no.",           discord.Color.red()),
            ("❌ Mis fuentes dicen que no.",     discord.Color.red()),
        ]
        texto, color = random.choice(respuestas)

        embed = discord.Embed(title="🎱 Bola mágica", color=color)
        embed.add_field(name="❓ Pregunta",  value=pregunta, inline=False)
        embed.add_field(name="🔮 Respuesta", value=texto,    inline=False)
        await interaction.response.send_message(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /trivia
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="trivia",
        description="Responde una pregunta de trivia en 15 segundos"
    )
    async def trivia(self, interaction: discord.Interaction):
        await interaction.response.defer()

        async with self.session.get(
            "https://opentdb.com/api.php?amount=1&type=multiple"
        ) as resp:
            if resp.status != 200:
                await interaction.followup.send(
                    "❌ No pude obtener una pregunta. Intenta más tarde.",
                    ephemeral=True
                )
                return
            data = await resp.json()

        pregunta    = data["results"][0]["question"]
        correcta    = data["results"][0]["correct_answer"]
        incorrectas = data["results"][0]["incorrect_answers"]

        opciones = incorrectas + [correcta]
        random.shuffle(opciones)

        letras         = ["🇦", "🇧", "🇨", "🇩"]
        opciones_texto = "\n".join(
            f"{letras[i]}  {opciones[i]}"
            for i in range(len(opciones))
        )
        letra_correcta = letras[opciones.index(correcta)]

        embed = discord.Embed(
            title="🧠 Trivia",
            description=pregunta,
            color=discord.Color.teal()
        )
        embed.add_field(name="Opciones", value=opciones_texto, inline=False)
        embed.set_footer(text="Tienes 15 segundos para responder...")
        await interaction.followup.send(embed=embed)

        def check(m: discord.Message):
            return (
                m.author == interaction.user
                and m.channel.id == interaction.channel.id
            )

        try:
            msg = await self.bot.wait_for("message", timeout=15.0, check=check)
            acertó = msg.content.strip().upper() in letra_correcta

            embed_resp = discord.Embed(
                description=(
                    f"{'✅ ¡Correcto' if acertó else '❌ ¡Incorrecto'}, "
                    f"{interaction.user.mention}! "
                    f"La respuesta era {letra_correcta} **{correcta}**"
                ),
                color=discord.Color.green() if acertó else discord.Color.red()
            )
            await interaction.channel.send(embed=embed_resp)

        except asyncio.TimeoutError:
            embed_time = discord.Embed(
                description=(
                    f"⏰ ¡Tiempo! {interaction.user.mention} "
                    f"La respuesta era {letra_correcta} **{correcta}**"
                ),
                color=discord.Color.orange()
            )
            await interaction.channel.send(embed=embed_time)


async def setup(bot: commands.Bot):
    await bot.add_cog(Diversion(bot))