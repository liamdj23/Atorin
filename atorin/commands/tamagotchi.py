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
from random import randint
import discord
from discord.ext import commands, tasks
from discord.commands import Option, SlashCommandGroup, slash_command
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from atorin.bot import Atorin
from .. import database
from ..config import config


foods = {
    "1": {"name": "🍎 Jabłko", "cost": 5, "points": 5},
    "2": {"name": "🍌 Banan", "cost": 5, "points": 5},
}
drinks = {
    "1": {"name": "🚰 Woda", "cost": 5, "points": 5},
    "2": {"name": "🧃 Sok", "cost": 10, "points": 7},
}
potions = {
    "1": {"name": "💊 Tabletka", "cost": 50, "points": 25},
    "2": {"name": "💉 Strzykawka", "cost": 200, "points": 100},
}
wallpapers = {"1": {"name": "Zwykła tapeta", "cost": 25}}
hats = {"1": {"name": "Czapka z daszkiem", "cost": 50}}


async def generate_status(owner: int):
    pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(owner=owner).first()
    template = Image.open("assets/tamagotchi/pet_status.png")
    if pet.hunger.state == 100:
        hunger_progress_bar = Image.open("assets/tamagotchi/pet_progress_100.png")
    elif pet.hunger.state <= 99 and pet.hunger.state >= 90:
        hunger_progress_bar = Image.open("assets/tamagotchi/pet_progress_90.png")
    elif pet.hunger.state <= 89 and pet.hunger.state >= 80:
        hunger_progress_bar = Image.open("assets/tamagotchi/pet_progress_80.png")
    elif pet.hunger.state <= 79 and pet.hunger.state >= 70:
        hunger_progress_bar = Image.open("assets/tamagotchi/pet_progress_70.png")
    elif pet.hunger.state <= 69 and pet.hunger.state >= 60:
        hunger_progress_bar = Image.open("assets/tamagotchi/pet_progress_60.png")
    elif pet.hunger.state <= 59 and pet.hunger.state >= 50:
        hunger_progress_bar = Image.open("assets/tamagotchi/pet_progress_50.png")
    elif pet.hunger.state <= 49 and pet.hunger.state >= 40:
        hunger_progress_bar = Image.open("assets/tamagotchi/pet_progress_40.png")
    elif pet.hunger.state <= 39 and pet.hunger.state >= 30:
        hunger_progress_bar = Image.open("assets/tamagotchi/pet_progress_30.png")
    elif pet.hunger.state <= 29 and pet.hunger.state >= 20:
        hunger_progress_bar = Image.open("assets/tamagotchi/pet_progress_20.png")
    elif pet.hunger.state <= 19 and pet.hunger.state >= 10:
        hunger_progress_bar = Image.open("assets/tamagotchi/pet_progress_10.png")
    elif pet.hunger.state <= 9 and pet.hunger.state >= 5:
        hunger_progress_bar = Image.open("assets/tamagotchi/pet_progress_5.png")
    else:
        hunger_progress_bar = None
    if pet.thirst.state == 100:
        thirst_progress_bar = Image.open("assets/tamagotchi/pet_progress_100.png")
    elif pet.thirst.state <= 99 and pet.thirst.state >= 90:
        thirst_progress_bar = Image.open("assets/tamagotchi/pet_progress_90.png")
    elif pet.thirst.state <= 89 and pet.thirst.state >= 80:
        thirst_progress_bar = Image.open("assets/tamagotchi/pet_progress_80.png")
    elif pet.thirst.state <= 79 and pet.thirst.state >= 70:
        thirst_progress_bar = Image.open("assets/tamagotchi/pet_progress_70.png")
    elif pet.thirst.state <= 69 and pet.thirst.state >= 60:
        thirst_progress_bar = Image.open("assets/tamagotchi/pet_progress_60.png")
    elif pet.thirst.state <= 59 and pet.thirst.state >= 50:
        thirst_progress_bar = Image.open("assets/tamagotchi/pet_progress_50.png")
    elif pet.thirst.state <= 49 and pet.thirst.state >= 40:
        thirst_progress_bar = Image.open("assets/tamagotchi/pet_progress_40.png")
    elif pet.thirst.state <= 39 and pet.thirst.state >= 30:
        thirst_progress_bar = Image.open("assets/tamagotchi/pet_progress_30.png")
    elif pet.thirst.state <= 29 and pet.thirst.state >= 20:
        thirst_progress_bar = Image.open("assets/tamagotchi/pet_progress_20.png")
    elif pet.thirst.state <= 19 and pet.thirst.state >= 10:
        thirst_progress_bar = Image.open("assets/tamagotchi/pet_progress_10.png")
    elif pet.thirst.state <= 9 and pet.thirst.state >= 5:
        thirst_progress_bar = Image.open("assets/tamagotchi/pet_progress_5.png")
    else:
        thirst_progress_bar = None
    if pet.sleep.state == 100:
        sleep_progress_bar = Image.open("assets/tamagotchi/pet_progress_100.png")
    elif pet.sleep.state <= 99 and pet.sleep.state >= 90:
        sleep_progress_bar = Image.open("assets/tamagotchi/pet_progress_90.png")
    elif pet.sleep.state <= 89 and pet.sleep.state >= 80:
        sleep_progress_bar = Image.open("assets/tamagotchi/pet_progress_80.png")
    elif pet.sleep.state <= 79 and pet.sleep.state >= 70:
        sleep_progress_bar = Image.open("assets/tamagotchi/pet_progress_70.png")
    elif pet.sleep.state <= 69 and pet.sleep.state >= 60:
        sleep_progress_bar = Image.open("assets/tamagotchi/pet_progress_60.png")
    elif pet.sleep.state <= 59 and pet.sleep.state >= 50:
        sleep_progress_bar = Image.open("assets/tamagotchi/pet_progress_50.png")
    elif pet.sleep.state <= 49 and pet.sleep.state >= 40:
        sleep_progress_bar = Image.open("assets/tamagotchi/pet_progress_40.png")
    elif pet.sleep.state <= 39 and pet.sleep.state >= 30:
        sleep_progress_bar = Image.open("assets/tamagotchi/pet_progress_30.png")
    elif pet.sleep.state <= 29 and pet.sleep.state >= 20:
        sleep_progress_bar = Image.open("assets/tamagotchi/pet_progress_20.png")
    elif pet.sleep.state <= 19 and pet.sleep.state >= 10:
        sleep_progress_bar = Image.open("assets/tamagotchi/pet_progress_10.png")
    elif pet.sleep.state <= 9 and pet.sleep.state >= 5:
        sleep_progress_bar = Image.open("assets/tamagotchi/pet_progress_5.png")
    else:
        sleep_progress_bar = None
    if pet.health.state == 100:
        health_progress_bar = Image.open("assets/tamagotchi/pet_progress_100.png")
    elif pet.health.state <= 99 and pet.health.state >= 90:
        health_progress_bar = Image.open("assets/tamagotchi/pet_progress_90.png")
    elif pet.health.state <= 89 and pet.health.state >= 80:
        health_progress_bar = Image.open("assets/tamagotchi/pet_progress_80.png")
    elif pet.health.state <= 79 and pet.health.state >= 70:
        health_progress_bar = Image.open("assets/tamagotchi/pet_progress_70.png")
    elif pet.health.state <= 69 and pet.health.state >= 60:
        health_progress_bar = Image.open("assets/tamagotchi/pet_progress_60.png")
    elif pet.health.state <= 59 and pet.health.state >= 50:
        health_progress_bar = Image.open("assets/tamagotchi/pet_progress_50.png")
    elif pet.health.state <= 49 and pet.health.state >= 40:
        health_progress_bar = Image.open("assets/tamagotchi/pet_progress_40.png")
    elif pet.health.state <= 39 and pet.health.state >= 30:
        health_progress_bar = Image.open("assets/tamagotchi/pet_progress_30.png")
    elif pet.health.state <= 29 and pet.health.state >= 20:
        health_progress_bar = Image.open("assets/tamagotchi/pet_progress_20.png")
    elif pet.health.state <= 19 and pet.health.state >= 10:
        health_progress_bar = Image.open("assets/tamagotchi/pet_progress_10.png")
    elif pet.health.state <= 9 and pet.health.state >= 5:
        health_progress_bar = Image.open("assets/tamagotchi/pet_progress_5.png")
    else:
        health_progress_bar = None
    if hunger_progress_bar:
        template.paste(hunger_progress_bar, (583, 150))
    if thirst_progress_bar:
        template.paste(thirst_progress_bar, (583, 267))
    if sleep_progress_bar:
        template.paste(sleep_progress_bar, (583, 383))
    if health_progress_bar:
        template.paste(health_progress_bar, (583, 500))
    # pet_background = Image.new("RGB", (316, 466), (255, 0, 0))
    if pet.wallpaper:
        pet_background = Image.open(f"assets/tamagotchi/wallpapers/{pet.wallpaper}.png")
    else:
        pet_background = Image.open("assets/tamagotchi/wallpapers/0.png")
    pet_image = Image.open("assets/tamagotchi/pet.png")
    pet_background.paste(pet_image, (0, 9), pet_image.split()[3])
    template.paste(pet_background, (117, 117))
    template_draw = ImageDraw.Draw(template)
    template_draw.text(
        (960, 140),
        f"{pet.hunger.state}",
        (255, 255, 255),
        ImageFont.truetype("assets/tamagotchi/apasih.ttf", 48),
    )
    template_draw.text(
        (960, 257),
        f"{pet.thirst.state}",
        (255, 255, 255),
        ImageFont.truetype("assets/tamagotchi/apasih.ttf", 48),
    )
    template_draw.text(
        (960, 375),
        f"{pet.sleep.state}",
        (255, 255, 255),
        ImageFont.truetype("assets/tamagotchi/apasih.ttf", 48),
    )
    template_draw.text(
        (960, 490),
        f"{pet.health.state}",
        (255, 255, 255),
        ImageFont.truetype("assets/tamagotchi/apasih.ttf", 48),
    )
    template_draw.text(
        (625, 570),
        f"Portfel: {pet.wallet}",
        (255, 255, 255),
        ImageFont.truetype("assets/tamagotchi/apasih.ttf", 44),
    )
    img = BytesIO()
    template.save(img, "PNG")
    img.seek(0)
    return img


