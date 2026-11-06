import discord
from discord import app_commands
from discord.ext import commands
from utils import db
import random
import asyncio


# ══════════════════════════════════════════════════════════════════
#  HELPERS — baraja (blackjack)
# ══════════════════════════════════════════════════════════════════

PALOS   = ["♠️", "♥️", "♦️", "♣️"]
VALORES = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

def nueva_baraja() -> list:
    baraja = [{"palo": p, "valor": v} for p in PALOS for v in VALORES]
    random.shuffle(baraja)
    return baraja

def valor_carta(carta: dict) -> int:
    v = carta["valor"]
    if v in ("J", "Q", "K"): return 10
    if v == "A":              return 11
    return int(v)

def calcular_mano(mano: list) -> int:
    total = sum(valor_carta(c) for c in mano)
    ases  = sum(1 for c in mano if c["valor"] == "A")
    while total > 21 and ases:
        total -= 10
        ases  -= 1
    return total

def mostrar_mano(mano: list) -> str:
    return "  ".join(f"{c['valor']}{c['palo']}" for c in mano)


# ══════════════════════════════════════════════════════════════════
#  HELPERS — baraja y evaluación de manos (poker)
# ══════════════════════════════════════════════════════════════════

VALORES_POKER  = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
VALOR_NUM      = {v: i for i, v in enumerate(VALORES_POKER)}   # "2"→0 … "A"→12

def nueva_baraja_poker() -> list[tuple[str, str]]:
    baraja = [(v, p) for v in VALORES_POKER for p in PALOS]
    random.shuffle(baraja)
    return baraja

def carta_poker_str(carta: tuple[str, str]) -> str:
    return f"{carta[0]}{carta[1]}"

def mano_poker_str(mano: list[tuple[str, str]]) -> str:
    return "  ".join(carta_poker_str(c) for c in mano)

def _grupos_poker(mano7: list[tuple[str, str]]) -> list[tuple[str, int]]:
    conteo: dict[str, int] = {}
    for v, _ in mano7:
        conteo[v] = conteo.get(v, 0) + 1
    return sorted(conteo.items(), key=lambda x: (x[1], VALOR_NUM[x[0]]), reverse=True)

def _es_color_poker(mano7: list[tuple[str, str]]) -> list[tuple[str, str]] | None:
    por_palo: dict[str, list] = {}
    for carta in mano7:
        por_palo.setdefault(carta[1], []).append(carta)
    for cartas in por_palo.values():
        if len(cartas) >= 5:
            return sorted(cartas, key=lambda c: VALOR_NUM[c[0]], reverse=True)[:5]
    return None

def _escalera_poker(vals: list[int]) -> int | None:
    unicos = sorted(set(vals), reverse=True)
    if {12, 0, 1, 2, 3}.issubset(set(unicos)):
        return 3   # rueda A-2-3-4-5, carta alta = 5
    for i in range(len(unicos) - 4):
        if unicos[i] - unicos[i + 4] == 4:
            return unicos[i]
    return None

def evaluar_mano_poker(mano7: list[tuple[str, str]]) -> tuple[int, list[int]]:
    """
    Devuelve (rango, desempates).
    8=Escalera Real · 7=Esc.Color · 6=Póker · 5=Full · 4=Color
    3=Escalera · 2=Trío · 1=Doble Par · 0=Par/Carta Alta
    """
    nums   = sorted([VALOR_NUM[v] for v, _ in mano7], reverse=True)
    grupos = _grupos_poker(mano7)
    color5 = _es_color_poker(mano7)
    esc_h  = _escalera_poker(nums)

    # Escalera de Color / Escalera Real
    if color5:
        vals_c = [VALOR_NUM[c[0]] for c in color5]
        esc_c  = _escalera_poker(vals_c)
        if esc_c is not None:
            return (8, [esc_c]) if esc_c == 12 else (7, [esc_c])

    # Póker (4 iguales)
    if grupos[0][1] == 4:
        cuatro = VALOR_NUM[grupos[0][0]]
        kicker = max(VALOR_NUM[v] for v, _ in mano7 if v != grupos[0][0])
        return (6, [cuatro, kicker])

    # Full House
    if grupos[0][1] == 3 and grupos[1][1] >= 2:
        return (5, [VALOR_NUM[grupos[0][0]], VALOR_NUM[grupos[1][0]]])

    # Color
    if color5:
        return (4, [VALOR_NUM[c[0]] for c in color5])

    # Escalera
    if esc_h is not None:
        return (3, [esc_h])

    # Trío
    if grupos[0][1] == 3:
        trio    = VALOR_NUM[grupos[0][0]]
        kickers = sorted([VALOR_NUM[v] for v, _ in mano7 if v != grupos[0][0]], reverse=True)[:2]
        return (2, [trio] + kickers)

    # Doble Par
    if grupos[0][1] == 2 and grupos[1][1] == 2:
        p1     = max(VALOR_NUM[grupos[0][0]], VALOR_NUM[grupos[1][0]])
        p2     = min(VALOR_NUM[grupos[0][0]], VALOR_NUM[grupos[1][0]])
        kicker = max(VALOR_NUM[v] for v, _ in mano7
                     if v not in (grupos[0][0], grupos[1][0]))
        return (1, [p1, p2, kicker])

    # Par
    if grupos[0][1] == 2:
        par     = VALOR_NUM[grupos[0][0]]
        kickers = sorted([VALOR_NUM[v] for v, _ in mano7 if v != grupos[0][0]], reverse=True)[:3]
        return (0, [par] + kickers)

    # Carta Alta
    return (0, nums[:5])

