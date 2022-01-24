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

from atorin.bot import Atorin
from .. import database
from ..config import config


class Tamagotchi(commands.Cog, name="📟 Tamagotchi"):
    def __init__(self, bot: Atorin):
        self.bot = bot

    async def cog_before_invoke(self, ctx: discord.ApplicationContext):
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        )[0]
        if (
            not ctx.command.name in ("feed", "drink", "sleep")
            and pet.sleep.in_bed is not True
        ):
            return True
        else:
            raise commands.CommandError(
                f"Nie możesz użyć komendy `{ctx.command.name}` kiedy Twój pupil śpi!"
            )

    tamagotchi = SlashCommandGroup("tamagotchi", "Twój wirtualny pupil")
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
        )[0]
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

    async def food_searcher(ctx: discord.AutocompleteContext):
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.interaction.user.id
        )[0]
        inventory: list = [*{*pet.inventory}]
        return [
            item.name
            for item in inventory
            if item.type == 0 and item.name.lower().startswith(ctx.value.lower())
        ]

    @tamagotchi.command(
        description="Nakarm pupila",
        guild_ids=config["guild_ids"],
    )
    async def feed(
        self,
        ctx: discord.ApplicationContext,
        food: Option(
            str, "Wybierz jedzenie", autocomplete=food_searcher, required=True
        ),
        count: Option(int, "Ilość", required=True),
    ):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        )[0]
        inventory: dict = {
            i: pet.inventory.count(i) for i in pet.inventory
        }  # {"database.tamagotchi.Item(name="Apple")": 3,}
        item: database.tamagotchi.Item = database.tamagotchi.Item.objects(name=food)[0]
        if inventory[item] < count:
            raise commands.BadArgument(
                f"Nie posiadasz takiej ilości przedmiotu `{item.name}`!"
            )
        if item.points * count > pet.hunger.limit:
            raise commands.CommandError("Zbyt duża ilość jedzenia!")
        for i in range(count):
            pet.inventory.remove(item)
            pet.hunger.state += item.points
        pet.save()
        await ctx.send_followup("Nakarmiono pupila!")

    async def drink_searcher(ctx: discord.AutocompleteContext):
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.interaction.user.id
        )[0]
        inventory: list = [*{*pet.inventory}]
        return [
            item.name
            for item in inventory
            if item.type == 1 and item.name.lower().startswith(ctx.value.lower())
        ]

    @tamagotchi.command(
        description="Zaspokój pragnienie pupila",
        guild_ids=config["guild_ids"],
    )
    async def drink(
        self,
        ctx: discord.ApplicationContext,
        _drink: Option(
            str, "Wybierz napój", autocomplete=drink_searcher, required=True
        ),
        count: Option(int, "Ilość", required=True),
    ):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        )[0]
        inventory: dict = {
            i: pet.inventory.count(i) for i in pet.inventory
        }  # {"database.tamagotchi.Item(name="Water")": 2,}
        item: database.tamagotchi.Item = database.tamagotchi.Item.objects(name=_drink)[
            0
        ]
        if inventory[item] < count:
            raise commands.BadArgument(
                f"Nie posiadasz takiej ilości przedmiotu `{item.name}`!"
            )
        if item.points * count > pet.thirst.limit:
            raise commands.CommandError("Zbyt duża ilość napoju!")
        for i in range(count):
            pet.inventory.remove(item)
            pet.thirst.state += item.points
        pet.save()
        await ctx.send_followup("Zaspokojono pragnienie pupila!")

    @tamagotchi.command(
        description="Położ pupila spać",
        guild_ids=config["guild_ids"],
    )
    async def sleep(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        )[0]
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
        )[0]
        pet.sleep.in_bed = False
        pet.save()
        await ctx.send_followup("Pupil się obudził!")

    @tamagotchi.command(
        description="Ulepszenia pupila",
        guild_ids=config["guild_ids"],
    )
    async def upgrades(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await ctx.send_followup("Masz wszystkie ulepszenia pupila!")

    @tamagotchi.command(
        description="Saldo konta",
        guild_ids=config["guild_ids"],
    )
    async def balance(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await ctx.send_followup("Masz 100 coinów!")

    @tamagotchi.command(
        description="Darmowe 100 coinów do odebrania raz dziennie",
        guild_ids=config["guild_ids"],
    )
    async def daily(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await ctx.send_followup("Otrzymano darmowe 100 coinów!")

    @tamagotchi_shop.command(
        description="Kup jedzenie dla pupila",
        guild_ids=config["guild_ids"],
    )
    async def food(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await ctx.send_followup("Zakupiono jedzenie dla pupila!")

    @tamagotchi_shop.command(
        description="Kup napój dla pupila",
        guild_ids=config["guild_ids"],
    )
    async def drinks(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await ctx.send_followup("Zakupiono napój dla pupila!")

    @tamagotchi_shop.command(
        description="Kup ubranie dla pupila",
        guild_ids=config["guild_ids"],
    )
    async def clothes(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await ctx.send_followup("Zakupiono ubranie dla pupila!")

    @tamagotchi_shop.command(
        description="Kup ulepszenie dla pupila",
        guild_ids=config["guild_ids"],
    )
    async def upgrades(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await ctx.send_followup("Zakupiono ulepszenie dla pupila!")

    @tamagotchi.command(
        description="Przekaż coiny",
        guild_ids=config["guild_ids"],
    )
    async def transfer(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await ctx.send_followup("Przekazano 100 coinów!")

    @tamagotchi.command(
        description="Daj przedmiot",
        guild_ids=config["guild_ids"],
    )
    async def give(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await ctx.send_followup("Dano przedmiot!")


def setup(bot):
    bot.add_cog(Tamagotchi(bot))