class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value: bool = None

    @discord.ui.button(label="Potwierdź", style=discord.ButtonStyle.green)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.value = True
        self.stop()

    @discord.ui.button(label="Anuluj", style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = False
        self.stop()


class FoodDropdown(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__(
            placeholder="Wybierz jedzenie...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        id = self.values[0]
        item = foods[id]
        pet.foods[id] -= 1
        if pet.foods[id] == 0:
            del pet.foods[id]
        if pet.hunger.state + item["points"] > 100:
            await interaction.message.edit(
                content=f"Pupil nie chce zjeść {item['name']}",
                view=None,
                delete_after=10,
            )
        else:
            pet.hunger.state += item["points"]
        pet.save()
        await interaction.message.edit(
            content="Nakarmiono pupila!", view=None, delete_after=5
        )
        self.view.stop()


class DrinkDropdown(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__(
            placeholder="Wybierz napój...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        id = self.values[0]
        item = drinks[id]
        pet.drinks[id] -= 1
        if pet.drinks[id] == 0:
            del pet.drinks[id]
        if pet.thirst.state + item["points"] > 100:
            await interaction.message.edit(
                content=f"Pupil nie chce wypić {item['name']}",
                view=None,
                delete_after=10,
            )
        else:
            pet.thirst.state += item["points"]
        pet.save()
        await interaction.message.edit(
            content="Napojono pupila!", view=None, delete_after=5
        )
        self.view.stop()


class PotionDropdown(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__(
            placeholder="Wybierz lekarstwo...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        id = self.values[0]
        item = potions[id]
        pet.potions[id] -= 1
        if pet.potions[id] == 0:
            del pet.potions[id]
        if pet.health.state + item["points"] > 100:
            await interaction.message.edit(
                content=f"Pupil nie chce {item['name']}",
                view=None,
                delete_after=10,
            )
        else:
            pet.health.state += item["points"]
        pet.save()
        await interaction.message.edit(
            content="Uleczono pupila!", view=None, delete_after=5
        )
        self.view.stop()


class WallpaperDropdown(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption]):
        super().__init__(
            placeholder="Wybierz tapetę...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        id = self.values[0]
        pet.wallpaper = id
        pet.save()
        await interaction.message.edit(
            content="Zmieniono tapetę!", view=None, delete_after=5
        )
        self.view.stop()


class Pet(discord.ui.View):
    def __init__(self, message: discord.Message):
        super().__init__(timeout=60)
        self.message = message

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(view=self)

    @discord.ui.button(
        emoji="<:feed:949827709662527548>", style=discord.ButtonStyle.grey
    )
    async def foods(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        if pet.hunger.state == 100:
            await interaction.message.reply("Pupil nie jest głodny!", delete_after=10)
            return
        options: list[discord.SelectOption] = []
        for id in foods:
            if id in pet.foods:
                item = foods[id]
                options.append(
                    discord.SelectOption(
                        label=item["name"], description=f"+{item['points']}", value=id
                    )
                )
        if not options:
            await interaction.message.reply(
                content="❌ Twój pupil nie ma nic do jedzenia, użyj komendy `/pet shop food` aby zakupić jedzenie.",
                delete_after=5,
            )
            return
        view = discord.ui.View(FoodDropdown(options))
        await interaction.message.reply(
            content="⬇️ Wybierz czym chcesz nakarmić pupila",
            view=view,
            delete_after=60,
        )
        await view.wait()
        status_image = await generate_status(interaction.user.id)
        await interaction.message.edit(
            file=discord.File(status_image, "pet_status.png")
        )

    @discord.ui.button(
        emoji="<:drink:949827709641572352>", style=discord.ButtonStyle.grey
    )
    async def drinks(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        if pet.thirst.state == 100:
            await interaction.message.reply("Pupil nie chce pić!", delete_after=10)
            return
        options: list[discord.SelectOption] = []
        for id in drinks:
            if id in pet.drinks:
                item = drinks[id]
                options.append(
                    discord.SelectOption(
                        label=item["name"], description=f"+{item['points']}", value=id
                    )
                )
        if not options:
            await interaction.message.reply(
                content="❌ Twój pupil nie ma nic do picia, użyj komendy `/pet shop drinks` aby zakupić napoje.",
                delete_after=5,
            )
            return
        view = discord.ui.View(DrinkDropdown(options))
        await interaction.message.reply(
            content="⬇️ Wybierz czym chcesz napoić pupila",
            view=view,
            delete_after=60,
        )
        await view.wait()
        status_image = await generate_status(interaction.user.id)
        await interaction.message.edit(
            file=discord.File(status_image, "pet_status.png")
        )

    @discord.ui.button(
        emoji="<:sleep:949827710014853171>", style=discord.ButtonStyle.grey
    )
    async def sleep(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        if pet.sleep.in_bed:
            pet.sleep.in_bed = False
            pet.save()
            await interaction.message.reply(
                content="Pupil się obudził", delete_after=10
            )
        else:
            if pet.sleep.state == 100:
                await interaction.message.reply(
                    content="Pupil nie chce iść spać", delete_after=10
                )
                return
            pet.sleep.in_bed = True
            pet.save()
            await interaction.message.reply(content="Pupil zasnął!", delete_after=10)
        status_image = await generate_status(interaction.user.id)
        await interaction.message.edit(
            file=discord.File(status_image, "pet_status.png")
        )

    @discord.ui.button(
        emoji="<:health:949827709666742312>", style=discord.ButtonStyle.grey
    )
    async def potions(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        if pet.health.state == 100:
            await interaction.message.reply("Pupil nie jest chory!", delete_after=10)
            return
        options: list[discord.SelectOption] = []
        for id in potions:
            if id in pet.potions:
                item = potions[id]
                options.append(
                    discord.SelectOption(
                        label=item["name"], description=f"+{item['points']}", value=id
                    )
                )
        if not options:
            await interaction.message.reply(
                content="❌ Twój pupil nie ma lekarstw, użyj komendy `/pet shop potions` aby zakupić lekarstwa.",
                delete_after=5,
            )
            return
        view = discord.ui.View(FoodDropdown(options))
        await interaction.message.reply(
            content="⬇️ Wybierz czym chcesz uleczyć pupila",
            view=view,
            delete_after=60,
        )
        status_image = await generate_status(interaction.user.id)
        await interaction.message.edit(
            file=discord.File(status_image, "pet_status.png")
        )

    @discord.ui.button(emoji="🖼", style=discord.ButtonStyle.grey)
    async def wallpapers(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        options: list[discord.SelectOption] = []
        for id in wallpapers:
            if id in pet.wallpapers and not id == pet.wallpaper:
                item = wallpapers[id]
                options.append(discord.SelectOption(label=item["name"], value=id))
        if not options:
            await interaction.message.reply(
                content="❌ Twój pupil nie ma tapet, użyj komendy `/pet shop wallpapers` aby zakupić tapety.",
                delete_after=5,
            )
            return
        view = discord.ui.View(WallpaperDropdown(options))
        await interaction.message.reply(
            content="⬇️ Wybierz tapetę do pokoju pupila",
            view=view,
            delete_after=60,
        )
        status_image = await generate_status(interaction.user.id)
        await interaction.message.edit(
            file=discord.File(status_image, "pet_status.png")
        )

    @discord.ui.button(emoji="🎁", style=discord.ButtonStyle.grey)
    async def daily(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        if pet.daily is None or (datetime.now() - pet.daily) > timedelta(1):
            pet.wallet += 100
            pet.daily = datetime.now()
            pet.save()
            await interaction.message.reply(
                content="Otrzymano darmowe 100 coinów!",
                delete_after=5,
            )
        else:
            await interaction.message.reply(
                content="Otrzymałeś już darmowe 100 coinów, wróć jutro.",
                delete_after=5,
            )
        status_image = await generate_status(interaction.user.id)
        await interaction.message.edit(
            file=discord.File(status_image, "pet_status.png")
        )


class Tamagotchi(commands.Cog, name="📟 Tamagotchi"):
    def __init__(self, bot: Atorin):
        self.bot = bot
        self.check_pets_thirst.start()
        self.check_pets_hanger.start()
        self.check_pets_sleep.start()
        self.check_pets_health.start()
        self.foods = {
            "1": {"name": "🍎 Jabłko", "cost": 5, "points": 5},
            "2": {"name": "🍌 Banan", "cost": 5, "points": 5},
        }
        self.drinks = {
            "1": {"name": "🚰 Woda", "cost": 5, "points": 5},
            "2": {"name": "🧃 Sok", "cost": 10, "points": 7},
        }
        self.potions = {
            "1": {"name": "💊 Tabletka", "cost": 50, "points": 25},
            "2": {"name": "💉 Strzykawka", "cost": 200, "points": 100},
        }
        self.wallpapers = {"1": {"name": "Zwykła tapeta", "cost": 25}}
        self.hats = {"1": {"name": "Czapka z daszkiem", "cost": 50}}

    @tasks.loop(minutes=1)
    async def check_pets_thirst(self):
        for pet in database.tamagotchi.Pet.objects:
            if pet.thirst.state >= 5:
                pet.thirst.state -= randint(1, 5)
            else:
                pet.thirst.state = 0
            pet.save()

    @tasks.loop(minutes=2)
    async def check_pets_hanger(self):
        for pet in database.tamagotchi.Pet.objects:
            if pet.hunger.state >= 5:
                pet.hunger.state -= randint(1, 5)
            else:
                pet.hunger.state = 0
            pet.save()

    @tasks.loop(minutes=3)
    async def check_pets_sleep(self):
        for pet in database.tamagotchi.Pet.objects:
            if pet.sleep.in_bed:
                pet.sleep.state += randint(5, 10)
            else:
                if pet.sleep.state >= 5:
                    pet.sleep.state -= randint(1, 5)
                else:
                    pet.sleep.state = 0
            pet.save()

    @tasks.loop(hours=2)
    async def check_pets_health(self):
        for pet in database.tamagotchi.Pet.objects:
            if pet.thirst.state == 0:
                if pet.health.state >= 5:
                    pet.health.state -= randint(1, 5)
                else:
                    pet.health.state = 0
            if pet.hunger.state == 0:
                if pet.health.state >= 5:
                    pet.health.state -= randint(1, 5)
                else:
                    pet.health.state = 0
            if pet.sleep.state == 0 and not pet.sleep.in_bed:
                if pet.health.state >= 5:
                    pet.health.state -= randint(1, 5)
                else:
                    pet.health.state = 0
            pet.save()

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

    tamagotchi_settings = SlashCommandGroup("settings", "Ustawienia")
    tamagotchi_shop = SlashCommandGroup("shop", "Sklep")

    @tamagotchi_settings.command(
        description="Tworzy pupila", guild_ids=config["guild_ids"]
    )
    async def start(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        created: database.tamagotchi.Pet = database.tamagotchi.Pet(
            owner=ctx.author.id
        ).save()
        if created:
            embed = discord.Embed()
            embed.title = "Tworzenie pupila"
            embed.description = "✅ **Utworzono pupila! Możesz go odwiedzić wpisując komendę `/pet status`**."
            await ctx.send_followup(embed=embed)
        else:
            raise commands.CommandError("Nie udało się utworzyć pupila!")

    @tamagotchi_settings.command(
        description="Usuwa pupila", guild_ids=config["guild_ids"]
    )
    async def remove(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        embed = discord.Embed()
        embed.title = "Usuwanie pupila"
        embed.description = "❓ **Czy na pewno chcesz usunąć swojego pupila? Utracisz cały postęp oraz posiadane coiny oraz przedmioty.**\n**UWAGA! Ta czynność jest nieodwracalna!**"
        confirm_view = Confirm()
        message = await ctx.send_followup(embed=embed, view=confirm_view)
        await confirm_view.wait()
        if confirm_view.value is None:
            await message.delete()
        elif confirm_view.value:
            deleted: int = database.tamagotchi.Pet.objects(owner=ctx.author.id).delete()
            if deleted == 1:
                embed.description = "✅ **Usunięto pupila!**"
                await message.edit(embed=embed, view=None)
            else:
                raise commands.CommandError("Nie udało się usunąć pupila!")
        else:
            embed.description = "❌ Anulowano"
            await message.edit(embed=embed, view=None)

    @slash_command(
        description="Twój pupil",
        guild_ids=config["guild_ids"],
    )
    async def pet(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        img = await generate_status(ctx.author.id)
        embed = discord.Embed()
        embed.title = f"Pupil {ctx.author}"
        embed.set_image(url="attachment://pet_status.png")
        message = await ctx.send_followup(
            embed=embed, file=discord.File(img, "pet_status.png")
        )
        await message.edit(view=Pet(message))

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
        count: Option(int, "Wpisz ilość", min_value=1, default=1),
    ):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        for id in self.foods:
            item = self.foods[id]
            if item["name"] == food_name:
                embed = discord.Embed()
                embed.title = "Zakup jedzenia"
                embed.description = f"❓ **Czy na pewno chcesz kupić {item['name']}?**"
                embed.add_field(name="🔢 Ilość:", value=count)
                embed.add_field(name="🪙 Koszt:", value=item["cost"] * count)
                embed.add_field(
                    name="<:feed:949827709662527548> Jedzenie:",
                    value=f"+{item['points'] * count}",
                )
                confirm_view = Confirm()
                message = await ctx.send_followup(embed=embed, view=confirm_view)
                await confirm_view.wait()
                embed = discord.Embed()
                embed.title = "Zakup jedzenia"
                if confirm_view.value is None:
                    await message.delete()
                elif confirm_view.value:
                    if pet.wallet < item["cost"] * count:
                        embed.description = f"❌ **Nie posiadasz {item['cost'] * count} coinów, aby zakupić {count} sztuk {item['name']}!**"
                        return await message.edit(embed=embed, view=None)
                    try:
                        pet.foods[id] += count
                    except KeyError:
                        pet.foods[id] = count
                    pet.wallet -= item["cost"] * count
                    pet.save()
                    embed.description = f"✅ **Pomyślnie zakupiono {count} {item['name']} za {item['cost'] * count} coinów!**"
                else:
                    embed.description = "❌ **Anulowano zakup.**"
                await message.edit(embed=embed, view=None)

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
        count: Option(int, "Wpisz ilość", min_value=1, default=1),
    ):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        for id in self.drinks:
            item = self.drinks[id]
            if item["name"] == drink_name:
                embed = discord.Embed()
                embed.title = "Zakup napoju"
                embed.description = f"❓ **Czy na pewno chcesz kupić {item['name']}?**"
                embed.add_field(name="🔢 Ilość:", value=count)
                embed.add_field(name="🪙 Koszt:", value=item["cost"] * count)
                embed.add_field(
                    name="<:drink:949827709641572352> Nawodnienie:",
                    value=f"+{item['points'] * count}",
                )
                confirm_view = Confirm()
                message = await ctx.send_followup(embed=embed, view=confirm_view)
                await confirm_view.wait()
                embed = discord.Embed()
                embed.title = "Zakup napoju"
                if confirm_view.value is None:
                    await message.delete()
                elif confirm_view.value:
                    if pet.wallet < item["cost"] * count:
                        embed.description = f"❌ **Nie posiadasz {item['cost'] * count} coinów, aby zakupić {count} sztuk {item['name']}!**"
                        return await message.edit(embed=embed, view=None)
                    try:
                        pet.drinks[id] += count
                    except KeyError:
                        pet.drinks[id] = count
                    pet.wallet -= item["cost"] * count
                    pet.save()
                    embed.description = f"✅ **Pomyślnie zakupiono {count} {item['name']} za {item['cost'] * count} coinów!**"
                else:
                    embed.description = "❌ **Anulowano zakup.**"
                await message.edit(embed=embed, view=None)

    async def wallpapers_shop_searcher(self, ctx: discord.AutocompleteContext):
        return [
            item["name"]
            for item in self.wallpapers.values()
            if item["name"].lower().startswith(ctx.value.lower())
        ]

    @tamagotchi_shop.command(
        description="Kup tapety dla pupila", guild_ids=config["guild_ids"]
    )
    async def wallpapers(
        self,
        ctx: discord.ApplicationContext,
        wallpaper_name: Option(
            str, "Wybierz tapetę", autocomplete=wallpapers_shop_searcher
        ),
    ):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        for id in self.wallpapers:
            item = self.wallpapers[id]
            if item["name"] == wallpaper_name:
                embed = discord.Embed()
                embed.title = "Zakup tapety"
                if id in pet.wallpapers:
                    embed.description = f"❌ **Posiadasz już tę tapetę, sprawdź zakupione tapety komendą `/pet wallpapers`**"
                    return await ctx.send_followup(embed=embed)
                embed.description = f"❓ **Czy na pewno chcesz kupić {item['name']}?**"
                embed.add_field(name="🪙 Koszt:", value=item["cost"])
                confirm_view = Confirm()
                message = await ctx.send_followup(embed=embed, view=confirm_view)
                await confirm_view.wait()
                embed = discord.Embed()
                embed.title = "Zakup tapety"
                if confirm_view.value is None:
                    await message.delete()
                elif confirm_view.value:
                    if pet.wallet < item["cost"]:
                        embed.description = f"❌ **Nie posiadasz {item['cost']} coinów, aby zakupić {item['name']}!**"
                        return await message.edit(embed=embed, view=None)
                    pet.wallpapers.append(id)
                    pet.wallet -= item["cost"]
                    pet.save()
                    embed.description = f"✅ **Pomyślnie zakupiono {item['name']} za {item['cost']} coinów!**"
                else:
                    embed.description = "❌ **Anulowano zakup.**"
                await message.edit(embed=embed, view=None)

    async def potions_shop_searcher(self, ctx: discord.AutocompleteContext):
        return [
            item["name"]
            for item in self.potions.values()
            if item["name"].lower().startswith(ctx.value.lower())
        ]

    @tamagotchi_shop.command(
        description="Kup lekarstwa dla pupila",
        guild_ids=config["guild_ids"],
    )
    async def potions(
        self,
        ctx: discord.ApplicationContext,
        potion_name: Option(
            str, "Wybierz lekarstwo", autocomplete=potions_shop_searcher
        ),
        count: Option(int, "Wpisz ilość", min_value=1, default=1),
    ):
        await ctx.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=ctx.author.id
        ).first()
        for id in self.potions:
            item = self.potions[id]
            if item["name"] == potion_name:
                embed = discord.Embed()
                embed.title = "Zakup lekarstwa"
                embed.description = f"❓ **Czy na pewno chcesz kupić {item['name']}?**"
                embed.add_field(name="🔢 Ilość:", value=count)
                embed.add_field(name="🪙 Koszt:", value=item["cost"] * count)
                embed.add_field(
                    name="<:health:949827709666742312> Zdrowie:",
                    value=f"+{item['points'] * count}",
                )
                confirm_view = Confirm()
                message = await ctx.send_followup(embed=embed, view=confirm_view)
                await confirm_view.wait()
                embed = discord.Embed()
                embed.title = "Zakup lekarstwa"
                if confirm_view.value is None:
                    await message.delete()
                elif confirm_view.value:
                    if pet.wallet < item["cost"] * count:
                        embed.description = f"❌ **Nie posiadasz {item['cost'] * count} coinów, aby zakupić {count} sztuk {item['name']}!**"
                        return await message.edit(embed=embed, view=None)
                    try:
                        pet.potions[id] += count
                    except KeyError:
                        pet.potions[id] = count
                    pet.wallet -= item["cost"] * count
                    pet.save()
                    embed.description = f"✅ **Pomyślnie zakupiono {count} {item['name']} za {item['cost'] * count} coinów!**"
                else:
                    embed.description = "❌ **Anulowano zakup.**"
                await message.edit(embed=embed, view=None)

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

    @tamagotchi_shop.command(
        description="Przekaż coiny",
        guild_ids=config["guild_ids"],
    )
    async def give(
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
