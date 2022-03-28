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
import random
from typing import List
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
    if pet.hunger.state >= 100:
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
    if pet.thirst.state >= 100:
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
    if pet.sleep.state >= 100:
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
    if pet.health.state >= 100:
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
    if pet.wallpaper:
        pet_background = Image.open(f"assets/tamagotchi/wallpapers/{pet.wallpaper}.png")
    else:
        pet_background = Image.open("assets/tamagotchi/wallpapers/0.png")
    pet_image = Image.open("assets/tamagotchi/pet.png")
    pet_background.paste(pet_image, (0, 9), pet_image.split()[3])
    if pet.sleep.in_bed:
        sleep_background = Image.open("assets/tamagotchi/sleep_background.png")
        pet_background.paste(sleep_background, (0, 0), sleep_background.split()[3])
    template.paste(pet_background, (117, 117))
    template_draw = ImageDraw.Draw(template)
    template_draw.text(
        (960, 140),
        f"{100 if pet.hunger.state >= 100 else pet.hunger.state}",
        (255, 255, 255),
        ImageFont.truetype("assets/tamagotchi/apasih.ttf", 48),
    )
    template_draw.text(
        (960, 257),
        f"{100 if pet.thirst.state >= 100 else pet.thirst.state}",
        (255, 255, 255),
        ImageFont.truetype("assets/tamagotchi/apasih.ttf", 48),
    )
    template_draw.text(
        (960, 375),
        f"{100 if pet.sleep.state >= 100 else pet.sleep.state}",
        (255, 255, 255),
        ImageFont.truetype("assets/tamagotchi/apasih.ttf", 48),
    )
    template_draw.text(
        (960, 490),
        f"{100 if pet.health.state >= 100 else pet.health.state}",
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
        super().__init__(timeout=30)
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
                delete_after=5,
            )
        else:
            pet.hunger.state += item["points"]
        pet.save()
        await interaction.message.delete()
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
                delete_after=5,
            )
        else:
            pet.thirst.state += item["points"]
        pet.save()
        await interaction.message.delete()
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
                delete_after=5,
            )
        else:
            pet.health.state += item["points"]
        pet.save()
        await interaction.message.delete()
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
        await interaction.message.delete()
        self.view.stop()