def describir_mano_poker(mano7: list[tuple[str, str]]) -> str:
    rango, _ = evaluar_mano_poker(mano7)
    grupos   = _grupos_poker(mano7)
    if rango == 8: return "🏆 Escalera Real"
    if rango == 7: return "🎯 Escalera de Color"
    if rango == 6: return f"🃏 Póker de {grupos[0][0]}s"
    if rango == 5: return f"🏠 Full House ({grupos[0][0]}s sobre {grupos[1][0]}s)"
    if rango == 4: return "🎨 Color"
    if rango == 3: return "📈 Escalera"
    if rango == 2: return f"3️⃣ Trío de {grupos[0][0]}s"
    if rango == 1: return f"2️⃣ Doble Par ({grupos[0][0]}s y {grupos[1][0]}s)"
    if grupos[0][1] == 2: return f"1️⃣ Par de {grupos[0][0]}s"
    return f"🂠 Carta Alta ({grupos[0][0]})"


# ══════════════════════════════════════════════════════════════════
#  ESTADO — partida de poker
# ══════════════════════════════════════════════════════════════════

class PartidaPoker:
    def __init__(self, user_id: int, guild_id: int, apuesta: int):
        self.user_id  = user_id
        self.guild_id = guild_id
        self.apuesta  = apuesta
        self.bote     = apuesta * 2   # usuario + bot aportan lo mismo

        baraja         = nueva_baraja_poker()
        self.mano_user = [baraja.pop(), baraja.pop()]
        self.mano_bot  = [baraja.pop(), baraja.pop()]
        self.comunales = [baraja.pop() for _ in range(5)]
        self.fase      = 0   # 0=pre-flop · 1=flop · 2=turn · 3=river · 4=showdown

    def cartas_visibles(self) -> list[tuple[str, str]]:
        if self.fase == 0: return []
        if self.fase == 1: return self.comunales[:3]
        if self.fase == 2: return self.comunales[:4]
        return self.comunales[:5]

    def mano_total_user(self) -> list[tuple[str, str]]:
        return self.mano_user + self.comunales

    def mano_total_bot(self) -> list[tuple[str, str]]:
        return self.mano_bot + self.comunales

    def decision_bot(self) -> str:
        visibles = self.cartas_visibles()
        if not visibles:
            return "check"
        rango, _ = evaluar_mano_poker(self.mano_bot + visibles)
        if rango >= 2:                              # Trío o mejor → sube siempre
            return "raise"
        if rango == 0 and random.random() < 0.25:  # mano débil → fold ocasional
            return "fold"
        if random.random() < 0.25:                 # bluff
            return "raise"
        return "check"

    def ganador(self) -> str:
        ru, du = evaluar_mano_poker(self.mano_total_user())
        rb, db_ = evaluar_mano_poker(self.mano_total_bot())
        if ru > rb: return "user"
        if rb > ru: return "bot"
        return "empate" if du == db_ else ("user" if du > db_ else "bot")


def _embed_poker(
    partida: PartidaPoker,
    titulo: str,
    color: discord.Color,
    mostrar_bot: bool = False
) -> discord.Embed:
    fases = ["Pre-Flop", "Flop", "Turn", "River", "Showdown"]
    embed = discord.Embed(
        title=f"🃏 Texas Hold'em — {fases[min(partida.fase, 4)]}",
        description=titulo,
        color=color
    )
    embed.add_field(name="🙋 Tu mano",    value=mano_poker_str(partida.mano_user), inline=True)
    embed.add_field(
        name="🤖 Bot",
        value=mano_poker_str(partida.mano_bot) if mostrar_bot else "🂠  🂠",
        inline=True
    )
    visibles = partida.cartas_visibles()
    embed.add_field(
        name="🎴 Mesa",
        value=mano_poker_str(visibles) if visibles else "_Aún no reveladas_",
        inline=False
    )
    embed.add_field(name="💰 Bote",       value=f"**{partida.bote:,} 🪙**", inline=True)
    embed.add_field(name="🎯 Tu apuesta", value=f"{partida.apuesta:,} 🪙",  inline=True)
    if mostrar_bot:
        embed.add_field(name="📊 Tu mano",   value=describir_mano_poker(partida.mano_total_user()), inline=False)
        embed.add_field(name="📊 Mano bot",  value=describir_mano_poker(partida.mano_total_bot()),  inline=False)
    embed.set_footer(text="Se borra en 5 min")
    return embed


