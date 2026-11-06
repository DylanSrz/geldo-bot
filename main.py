import discord
from discord.ext import commands
import asyncio
import os
from utils.config import TOKEN, PREFIX, verificar
from utils.db import init_db

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    # Sincronizamos AQUÍ, cuando el bot ya está conectado y tiene application_id
    await bot.tree.sync()
    print(f"✅ Slash commands sincronizados")
    print(f"✅ Bot conectado como {bot.user} ({bot.user.id})")
    print(f"✅ Servidores activos: {len(bot.guilds)}")


async def main():
    verificar()

    async with bot:
        await init_db()

        for archivo in os.listdir("./cogs"):
            if archivo.endswith(".py"):
                nombre = archivo[:-3]
                try:
                    await bot.load_extension(f"cogs.{nombre}")
                    print(f"  ✅ Cog cargado: {nombre}")
                except Exception as e:
                    print(f"  ❌ Error al cargar {nombre}: {e}")

        await bot.start(TOKEN)


asyncio.run(main())
