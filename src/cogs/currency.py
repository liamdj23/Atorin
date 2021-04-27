import datetime
import random
from asyncio import TimeoutError

import discord
from discord.ext import commands


class Currency(commands.Cog, name="🪙 Ekonomia"):
    def __init__(self, bot):
        self.bot = bot
        self.currency_icon = "<:atorincoin:834410470492078091>"

    # @commands.Cog.listener()
    # async def on_message(self):
    #

    async def get_wallet(self, user):
        wallet = self.bot.mongo.Wallet.objects(id=user.id).first()
        if not wallet:
            wallet = self.bot.mongo.Wallet(id=user.id)
            wallet.save()
        return wallet

    async def add_coins(self, user, coins):
        wallet = await self.get_wallet(user)
        wallet.balance = wallet.balance + coins
        wallet.save()

    @commands.command(description="Sprawdź swój stan konta", aliases=["bal", "wallet", "portfel"])
    async def balance(self, ctx):
        wallet = await self.get_wallet(ctx.author)
        embed = self.bot.embed(ctx.author)
        embed.title = f"{ctx.author}"
        embed.add_field(name="Portfel", value=f"{wallet.balance}{self.currency_icon}")
        await ctx.send(embed=embed)

    @commands.command(description=f"Odbierz darmowe 500 AtorinCoinów")
    async def daily(self, ctx):
        wallet = await self.get_wallet(ctx.author)
        now = datetime.datetime.now()
        if wallet.daily:
            if wallet.daily.date() == now.date():
                await ctx.send("❌ Odebrałeś już daily!")
                return
        wallet.daily = now
        wallet.save()
        await self.add_coins(ctx.author, 500)
        await ctx.send(f"Pomyślnie przyznano **500**{self.currency_icon}!")

    @commands.command(description="Pracuj aby powiększyć stan konta")
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def work(self, ctx):
        payment = random.randint(5, 100)
        wallet = await self.get_wallet(ctx.author)
        wallet.balance += payment
        wallet.save()
        await ctx.send(f"{ctx.author.mention} był w pracy i zarobił **{payment}**{self.currency_icon}!")

    @commands.command(description="Jednoręki bandyta\nKoszt: 100 AtorinCoinów")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def slots(self, ctx):
        wallet = await self.get_wallet(ctx.author)
        if wallet.balance < 100:
            await ctx.send(f"❌ Musisz mieć **100**{self.currency_icon} aby zagrać!")
            return
        wallet.balance -= 100
        wallet.save()
        embed = self.bot.embed(ctx.author)

        slots = [self.currency_icon, "🔋", "📀", "💿", "💾", "📼"]
        slot1 = slots[random.randint(0, 5)]
        slot2 = slots[random.randint(0, 5)]
        slot3 = slots[random.randint(0, 5)]
        slot4 = slots[random.randint(0, 5)]
        slot5 = slots[random.randint(0, 5)]
        slot6 = slots[random.randint(0, 5)]
        slot7 = slots[random.randint(0, 5)]
        slot8 = slots[random.randint(0, 5)]
        slot9 = slots[random.randint(0, 5)]

        embed.description = f"🎰 Maszyna za **100**{self.currency_icon} ruszyła...\n\n"

        embed.description += "| {} | {} | {} |\n".format(slot1, slot4, slot7)
        embed.description += "| {} | {} | {} | <---\n".format(slot2, slot5, slot8)
        embed.description += "| {} | {} | {} |\n\n".format(slot3, slot6, slot9)

        if slot2 == slot5 == slot8:
            embed.description += f"... i wygrałeś **200**{self.currency_icon}!"
            embed.color = 0x00FF00
            wallet.balance += 200
            wallet.save()
        elif slot2 == slot5:
            embed.description += f"... i wygrałeś **100**{self.currency_icon}."
            embed.color = 0x000000
            wallet.balance += 100
            wallet.save()
        else:
            embed.description += f"... i przegrałeś **100**{self.currency_icon}."
            embed.color = 0xFF0000
        await ctx.send(embed=embed)

    @commands.command(description="Zgadnij czy liczba jest większa lub mniejsza "
                                  "i zdobądź 25 AtorinCoinów")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def highlow(self, ctx):
        wallet = await self.get_wallet(ctx.author)
        number = random.randint(0, 100)
        result = random.randint(0, 100)
        embed = self.bot.embed(ctx.author)
        embed.title = "Większa czy mniejsza?"
        embed.description = f"Wylosowana liczba to **{number}**\nnastępna będzie mniejsza czy większa?"
        message = await ctx.send(embed=embed)
        await message.add_reaction("⬆")
        await message.add_reaction("⬇")

        def check(reaction, user):
            return user.id == ctx.author.id and (str(reaction.emoji) == "⬆" or str(reaction.emoji) == "⬇") \
                   and reaction.message.id == message.id

        try:
            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=60)
        except TimeoutError:
            await ctx.send("❌ Nie wybrano odpowiedzi.")
            await message.clear_reactions()
            return

        if str(reaction.emoji) == "⬆" and result > number:
            await ctx.send(f"Następna liczba to **{result}**, wygrywasz **25**{self.currency_icon}")
            wallet.balance += 25
            wallet.save()
        elif str(reaction.emoji) == "⬇" and result < number:
            await ctx.send(f"Następna liczba to **{result}**, wygrywasz **25**{self.currency_icon}")
            wallet.balance += 25
            wallet.save()
        else:
            await ctx.send(f"Następna liczba to **{result}**, przegrałeś.")

    @commands.command(description="Przekaż swoje AtorinCoiny komuś innemu", usage="<osoba> <ilość>")
    async def give(self, ctx, member: discord.Member, amount: int):
        if amount < 0:
            await ctx.send("❌ Podana liczba musi być dodatnia!")
            return
        if member.id == ctx.author.id:
            await ctx.send("❌ Nie możesz przekazywać samemu sobie!")
            return
        wallet = await self.get_wallet(ctx.author)
        if wallet.balance < amount:
            await ctx.send(f"❌ Nie masz wystarczającej ilości {self.currency_icon}!")
            return
        wallet2 = await self.get_wallet(member)
        wallet.balance -= amount
        wallet2.balance += amount
        wallet.save()
        wallet2.save()
        await ctx.send(f"Przekazano {amount}{self.currency_icon} użytkownikowi {member.mention}")
