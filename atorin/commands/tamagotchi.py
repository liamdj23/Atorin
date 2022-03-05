"""
```yml
    _   _             _       
   / \ | |_ ___  _ __(_)_ __  
  / _ \| __/ _ \| '__| | '_ \ 
 / ___ \ || (_) | |  | | | | |
/_/   \_\__\___/|_|  |_|_| |_|
```
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                              
Made with ❤️ by Piotr Gaździcki.

"""
import discord
from discord.ext import commands
from discord.commands import slash_command, Option, OptionChoice, SlashCommandGroup
from datetime import datetime, timedelta

from atorin.bot import Atorin
from .. import database
from ..config import config


class Tamagotchi(commands.Cog, name="📟 Tamagotchi"):
    def __init__(self, bot: Atorin):
        self.bot = bot
        self.foods = {
            "1": {"name": "🍎 Jabłko", "cost": 5, "points": 5},
            "2": {"name": "🍌 Banan", "cost": 5, "points": 5},
        }
        self.drinks = {"1": {"name": "🚰 Woda", "cost": 5, "points": 5}}

    async def cog_before_invoke(self, ctx: discord.ApplicationContext):
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        if not ctx.command.name == "start" and pet is None:
            raise commands.CommandError(
                "Nie posiadasz pupila! Utwórz go komendą /tamagotchi settings start"
            )
        if ctx.command.name in ("feed", "drink", "sleep") and pet.sleep.in_bed is True:
            raise commands.CommandError(
                f"Nie możesz użyć komendy `{ctx.command.name}` kiedy Twój pupil śpi!"
            )

    tamagotchi = SlashCommandGroup("pet", "Twój wirtualny pupil")
    tamagotchi_settings = tamagotchi.create_subgroup("settings", "Ustawienia")
    tamagotchi_shop = tamagotchi.create_subgroup("shop", "Sklep")

    @tamagotchi_settings.command(
        description="Tworzy pupila", guild_ids=config["guild_ids"]
    )
    async def start(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        created: database.tamagotchi.Pet = database.tamagotchi.Pet(
            owner=ctx.author.id
        ).save()
        if created:
            await ctx.send_followup("Utworzono pupila!")
        else:
            raise commands.CommandError("Nie udało się utworzyć pupila!")

    @tamagotchi_settings.command(
        description="Usuwa pupila", guild_ids=config["guild_ids"]
    )
    async def remove(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        deleted: int = database.tamagotchi.Pet.objects(owner=ctx.author.id).delete()
        if deleted == 1:
            await ctx.send_followup("Usunięto pupila!")
        else:
            raise commands.CommandError("Nie udało się usunąć pupila!")

    @tamagotchi_settings.command(
        description="Resetuje pupila do stanu początkowego",
        guild_ids=config["guild_ids"],
    )
    async def reset(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        deleted: int = database.tamagotchi.Pet.objects(owner=ctx.author.id).delete()
        if deleted == 1:
            created: database.tamagotchi.Pet = database.tamagotchi.Pet(
                owner=ctx.author.id
            ).save()
            if created:
                await ctx.send_followup("Zresetowano pupila!")
            else:
                raise commands.CommandError("Nie udało się zresetować pupila!")
        else:
            raise commands.CommandError("Nie udało się zresetować pupila!")

    @tamagotchi.command(
        description="Status pupila",
        guild_ids=config["guild_ids"],
    )
    async def status(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        embed = discord.Embed()
        embed.title = f"Pupil {ctx.author}"
        embed.add_field(
            name="🍔 Jedzenie", value=f"{pet.hunger.state}/{pet.hunger.limit}"
        )
        embed.add_field(
            name="🥤 Pragnienie", value=f"{pet.thirst.state}/{pet.thirst.limit}"
        )
        embed.add_field(name="🛏 Sen", value=f"{pet.sleep.state}/{pet.sleep.limit}")
        await ctx.send_followup(embed=embed)

    async def food_searcher(self, ctx: discord.AutocompleteContext):
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.interaction.user.id
        ).first()
        foods: list[dict] = []
        for id in self.foods:
            if id in pet.foods:
                foods.append(self.foods[id])
        return [
            food["name"]
            for food in foods
            if food["name"].lower().startswith(ctx.value.lower())
        ]

    @tamagotchi.command(
        description="Nakarm pupila",
        guild_ids=config["guild_ids"],
    )
    async def feed(
        self,
        ctx: discord.ApplicationContext,
        food_name: Option(
            str,
            "Wybierz jedzenie",
            autocomplete=food_searcher,
        ),
    ):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        if pet.hunger.state >= 100:
            raise commands.CommandError("Pupil jest najedzony!")
        for id in self.foods:
            item = self.foods[id]
            if item["name"] == food_name:
                pet.foods[id] -= 1
                if pet.foods[id] == 0:
                    del pet.foods[id]
                pet.hunger.state += item["points"]
                pet.save()
                return await ctx.send_followup("Nakarmiono pupila!")

    async def drink_searcher(self, ctx: discord.AutocompleteContext):
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.interaction.user.id
        ).first()
        drinks: list[dict] = []
        for id in self.drinks:
            if id in pet.drinks:
                drinks.append(self.drinks[id])
        return [
            drink["name"]
            for drink in drinks
            if drink["name"].lower().startswith(ctx.value.lower())
        ]

    @tamagotchi.command(
        description="Zaspokój pragnienie pupila",
        guild_ids=config["guild_ids"],
    )
    async def drink(
        self,
        ctx: discord.ApplicationContext,
        drink_name: Option(str, "Wybierz napój", autocomplete=drink_searcher),
    ):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        if pet.thirst.state >= 100:
            raise commands.CommandError("Pupil jest napojony!")
        for id in self.drinks:
            item = self.drinks[id]
            if item["name"] == drink_name:
                pet.drinks[id] -= 1
                if pet.drinks[id] == 0:
                    del pet.drinks[id]
                pet.thirst.state += item["points"]
                pet.save()
                return await ctx.send_followup("Napojono pupila!")

    @tamagotchi.command(
        description="Położ pupila spać",
        guild_ids=config["guild_ids"],
    )
    async def sleep(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        pet.sleep.in_bed = True
        pet.save()
        await ctx.send_followup("Pupil zasnął!")

    @tamagotchi.command(
        description="Obudź pupila",
        guild_ids=config["guild_ids"],
    )
    async def wakeup(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        pet.sleep.in_bed = False
        pet.save()
        await ctx.send_followup("Pupil się obudził!")

    # @tamagotchi.command(
    #     description="Ulepszenia pupila",
    #     guild_ids=config["guild_ids"],
    # )
    # async def upgrades(self, ctx: discord.ApplicationContext):
    #     await ctx.defer()
    #     await ctx.send_followup("Masz wszystkie ulepszenia pupila!")

    @tamagotchi.command(
        description="Saldo konta",
        guild_ids=config["guild_ids"],
    )
    async def balance(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        await ctx.send_followup(f"Masz {pet.wallet} coinów!")

    @tamagotchi.command(
        description="Darmowe 100 coinów do odebrania raz dziennie",
        guild_ids=config["guild_ids"],
    )
    async def daily(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        if (datetime.now() - pet.daily) > timedelta(1):
            pet.wallet += 100
            pet.daily = datetime.now()
            pet.save()
            await ctx.send_followup("Otrzymano darmowe 100 coinów!")
        else:
            await ctx.send_followup("Otrzymałeś już darmowe 100 coinów, wróć jutro.")

    async def food_shop_searcher(self, ctx: discord.AutocompleteContext):
        return [
            item["name"]
            for item in self.foods.values()
            if item["name"].lower().startswith(ctx.value.lower())
        ]

    @tamagotchi_shop.command(
        description="Kup jedzenie dla pupila",
        guild_ids=config["guild_ids"],
    )
    async def food(
        self,
        ctx: discord.ApplicationContext,
        food_name: Option(str, "Wybierz jedzenie", autocomplete=food_shop_searcher),
    ):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        for id in self.foods:
            item = self.foods[id]
            if item["name"] == food_name:
                if pet.wallet < item["cost"]:
                    raise commands.BadArgument(
                        f"Nie posiadasz {item['cost']} coinów, aby zakupić ten przedmiot!"
                    )
                try:
                    pet.foods[id] += 1
                except KeyError:
                    pet.foods[id] = 1
                pet.wallet -= item["cost"]
                pet.save()
                return await ctx.send_followup("Zakupiono jedzenie dla pupila!")

    async def drink_shop_searcher(self, ctx: discord.AutocompleteContext):
        return [
            item["name"]
            for item in self.drinks.values()
            if item["name"].lower().startswith(ctx.value.lower())
        ]

    @tamagotchi_shop.command(
        description="Kup napój dla pupila",
        guild_ids=config["guild_ids"],
    )
    async def drink(
        self,
        ctx: discord.ApplicationContext,
        drink_name: Option(str, "Wybierz napój", autocomplete=drink_shop_searcher),
    ):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        for id in self.drinks:
            item = self.drinks[id]
            if item["name"] == drink_name:
                if pet.wallet < item["cost"]:
                    raise commands.BadArgument(
                        f"Nie posiadasz {item['cost']} coinów, aby zakupić ten przedmiot!"
                    )
                try:
                    pet.drinks[id] += 1
                except KeyError:
                    pet.drinks[id] = 1
                pet.wallet -= item["cost"]
                pet.save()
                return await ctx.send_followup("Zakupiono napój dla pupila!")

    # @tamagotchi_shop.command(
    #     description="Kup ubranie dla pupila",
    #     guild_ids=config["guild_ids"],
    # )
    # async def clothes(self, ctx: discord.ApplicationContext):
    #     await ctx.defer()
    #     await ctx.send_followup("Zakupiono ubranie dla pupila!")

    # @tamagotchi_shop.command(
    #     description="Kup ulepszenie dla pupila",
    #     guild_ids=config["guild_ids"],
    # )
    # async def upgrades(self, ctx: discord.ApplicationContext):
    #     await ctx.defer()
    #     await ctx.send_followup("Zakupiono ulepszenie dla pupila!")

    @tamagotchi.command(
        description="Przekaż coiny",
        guild_ids=config["guild_ids"],
    )
    async def transfer(
        self,
        ctx: discord.ApplicationContext,
        user: Option(discord.Member, "Wybierz komu przekazać coiny"),
        coins: Option(int, "Podaj ilość coinów", min_value=1),
    ):
        await ctx.defer()
        if user.id == ctx.author.id:
            raise commands.BadArgument("Nie możesz przekazać coinów samemu sobie!")
        author_pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        if author_pet.wallet < coins:
            raise commands.BadArgument("Nie masz takiej ilości coinów!")
        recipent_pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        if not recipent_pet:
            raise commands.BadArgument("Odbiorca nie posiada pupila!")
        author_pet.wallet -= coins
        recipent_pet.wallet += coins
        author_pet.save()
        recipent_pet.save()
        await ctx.send_followup(f"Przekazano {coins} coinów do {user.mention}!")


def setup(bot):
    bot.add_cog(Tamagotchi(bot))
