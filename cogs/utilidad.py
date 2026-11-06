import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from utils.config import WEATHER_API_KEY, DEEPL_API_KEY


class Utilidad(commands.Cog):
    """Comandos de utilidad: clima, traducción y encuestas."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session: aiohttp.ClientSession | None = None

    async def cog_load(self):
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        if self.session:
            await self.session.close()


    # ══════════════════════════════════════════════════════════════
    #  /clima <ciudad>
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="clima",
        description="Muestra el clima actual de una ciudad"
    )
    @app_commands.describe(ciudad="Nombre de la ciudad, ej: Barranquilla")
    async def clima(self, interaction: discord.Interaction, ciudad: str):

        if not WEATHER_API_KEY:
            await interaction.response.send_message(
                "⚠️ Este comando no está disponible: "
                "falta `WEATHER_API_KEY` en el `.env`.",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        params = {
            "q":     ciudad,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang":  "es",
        }

        async with self.session.get(
            "https://api.openweathermap.org/data/2.5/weather", params=params
        ) as resp:
            if resp.status == 404:
                await interaction.followup.send(
                    f"❌ No encontré la ciudad **{ciudad}**. "
                    f"Verifica el nombre e intenta de nuevo.",
                    ephemeral=True
                )
                return
            if resp.status != 200:
                await interaction.followup.send(
                    "❌ Error al consultar el clima. Intenta más tarde.",
                    ephemeral=True
                )
                return
            data = await resp.json()

        # ── Extraemos los datos ────────────────────────────────────
        nombre      = data["name"]
        pais        = data["sys"]["country"]
        temp        = data["main"]["temp"]
        sensacion   = data["main"]["feels_like"]
        temp_min    = data["main"]["temp_min"]
        temp_max    = data["main"]["temp_max"]
        humedad     = data["main"]["humidity"]
        viento      = data["wind"]["speed"]
        descripcion = data["weather"][0]["description"].capitalize()
        icono_code  = data["weather"][0]["icon"]
        icono_url   = f"https://openweathermap.org/img/wn/{icono_code}@2x.png"
        nubosidad   = data.get("clouds", {}).get("all", 0)
        visibilidad = data.get("visibility", 0) / 1000   # metros → km

        # Color del embed según temperatura
        if temp >= 30:
            color = discord.Color.red()
        elif temp >= 20:
            color = discord.Color.orange()
        elif temp >= 10:
            color = discord.Color.blue()
        else:
            color = discord.Color.teal()

        embed = discord.Embed(
            title=f"🌍 {nombre}, {pais}",
            description=descripcion,
            color=color
        )
        embed.set_thumbnail(url=icono_url)
        embed.add_field(
            name="🌡️ Temperatura",
            value=f"{temp:.1f} °C",
            inline=True
        )
        embed.add_field(
            name="🤔 Sensación",
            value=f"{sensacion:.1f} °C",
            inline=True
        )
        embed.add_field(
            name="💧 Humedad",
            value=f"{humedad}%",
            inline=True
        )
        embed.add_field(
            name="🔼 Máx / 🔽 Mín",
            value=f"{temp_max:.1f} °C / {temp_min:.1f} °C",
            inline=True
        )
        embed.add_field(
            name="💨 Viento",
            value=f"{viento} m/s",
            inline=True
        )
        embed.add_field(
            name="☁️ Nubosidad",
            value=f"{nubosidad}%",
            inline=True
        )
        embed.add_field(
            name="👁️ Visibilidad",
            value=f"{visibilidad:.1f} km",
            inline=True
        )
        embed.set_footer(text="Datos de OpenWeatherMap")
        embed.timestamp = discord.utils.utcnow()

        await interaction.followup.send(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /traducir <texto> <idioma>
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="traducir",
        description="Traduce un texto al idioma que elijas"
    )
    @app_commands.describe(
        texto="Texto a traducir (máx. 500 caracteres)",
        idioma="Idioma destino"
    )
    @app_commands.choices(idioma=[
        app_commands.Choice(name="Español",   value="ES"),
        app_commands.Choice(name="Inglés",    value="EN-US"),
        app_commands.Choice(name="Francés",   value="FR"),
        app_commands.Choice(name="Alemán",    value="DE"),
        app_commands.Choice(name="Portugués", value="PT-BR"),
        app_commands.Choice(name="Italiano",  value="IT"),
        app_commands.Choice(name="Japonés",   value="JA"),
        app_commands.Choice(name="Chino",     value="ZH"),
    ])
    async def traducir(
        self,
        interaction: discord.Interaction,
        texto: str,
        idioma: app_commands.Choice[str]
    ):
        if not DEEPL_API_KEY:
            await interaction.response.send_message(
                "⚠️ Este comando no está disponible: "
                "falta `DEEPL_API_KEY` en el `.env`.",
                ephemeral=True
            )
            return

        # Limitamos el texto para no gastar quota innecesariamente
        if len(texto) > 500:
            await interaction.response.send_message(
                "❌ El texto no puede superar los 500 caracteres.",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        url     = "https://api-free.deepl.com/v2/translate"
        payload = {
            "auth_key":    DEEPL_API_KEY,
            "text":        texto,
            "target_lang": idioma.value,
        }

        async with self.session.post(url, data=payload) as resp:
            if resp.status == 403:
                await interaction.followup.send(
                    "❌ API key de DeepL inválida. "
                    "Revisa `DEEPL_API_KEY` en el `.env`.",
                    ephemeral=True
                )
                return
            if resp.status == 456:
                await interaction.followup.send(
                    "❌ Se agotó la cuota mensual de DeepL.",
                    ephemeral=True
                )
                return
            if resp.status != 200:
                await interaction.followup.send(
                    "❌ Error al traducir. Intenta más tarde.",
                    ephemeral=True
                )
                return
            data = await resp.json()

        traduccion      = data["translations"][0]["text"]
        idioma_detectado = data["translations"][0].get(
            "detected_source_language", "?"
        )

        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(
            name=f"📝 Original ({idioma_detectado})",
            value=f"```{texto}```",
            inline=False
        )
        embed.add_field(
            name=f"🌐 Traducción → {idioma.name}",
            value=f"```{traduccion}```",
            inline=False
        )
        embed.set_footer(text="Traducido con DeepL")
        await interaction.followup.send(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /poll <pregunta> <opcion1> <opcion2> [opcion3] [opcion4]
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="poll",
        description="Crea una encuesta con hasta 4 opciones"
    )
    @app_commands.describe(
        pregunta="La pregunta de la encuesta",
        opcion1="Primera opción (obligatoria)",
        opcion2="Segunda opción (obligatoria)",
        opcion3="Tercera opción (opcional)",
        opcion4="Cuarta opción (opcional)",
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        pregunta:  str,
        opcion1:   str,
        opcion2:   str,
        opcion3:   str | None = None,
        opcion4:   str | None = None,
    ):
        emojis  = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]
        opciones = [o for o in [opcion1, opcion2, opcion3, opcion4]
                    if o is not None]

        descripcion = "\n\n".join(
            f"{emojis[i]}  {opcion}"
            for i, opcion in enumerate(opciones)
        )

        embed = discord.Embed(
            title=f"📊 {pregunta}",
            description=descripcion,
            color=discord.Color.gold()
        )
        embed.set_footer(
            text=f"Encuesta creada por {interaction.user.display_name}"
        )
        embed.timestamp = discord.utils.utcnow()

        await interaction.response.send_message(embed=embed)

        # Añadimos las reacciones automáticamente
        mensaje = await interaction.original_response()
        for i in range(len(opciones)):
            await mensaje.add_reaction(emojis[i])

    # ══════════════════════════════════════════════════════════════
    #  /userinfo [usuario]
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="userinfo",
        description="Muestra información de un usuario"
    )
    @app_commands.describe(usuario="Usuario a consultar (deja vacío para verte a ti)")
    async def userinfo(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member | None = None
    ):
        usuario = usuario or interaction.user

        embed = discord.Embed(
            title=f"👤 Info de {usuario.display_name}",
            color=usuario.color
        )
        embed.set_thumbnail(url=usuario.display_avatar.url)
        embed.add_field(
            name="🏷️ Usuario",
            value=str(usuario),
            inline=True
        )
        embed.add_field(
            name="🆔 ID",
            value=str(usuario.id),
            inline=True
        )
        embed.add_field(
            name="📅 En Discord desde",
            value=f"<t:{int(usuario.created_at.timestamp())}:D>",
            inline=True
        )
        embed.add_field(
            name="📥 En el servidor desde",
            value=f"<t:{int(usuario.joined_at.timestamp())}:D>",
            inline=True
        )
        embed.add_field(
            name="🎭 Roles",
            value=", ".join([r.mention for r in usuario.roles[1:]]) or "Ninguno",
            inline=False
        )
        embed.set_footer(text=f"Solicitado por {interaction.user.display_name}")
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)


    # ══════════════════════════════════════════════════════════════
    #  /serverinfo
    # ══════════════════════════════════════════════════════════════

    @app_commands.command(
        name="serverinfo",
        description="Muestra información del servidor"
    )
    async def serverinfo(self, interaction: discord.Interaction):
        server = interaction.guild

        embed = discord.Embed(
            title=f"🏰 {server.name}",
            color=discord.Color.blue()
        )
        if server.icon:
            embed.set_thumbnail(url=server.icon.url)

        embed.add_field(
            name="👑 Dueño",
            value=server.owner.mention,
            inline=True
        )
        embed.add_field(
            name="👥 Miembros",
            value=str(server.member_count),
            inline=True
        )
        embed.add_field(
            name="💬 Canales de texto",
            value=str(len(server.text_channels)),
            inline=True
        )
        embed.add_field(
            name="🔊 Canales de voz",
            value=str(len(server.voice_channels)),
            inline=True
        )
        embed.add_field(
            name="📅 Creado el",
            value=f"<t:{int(server.created_at.timestamp())}:D>",
            inline=True
        )
        embed.add_field(
            name="🎭 Roles",
            value=str(len(server.roles)),
            inline=True
        )
        embed.add_field(
            name="🆔 ID",
            value=str(server.id),
            inline=True
        )
        embed.set_footer(text=f"Solicitado por {interaction.user.display_name}")
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utilidad(bot))