class Pet(discord.ui.View):
    def __init__(self, message: discord.Message):
        super().__init__(timeout=60)
        self.message = message

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(view=self)

    @discord.ui.button(
        emoji="<:feed:956868052794900491>", style=discord.ButtonStyle.grey
    )
    async def foods(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        if pet.hunger.state == 100:
            await interaction.message.reply("Pupil nie jest głodny!", delete_after=5)
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
            delete_after=30,
        )
        await view.wait()
        status_image = await generate_status(interaction.user.id)
        await interaction.message.edit(
            file=discord.File(status_image, "pet_status.png")
        )

    @discord.ui.button(
        emoji="<:drink:956868053126250516>", style=discord.ButtonStyle.grey
    )
    async def drinks(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        if pet.thirst.state == 100:
            await interaction.message.reply("Pupil nie chce pić!", delete_after=5)
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
            delete_after=30,
        )
        await view.wait()
        status_image = await generate_status(interaction.user.id)
        await interaction.message.edit(
            file=discord.File(status_image, "pet_status.png")
        )

    @discord.ui.button(
        emoji="<:sleep:956868052996218951>", style=discord.ButtonStyle.grey
    )
    async def sleep(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        if pet.sleep.in_bed:
            pet.sleep.in_bed = False
            pet.save()
            await interaction.message.reply(content="Pupil się obudził", delete_after=5)
        else:
            if pet.sleep.state >= 100:
                await interaction.message.reply(
                    content="Pupil nie chce iść spać", delete_after=5
                )
                return
            pet.sleep.in_bed = True
            pet.save()
            await interaction.message.reply(content="Pupil zasnął!", delete_after=5)
        status_image = await generate_status(interaction.user.id)
        await interaction.message.edit(
            file=discord.File(status_image, "pet_status.png")
        )

    @discord.ui.button(
        emoji="<:health:956868053436616744>", style=discord.ButtonStyle.grey
    )
    async def potions(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        await interaction.response.defer()
        pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
            owner=interaction.user.id
        ).first()
        if pet.health.state == 100:
            await interaction.message.reply("Pupil nie jest chory!", delete_after=5)
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
        view = discord.ui.View(PotionDropdown(options))
        await interaction.message.reply(
            content="⬇️ Wybierz czym chcesz uleczyć pupila",
            view=view,
            delete_after=30,
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
            delete_after=30,
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
        else:
            await interaction.message.reply(
                content="❌ Otrzymałeś już darmowe 100 coinów, wróć jutro.",
                delete_after=5,
            )
        status_image = await generate_status(interaction.user.id)
        await interaction.message.edit(
            file=discord.File(status_image, "pet_status.png")
        )


def get_board_copy(board: List):
    dupeBoard = []
    for i in board:
        dupeBoard.append(i)
    return dupeBoard


def ttt_get_computer_move(view):
    for x in range(3):
        for y in range(3):
            board = get_board_copy(view.board)
            if board[y][x] == 0:
                board[y][x] = 1
                winner = view.check_board_winner(board)
                if winner == view.O:
                    return (y, x)
                else:
                    board[y][x] = 0
    for x in range(3):
        for y in range(3):
            board = get_board_copy(view.board)
            if board[y][x] == 0:
                board[y][x] = -1
                winner = view.check_board_winner(board)
                if winner == view.X:
                    return (y, x)
                else:
                    board[y][x] = 0
    board = get_board_copy(view.board)
    # check corners
    if board[0][0] == 0:
        return (0, 0)
    if board[0][2] == 0:
        return (0, 2)
    if board[2][0] == 0:
        return (2, 0)
    if board[2][2] == 0:
        return (2, 2)
    # check center
    if board[1][1] == 0:
        return (1, 1)
    # others
    other_moves = []
    if board[0][1] == 0:
        other_moves.append((0, 1))
    if board[1][0] == 0:
        other_moves.append((1, 0))
    if board[1][2] == 0:
        other_moves.append((1, 2))
    if board[2][1] == 0:
        other_moves.append((2, 1))
    if other_moves:
        return random.choice(other_moves)


class TicTacToeButton(discord.ui.Button["TicTacToe"]):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction):
        content = "Kółko i krzyżyk"
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        self.style = discord.ButtonStyle.danger
        self.label = "X"
        view.board[self.y][self.x] = view.X

        try:
            y, x = ttt_get_computer_move(view)
            view.board[y][x] = view.O
            for button in view.children:
                if button.x == x and button.y == y:
                    button.label = "O"
        except TypeError:
            pass

        self.disabled = True
        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = "Wygrana! +50 coinów"
                pet: database.tamagotchi.Pet = database.tamagotchi.Pet.objects(
                    owner=interaction.user.id
                ).first()
                pet.wallet += 50
                pet.save()
            elif winner == view.O:
                content = "Przegrana!"
            else:
                content = "Remis!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


class TicTacToe(discord.ui.View):
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    def check_board_winner(self, board=None):
        if not board:
            board = self.board
        for across in board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        for line in range(3):
            value = board[0][line] + board[1][line] + board[2][line]
            if value == -3:
                return self.X
            elif value == 3:
                return self.O

        diag = board[0][2] + board[1][1] + board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = board[0][0] + board[1][1] + board[2][2]
        if diag == -3:
            return self.X
        elif diag == 3:
            return self.O

        if all(i != 0 for row in board for i in row):
            return self.Tie

        return None


class FoodShopDropdown(discord.ui.Select):
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
        embed = discord.Embed()
        id = self.values[0]
        item = foods[id]
        if pet.wallet < item["cost"]:
            embed.description = f"❌ **Nie posiadasz {item['cost']} coinów, aby zakupić {item['name']}!**"
            return await interaction.message.reply(embed=embed, delete_after=5)
        try:
            pet.foods[id] += 1
        except KeyError:
            pet.foods[id] = 1
        pet.wallet -= item["cost"]
        pet.save()
        embed.description = (
            f"✅ **Pomyślnie zakupiono {item['name']} za {item['cost']} coinów!**"
        )
        await interaction.message.edit(embed=embed, view=None)


class DrinkShopDropdown(discord.ui.Select):
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
        embed = discord.Embed()
        id = self.values[0]
        item = drinks[id]
        if pet.wallet < item["cost"]:
            embed.description = f"❌ **Nie posiadasz {item['cost']} coinów, aby zakupić {item['name']}!**"
            return await interaction.message.reply(embed=embed, delete_after=5)
        try:
            pet.drinks[id] += 1
        except KeyError:
            pet.drinks[id] = 1
        pet.wallet -= item["cost"]
        pet.save()
        embed.description = (
            f"✅ **Pomyślnie zakupiono {item['name']} za {item['cost']} coinów!**"
        )
        await interaction.message.edit(embed=embed, view=None)


class WallpaperShopDropdown(discord.ui.Select):
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
        embed = discord.Embed()
        id = self.values[0]
        item = wallpapers[id]
        if id in pet.wallpapers:
            embed.description = f"❌ **Posiadasz już tę tapetę!**"
            return await interaction.message.reply(embed=embed, delete_after=5)
        if pet.wallet < item["cost"]:
            embed.description = f"❌ **Nie posiadasz {item['cost']} coinów, aby zakupić {item['name']}!**"
            return await interaction.message.reply(embed=embed, delete_after=5)
        pet.wallpapers.append(id)
        pet.wallet -= item["cost"]
        pet.save()
        embed.description = (
            f"✅ **Pomyślnie zakupiono {item['name']} za {item['cost']} coinów!**"
        )
        await interaction.message.edit(embed=embed, view=None)


class PotionShopDropdown(discord.ui.Select):
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
        embed = discord.Embed()
        id = self.values[0]
        item = potions[id]
        if pet.wallet < item["cost"]:
            embed.description = f"❌ **Nie posiadasz {item['cost']} coinów, aby zakupić {item['name']}!**"
            return await interaction.message.reply(embed=embed, delete_after=5)
        try:
            pet.potions[id] += 1
        except KeyError:
            pet.potions[id] = 1
        pet.wallet -= item["cost"]
        pet.save()
        embed.description = (
            f"✅ **Pomyślnie zakupiono {item['name']} za {item['cost']} coinów!**"
        )
        await interaction.message.edit(embed=embed, view=None)


class Tamagotchi(commands.Cog, name="📟 Tamagotchi"):
    def __init__(self, bot: Atorin):
        self.bot = bot
        self.check_pets_thirst.start()
        self.check_pets_hanger.start()
        self.check_pets_sleep.start()
        self.check_pets_health.start()

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
                if pet.sleep.state >= 100:
                    pet.sleep.state = 100
                else:
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

    tamagotchi_settings = SlashCommandGroup(
        "settings", "Ustawienia", guild_ids=config["guild_ids"]
    )
    tamagotchi_shop = SlashCommandGroup("shop", "Sklep", guild_ids=config["guild_ids"])
    tamagotchi_games = SlashCommandGroup("games", "Gry", guild_ids=config["guild_ids"])

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

    @tamagotchi_shop.command(
        description="Kup jedzenie dla pupila",
        guild_ids=config["guild_ids"],
    )
    async def food(
        self,
        ctx: discord.ApplicationContext,
    ):
        await ctx.defer()
        embed = discord.Embed(title="<:feed:956868052794900491> Jedzenie")
        embed.description = ""
        for item in foods.values():
            embed.description += f"**{item['name']}** | -{item['cost']} 🪙 | +{item['points']} <:feed:956868052794900491>\n"
        options: list[discord.SelectOption] = []
        for id in foods:
            item = foods[id]
            options.append(discord.SelectOption(label=item["name"], value=id))
        view = discord.ui.View(FoodShopDropdown(options), timeout=30)
        message = await ctx.send_followup(embed=embed, view=view)
        timed_out = view.wait()
        if timed_out:
            await message.delete()

    @tamagotchi_shop.command(
        description="Kup napój dla pupila",
        guild_ids=config["guild_ids"],
    )
    async def drink(
        self,
        ctx: discord.ApplicationContext,
    ):
        await ctx.defer()
        embed = discord.Embed(title="<:drink:956868053126250516> Napoje")
        embed.description = ""
        for item in drinks.values():
            embed.description += f"**{item['name']}** | -{item['cost']} 🪙 | +{item['points']} <:drink:956868053126250516>\n"
        options: list[discord.SelectOption] = []
        for id in drinks:
            item = drinks[id]
            options.append(discord.SelectOption(label=item["name"], value=id))
        view = discord.ui.View(DrinkShopDropdown(options), timeout=30)
        message = await ctx.send_followup(embed=embed, view=view)
        timed_out = view.wait()
        if timed_out:
            await message.delete()

    @tamagotchi_shop.command(
        description="Kup tapety dla pupila", guild_ids=config["guild_ids"]
    )
    async def wallpapers(
        self,
        ctx: discord.ApplicationContext,
    ):
        await ctx.defer()
        embed = discord.Embed(title="🖼 Tapety")
        embed.description = ""
        for item in wallpapers.values():
            embed.description += f"**{item['name']}** | -{item['cost']} 🪙 \n"
        options: list[discord.SelectOption] = []
        for id in wallpapers:
            item = wallpapers[id]
            options.append(discord.SelectOption(label=item["name"], value=id))
        view = discord.ui.View(WallpaperShopDropdown(options), timeout=30)
        message = await ctx.send_followup(embed=embed, view=view)
        timed_out = view.wait()
        if timed_out:
            await message.delete()

    @tamagotchi_shop.command(
        description="Kup lekarstwa dla pupila",
        guild_ids=config["guild_ids"],
    )
    async def potions(
        self,
        ctx: discord.ApplicationContext,
    ):
        await ctx.defer()
        embed = discord.Embed(title="<:health:956868053436616744> Lekarstwa")
        embed.description = ""
        for item in potions.values():
            embed.description += f"**{item['name']}** | -{item['cost']} 🪙 | +{item['points']} <:health:956868053436616744>\n"
        options: list[discord.SelectOption] = []
        for id in potions:
            item = potions[id]
            options.append(discord.SelectOption(label=item["name"], value=id))
        view = discord.ui.View(PotionShopDropdown(options), timeout=30)
        message = await ctx.send_followup(embed=embed, view=view)
        timed_out = view.wait()
        if timed_out:
            await message.delete()

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

    @tamagotchi_games.command(
        description="Kółko i krzyżyk", guild_ids=config["guild_ids"]
    )
    async def tictactoe(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await ctx.send_followup("Kółko i krzyżyk:", view=TicTacToe())


def setup(bot):
    bot.add_cog(Tamagotchi(bot))