# ══════════════════════════════════════════════════════════════════
#  VIEW — botones de acción del poker
# ══════════════════════════════════════════════════════════════════

class PokerView(discord.ui.View):

    def __init__(self, cog: "Minijuegos", partida: PartidaPoker):
        super().__init__(timeout=300)
        self.cog     = cog
        self.partida = partida

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.partida.user_id:
            await interaction.response.send_message("❌ Esta no es tu partida.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        """Devuelve la apuesta si el usuario no responde en 5 minutos."""
        partida = self.partida
        self.cog.partidas_activas.discard(partida.user_id)
        await db.add_coins(partida.guild_id, partida.user_id, partida.apuesta)

    # ── lógica central ─────────────────────────────────────────────

    async def _avanzar(self, interaction: discord.Interaction):
        partida = self.partida
        partida.fase += 1
        decision = partida.decision_bot()

        # Bot se retira → usuario cobra el bote
        if decision == "fold":
            self.cog.partidas_activas.discard(partida.user_id)
            self.stop()
            await db.add_coins(partida.guild_id, partida.user_id, partida.bote)
            embed = _embed_poker(
                partida,
                f"🤖 El bot se retiró. ¡Ganas **{partida.bote:,} 🪙**!",
                discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return

        # Bot sube
        desc_bot = ""
        if decision == "raise":
            subida = max(10, partida.apuesta // 2)
            saldo  = await db.get_economy(partida.guild_id, partida.user_id)
            if saldo["coins"] >= subida:
                await db.add_coins(partida.guild_id, partida.user_id, -subida)
                partida.bote    += subida * 2
                partida.apuesta += subida
                desc_bot = f"\n🤖 El bot sube **{subida:,} 🪙** — igualaste automáticamente."
            else:
                desc_bot = "\n🤖 El bot intenta subir pero no tienes fondos — se continúa."
        else:
            desc_bot = "\n🤖 El bot hace check."

        # Si llegamos al river → showdown directo
        if partida.fase >= 4:
            await self._showdown(interaction, desc_bot.strip())
            return

        fases_nombre = ["", "Flop", "Turn", "River"]
        embed = _embed_poker(
            partida,
            f"**{fases_nombre[partida.fase]}** revelado.{desc_bot}",
            discord.Color.blue()
        )
        embed.set_footer(text="Check = pasar · Raise = subir · Fold = retirarte  •  Se borra en 5 min")
        await interaction.response.edit_message(embed=embed, view=PokerView(self.cog, partida))

    async def _showdown(self, interaction: discord.Interaction, prefijo: str = ""):
        partida = self.partida
        partida.fase = 4
        ganador = partida.ganador()
        bote    = partida.bote

        self.cog.partidas_activas.discard(partida.user_id)
        self.stop()

        if ganador == "user":
            await db.add_coins(partida.guild_id, partida.user_id, bote)
            titulo = f"🏆 ¡Ganaste! Te llevas **{bote:,} 🪙**"
            color  = discord.Color.green()
        elif ganador == "bot":
            titulo = f"💸 El bot ganó. Perdiste **{partida.apuesta:,} 🪙**"
            color  = discord.Color.red()
        else:
            await db.add_coins(partida.guild_id, partida.user_id, partida.apuesta)
            titulo = f"🤝 Empate — recuperas **{partida.apuesta:,} 🪙**"
            color  = discord.Color.yellow()

        if prefijo:
            titulo = f"{prefijo}\n{titulo}"

        embed = _embed_poker(partida, titulo, color, mostrar_bot=True)
        await interaction.response.edit_message(embed=embed, view=None)

    # ── Botones ────────────────────────────────────────────────────

    @discord.ui.button(label="✅ Check / Call", style=discord.ButtonStyle.primary)
    async def check(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._avanzar(interaction)

    @discord.ui.button(label="⬆️ Raise", style=discord.ButtonStyle.success)
    async def raise_bet(self, interaction: discord.Interaction, button: discord.ui.Button):
        partida = self.partida
        subida  = max(10, partida.apuesta // 2)
        saldo   = await db.get_economy(partida.guild_id, partida.user_id)
        if saldo["coins"] < subida:
            await interaction.response.send_message(
                f"❌ Necesitas **{subida:,} 🪙** para subir. Tienes {saldo['coins']:,} 🪙.",
                ephemeral=True
            )
            return
        await db.add_coins(partida.guild_id, partida.user_id, -subida)
        partida.bote    += subida * 2
        partida.apuesta += subida
        await self._avanzar(interaction)

    @discord.ui.button(label="❌ Fold", style=discord.ButtonStyle.danger)
    async def fold(self, interaction: discord.Interaction, button: discord.ui.Button):
        partida = self.partida
        self.cog.partidas_activas.discard(partida.user_id)
        self.stop()
        embed = _embed_poker(
            partida,
            f"🏳️ Te retiraste. Perdiste **{partida.apuesta:,} 🪙**.",
            discord.Color.red(),
            mostrar_bot=True
        )
        await interaction.response.edit_message(embed=embed, view=None)


# ══════════════════════════════════════════════════════════════════
#  VIEW — Panel principal del casino (persistente)
# ══════════════════════════════════════════════════════════════════

class PanelCasino(discord.ui.View):
    """Panel fijo en el canal del casino con los 5 juegos."""

    def __init__(self):
        super().__init__(timeout=None)

    # Referencia al Cog — se inyecta al registrar la view
    cog: "Minijuegos" = None

    async def _verificar_canal(self, interaction: discord.Interaction) -> bool:
        config   = await db.get_guild(interaction.guild.id)
        canal_id = config.get("casino_channel") if config else None
        if not canal_id or interaction.channel.id != int(canal_id):
            await interaction.response.send_message(
                "❌ Este panel solo funciona en el canal de casino configurado.",
                ephemeral=True
            )
            return False
        return True

    async def _verificar_disponible(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id in self.cog.partidas_activas:
            await interaction.response.send_message(
                "⚠️ Ya tienes una partida activa. Termínala antes de iniciar otra.",
                ephemeral=True
            )
            return False
        return True

    # ── Botones ────────────────────────────────────────────────────

    @discord.ui.button(
        label="Blackjack 🃏",
        style=discord.ButtonStyle.success,
        custom_id="casino:blackjack",
        row=0
    )
    async def blackjack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._verificar_canal(interaction): return
        if not await self._verificar_disponible(interaction): return
        await interaction.response.send_modal(ModalApuesta("blackjack"))

    @discord.ui.button(
        label="Tragamonedas 🎰",
        style=discord.ButtonStyle.success,
        custom_id="casino:tragamonedas",
        row=0
    )
    async def tragamonedas(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._verificar_canal(interaction): return
        if not await self._verificar_disponible(interaction): return
        await interaction.response.send_modal(ModalApuesta("tragamonedas"))

    @discord.ui.button(
        label="Ruleta 🎡",
        style=discord.ButtonStyle.success,
        custom_id="casino:ruleta",
        row=1
    )
    async def ruleta(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._verificar_canal(interaction): return
        if not await self._verificar_disponible(interaction): return
        await interaction.response.send_modal(ModalApuesta("ruleta"))

    @discord.ui.button(
        label="Coinflip 🪙",
        style=discord.ButtonStyle.success,
        custom_id="casino:coinflip",
        row=1
    )
    async def coinflip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._verificar_canal(interaction): return
        if not await self._verificar_disponible(interaction): return
        await interaction.response.send_modal(ModalApuesta("coinflip"))

    @discord.ui.button(
        label="Poker ♠️",
        style=discord.ButtonStyle.primary,
        custom_id="casino:poker",
        row=2
    )
    async def poker(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._verificar_canal(interaction): return
        if not await self._verificar_disponible(interaction): return
        await interaction.response.send_modal(ModalApuesta("poker"))


# ══════════════════════════════════════════════════════════════════
#  MODAL — pedir apuesta
# ══════════════════════════════════════════════════════════════════

class ModalApuesta(discord.ui.Modal):

    apuesta_input = discord.ui.TextInput(
        label="¿Cuánto quieres apostar?",
        placeholder="Ej: 100",
        min_length=1,
        max_length=7
    )

    def __init__(self, juego: str):
        super().__init__(title=f"Apuesta — {juego.capitalize()}")
        self.juego = juego

    async def on_submit(self, interaction: discord.Interaction):
        try:
            apuesta = int(self.apuesta_input.value)
            if apuesta < 10:
                raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "❌ La apuesta debe ser un número entero de al menos **10 🪙**.",
                ephemeral=True
            )
            return

        eco = await db.get_economy(interaction.guild.id, interaction.user.id)
        if eco["coins"] < apuesta:
            await interaction.response.send_message(
                f"❌ No tienes suficientes monedas. Tienes **{eco['coins']:,} 🪙**.",
                ephemeral=True
            )
            return

        cog = PanelCasino.cog
        if self.juego == "blackjack":
            await cog.iniciar_blackjack(interaction, apuesta)
        elif self.juego == "tragamonedas":
            await cog.iniciar_tragamonedas(interaction, apuesta)
        elif self.juego == "ruleta":
            await cog.iniciar_ruleta(interaction, apuesta)
        elif self.juego == "coinflip":
            await cog.iniciar_coinflip(interaction, apuesta)
        elif self.juego == "poker":
            await cog.iniciar_poker(interaction, apuesta)


# ══════════════════════════════════════════════════════════════════
#  VIEW — Blackjack (Hit / Stand)
# ══════════════════════════════════════════════════════════════════

class BlackjackView(discord.ui.View):

    def __init__(self, cog: "Minijuegos", jugador: discord.Member,
                 baraja: list, mano_jugador: list, mano_dealer: list, apuesta: int):
        super().__init__(timeout=300)
        self.cog          = cog
        self.jugador      = jugador
        self.baraja       = baraja
        self.mano_jugador = mano_jugador
        self.mano_dealer  = mano_dealer
        self.apuesta      = apuesta

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.jugador.id:
            await interaction.response.send_message(
                "❌ Esta no es tu partida.", ephemeral=True
            )
            return False
        return True

    def embed_juego(self, ocultar_dealer: bool = True) -> discord.Embed:
        embed = discord.Embed(
            title=f"🃏 Blackjack — {self.jugador.display_name}",
            color=discord.Color.dark_green()
        )
        embed.add_field(
            name=f"Tu mano ({calcular_mano(self.mano_jugador)})",
            value=mostrar_mano(self.mano_jugador),
            inline=False
        )
        if ocultar_dealer:
            primera = self.mano_dealer[0]
            embed.add_field(
                name="Dealer",
                value=f"{primera['valor']}{primera['palo']}  🂠",
                inline=False
            )
        else:
            embed.add_field(
                name=f"Dealer ({calcular_mano(self.mano_dealer)})",
                value=mostrar_mano(self.mano_dealer),
                inline=False
            )
        embed.set_footer(text=f"Apuesta: {self.apuesta:,} 🪙  •  Se borra en 5 min")
        return embed

    async def finalizar(self, interaction: discord.Interaction, bust: bool = False):
        self.cog.partidas_activas.discard(self.jugador.id)
        self.stop()

        while calcular_mano(self.mano_dealer) < 17:
            self.mano_dealer.append(self.baraja.pop())

        total_j = calcular_mano(self.mano_jugador)
        total_d = calcular_mano(self.mano_dealer)

        if bust:
            resultado = "lose"
        elif total_d > 21 or total_j > total_d:
            resultado = "win"
        elif total_j == total_d:
            resultado = "push"
        else:
            resultado = "lose"

        guild_id = interaction.guild.id
        user_id  = self.jugador.id

        if resultado == "win":
            await db.add_coins(guild_id, user_id, self.apuesta)
            desc  = f"🎉 **{self.jugador.display_name}** ganó **{self.apuesta:,} 🪙**"
            color = discord.Color.green()
        elif resultado == "push":
            desc  = f"🤝 **{self.jugador.display_name}** empató — se devuelve la apuesta"
            color = discord.Color.yellow()
        else:
            await db.add_coins(guild_id, user_id, -self.apuesta)
            desc  = f"💸 **{self.jugador.display_name}** perdió **{self.apuesta:,} 🪙**"
            color = discord.Color.red()

        eco = await db.get_economy(guild_id, user_id)
        embed = discord.Embed(
            title="🃏 Blackjack — Resultado",
            description=desc,
            color=color
        )
        embed.add_field(name=f"Tu mano ({total_j})", value=mostrar_mano(self.mano_jugador), inline=True)
        embed.add_field(name=f"Dealer ({total_d})",  value=mostrar_mano(self.mano_dealer),  inline=True)
        embed.set_footer(text=f"Balance: {eco['coins']:,} 🪙  •  Se borra en 5 min")
        await interaction.response.edit_message(embed=embed, view=None)

    async def on_timeout(self):
        self.cog.partidas_activas.discard(self.jugador.id)

    @discord.ui.button(label="Hit 🃏", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.mano_jugador.append(self.baraja.pop())
        total = calcular_mano(self.mano_jugador)
        if total > 21:
            await self.finalizar(interaction, bust=True)
            return
        if total == 21:
            await self.finalizar(interaction, bust=False)
            return
        await interaction.response.edit_message(embed=self.embed_juego(), view=self)

    @discord.ui.button(label="Stand 🛑", style=discord.ButtonStyle.secondary)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.finalizar(interaction, bust=False)


# ══════════════════════════════════════════════════════════════════
#  VIEW — Ruleta
# ══════════════════════════════════════════════════════════════════

class RuletaView(discord.ui.View):

    NUMEROS_ROJOS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}

    def __init__(self, cog: "Minijuegos", jugador: discord.Member, apuesta: int):
        super().__init__(timeout=300)
        self.cog     = cog
        self.jugador = jugador
        self.apuesta = apuesta

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.jugador.id:
            await interaction.response.send_message(
                "❌ Esta no es tu ruleta.", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self):
        self.cog.partidas_activas.discard(self.jugador.id)

    async def resolver(self, interaction: discord.Interaction, tipo: str, eleccion: str):
        self.cog.partidas_activas.discard(self.jugador.id)
        self.stop()

        numero  = random.randint(0, 36)
        es_rojo = numero in self.NUMEROS_ROJOS
        es_par  = numero != 0 and numero % 2 == 0

        if tipo == "numero":
            gano          = str(numero) == eleccion
            multiplicador = 35
        elif tipo == "color":
            gano          = (eleccion == "rojo" and es_rojo) or \
                            (eleccion == "negro" and not es_rojo and numero != 0)
            multiplicador = 1
        else:
            gano          = (eleccion == "par" and es_par) or \
                            (eleccion == "impar" and not es_par and numero != 0)
            multiplicador = 1

        guild_id = interaction.guild.id
        user_id  = self.jugador.id
        ganancia = self.apuesta * multiplicador
        color_num = "🔴" if es_rojo else ("⬛" if numero != 0 else "💚")

        if gano:
            await db.add_coins(guild_id, user_id, ganancia)
            desc  = f"🎉 **{self.jugador.display_name}** ganó **{ganancia:,} 🪙**"
            color = discord.Color.green()
        else:
            await db.add_coins(guild_id, user_id, -self.apuesta)
            desc  = f"💸 **{self.jugador.display_name}** perdió **{self.apuesta:,} 🪙**"
            color = discord.Color.red()

        eco = await db.get_economy(guild_id, user_id)
        embed = discord.Embed(title="🎡 Ruleta — Resultado", description=desc, color=color)
        embed.add_field(name="🎯 Número",   value=f"{color_num} **{numero}**",    inline=True)
        embed.add_field(name="Tu apuesta",  value=eleccion.capitalize(),          inline=True)
        embed.set_footer(text=f"Balance: {eco['coins']:,} 🪙  •  Se borra en 5 min")
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Rojo 🔴",        style=discord.ButtonStyle.danger,    row=0)
    async def rojo(self, i, b): await self.resolver(i, "color", "rojo")

    @discord.ui.button(label="Negro ⬛",       style=discord.ButtonStyle.secondary, row=0)
    async def negro(self, i, b): await self.resolver(i, "color", "negro")

    @discord.ui.button(label="Par 2️⃣",        style=discord.ButtonStyle.primary,   row=1)
    async def par(self, i, b): await self.resolver(i, "parimpar", "par")

    @discord.ui.button(label="Impar 1️⃣",      style=discord.ButtonStyle.primary,   row=1)
    async def impar(self, i, b): await self.resolver(i, "parimpar", "impar")

    @discord.ui.button(label="Número exacto 🎯", style=discord.ButtonStyle.success, row=2)
    async def numero(self, i, b): await i.response.send_modal(ModalNumeroRuleta(self))


class ModalNumeroRuleta(discord.ui.Modal, title="Elige un número (0–36)"):

    numero_input = discord.ui.TextInput(
        label="Número", placeholder="0 al 36", min_length=1, max_length=2
    )

    def __init__(self, view: RuletaView):
        super().__init__()
        self.ruleta_view = view

    async def on_submit(self, interaction: discord.Interaction):
        try:
            n = int(self.numero_input.value)
            if not (0 <= n <= 36): raise ValueError
        except ValueError:
            await interaction.response.send_message(
                "❌ Ingresa un número entre 0 y 36.", ephemeral=True
            )
            return
        await self.ruleta_view.resolver(interaction, "numero", str(n))


# ══════════════════════════════════════════════════════════════════
#  VIEW — Coinflip
# ══════════════════════════════════════════════════════════════════

class CoinflipView(discord.ui.View):

    def __init__(self, cog: "Minijuegos", jugador: discord.Member, apuesta: int):
        super().__init__(timeout=300)
        self.cog     = cog
        self.jugador = jugador
        self.apuesta = apuesta

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.jugador.id:
            await interaction.response.send_message("❌ Esta no es tu partida.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        self.cog.partidas_activas.discard(self.jugador.id)

    async def resolver(self, interaction: discord.Interaction, eleccion: str):
        self.cog.partidas_activas.discard(self.jugador.id)
        self.stop()

        resultado = random.choice(["cara", "cruz"])
        gano      = eleccion == resultado
        guild_id  = interaction.guild.id
        user_id   = self.jugador.id

        if gano:
            await db.add_coins(guild_id, user_id, self.apuesta)
            desc  = f"🎉 **{self.jugador.display_name}** ganó **{self.apuesta:,} 🪙**"
            color = discord.Color.green()
        else:
            await db.add_coins(guild_id, user_id, -self.apuesta)
            desc  = f"💸 **{self.jugador.display_name}** perdió **{self.apuesta:,} 🪙**"
            color = discord.Color.red()

        emoji = "🪙" if resultado == "cara" else "🔘"
        eco   = await db.get_economy(guild_id, user_id)
        embed = discord.Embed(title="🪙 Coinflip — Resultado", description=desc, color=color)
        embed.add_field(name="Resultado",   value=f"{emoji} **{resultado.capitalize()}**", inline=True)
        embed.add_field(name="Tu elección", value=eleccion.capitalize(),                   inline=True)
        embed.set_footer(text=f"Balance: {eco['coins']:,} 🪙  •  Se borra en 5 min")
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Cara 🪙",  style=discord.ButtonStyle.primary)
    async def cara(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.resolver(interaction, "cara")

    @discord.ui.button(label="Cruz 🔘", style=discord.ButtonStyle.secondary)
    async def cruz(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.resolver(interaction, "cruz")


# ══════════════════════════════════════════════════════════════════
#  COG
# ══════════════════════════════════════════════════════════════════

class Minijuegos(commands.Cog):
    """Casino con Blackjack, Tragamonedas, Ruleta, Coinflip y Poker."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.partidas_activas: set[int] = set()
        PanelCasino.cog = self

    async def cog_load(self):
        self.bot.add_view(PanelCasino())

    # ── Blackjack ──────────────────────────────────────────────────

    async def iniciar_blackjack(self, interaction: discord.Interaction, apuesta: int):
        self.partidas_activas.add(interaction.user.id)

        baraja       = nueva_baraja()
        mano_jugador = [baraja.pop(), baraja.pop()]
        mano_dealer  = [baraja.pop(), baraja.pop()]

        view = BlackjackView(
            cog=self,
            jugador=interaction.user,
            baraja=baraja,
            mano_jugador=mano_jugador,
            mano_dealer=mano_dealer,
            apuesta=apuesta
        )

        # Blackjack natural
        if calcular_mano(mano_jugador) == 21:
            self.partidas_activas.discard(interaction.user.id)
            await db.add_coins(interaction.guild.id, interaction.user.id, apuesta)
            eco = await db.get_economy(interaction.guild.id, interaction.user.id)
            embed = discord.Embed(
                title="🃏 ¡BLACKJACK NATURAL!",
                description=(
                    f"🎉 **{interaction.user.display_name}** "
                    f"ganó **{apuesta:,} 🪙** con 21 al instante"
                ),
                color=discord.Color.gold()
            )
            embed.add_field(name="Tu mano (21)", value=mostrar_mano(mano_jugador), inline=False)
            embed.set_footer(text=f"Balance: {eco['coins']:,} 🪙  •  Se borra en 5 min")
            await interaction.response.send_message(embed=embed)
            msg = await interaction.original_response()
            asyncio.create_task(auto_borrar(msg))
            return

        await interaction.response.send_message(embed=view.embed_juego(), view=view)
        msg = await interaction.original_response()
        asyncio.create_task(auto_borrar(msg))

    # ── Tragamonedas ───────────────────────────────────────────────

    async def iniciar_tragamonedas(self, interaction: discord.Interaction, apuesta: int):
        self.partidas_activas.add(interaction.user.id)

        SIMBOLOS = ["🍒", "🍋", "🔔", "💎", "7️⃣", "⭐"]
        PESOS    = [35, 25, 20, 10, 7, 3]

        carrete = random.choices(SIMBOLOS, weights=PESOS, k=3)

        if carrete[0] == carrete[1] == carrete[2]:
            simbolo     = carrete[0]
            mult        = {"7️⃣": 50, "💎": 20, "⭐": 15, "🔔": 10, "🍋": 5, "🍒": 3}[simbolo]
            desc_result = f"🎉 **¡JACKPOT!** Triple {simbolo} — ×{mult}"
            gano        = True
        elif carrete[0] == carrete[1] or carrete[1] == carrete[2]:
            mult        = 1
            desc_result = "✅ Par — recuperas tu apuesta"
            gano        = True
        else:
            mult        = 0
            desc_result = "💸 Sin combinación — pierdes la apuesta"
            gano        = False

        guild_id = interaction.guild.id
        user_id  = interaction.user.id
        ganancia = apuesta * mult

        if gano and mult > 1:
            await db.add_coins(guild_id, user_id, ganancia)
            color = discord.Color.gold()
        elif gano and mult == 1:
            color = discord.Color.yellow()
        else:
            await db.add_coins(guild_id, user_id, -apuesta)
            color = discord.Color.red()

        self.partidas_activas.discard(interaction.user.id)
        eco = await db.get_economy(guild_id, user_id)
        embed = discord.Embed(
            title="🎰 Tragamonedas",
            description=(
                f"**{interaction.user.display_name}** giró los carretes\n\n"
                f"╔══════════════╗\n"
                f"║  {carrete[0]}  {carrete[1]}  {carrete[2]}  ║\n"
                f"╚══════════════╝\n\n"
                f"{desc_result}"
            ),
            color=color
        )
        embed.set_footer(text=f"Balance: {eco['coins']:,} 🪙  •  Se borra en 5 min")
        await interaction.response.send_message(embed=embed)
        msg = await interaction.original_response()
        asyncio.create_task(auto_borrar(msg))

    # ── Ruleta ─────────────────────────────────────────────────────

    async def iniciar_ruleta(self, interaction: discord.Interaction, apuesta: int):
        self.partidas_activas.add(interaction.user.id)

        embed = discord.Embed(
            title="🎡 Ruleta",
            description=(
                f"**{interaction.user.display_name}** apostó **{apuesta:,} 🪙**\n\n"
                "Elige tu tipo de apuesta:"
            ),
            color=discord.Color.dark_gold()
        )
        embed.add_field(name="🔴 Rojo / ⬛ Negro", value="Paga ×1",  inline=True)
        embed.add_field(name="2️⃣ Par / 1️⃣ Impar",  value="Paga ×1",  inline=True)
        embed.add_field(name="🎯 Número exacto",     value="Paga ×35", inline=True)
        embed.set_footer(text="Se borra en 5 min")

        view = RuletaView(cog=self, jugador=interaction.user, apuesta=apuesta)
        await interaction.response.send_message(embed=embed, view=view)
        msg = await interaction.original_response()
        asyncio.create_task(auto_borrar(msg))

    # ── Coinflip ───────────────────────────────────────────────────

    async def iniciar_coinflip(self, interaction: discord.Interaction, apuesta: int):
        self.partidas_activas.add(interaction.user.id)

        embed = discord.Embed(
            title="🪙 Coinflip",
            description=(
                f"**{interaction.user.display_name}** apostó **{apuesta:,} 🪙**\n\n"
                "¿Cara o Cruz?"
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Se borra en 5 min")

        view = CoinflipView(cog=self, jugador=interaction.user, apuesta=apuesta)
        await interaction.response.send_message(embed=embed, view=view)
        msg = await interaction.original_response()
        asyncio.create_task(auto_borrar(msg))

    # ── Poker ──────────────────────────────────────────────────────

    async def iniciar_poker(self, interaction: discord.Interaction, apuesta: int):
        self.partidas_activas.add(interaction.user.id)

        await db.add_coins(interaction.guild.id, interaction.user.id, -apuesta)
        partida = PartidaPoker(interaction.user.id, interaction.guild.id, apuesta)

        embed = _embed_poker(
            partida,
            (
                f"Cartas repartidas. Bote inicial: **{partida.bote:,} 🪙**\n"
                f"Elige una acción para avanzar al **Flop**."
            ),
            discord.Color.blue()
        )
        embed.set_footer(text="Check = pasar · Raise = subir · Fold = retirarte  •  Se borra en 5 min")

        view = PokerView(self, partida)
        await interaction.response.send_message(embed=embed, view=view)
        msg = await interaction.original_response()
        asyncio.create_task(auto_borrar(msg))


# ══════════════════════════════════════════════════════════════════
#  HELPER — auto-borrar mensaje después de N segundos
# ══════════════════════════════════════════════════════════════════

async def auto_borrar(mensaje: discord.Message, segundos: int = 300):
    await asyncio.sleep(segundos)
    try:
        await mensaje.delete()
    except discord.NotFound:
        pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Minijuegos(bot))
