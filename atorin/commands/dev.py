import os
import re
import io
import zlib
import discord
from discord.commands import Option, slash_command, OptionChoice, SlashCommandGroup
from discord.ext import commands
from discord.ui import Modal, InputText
import httpx
import base64

from atorin.bot import Atorin
from ..config import config


docs = {
    "python": "https://docs.python.org/3",
    "py-cord": "https://docs.pycord.dev/en/master",
}


def finder(text, collection, *, key=None, lazy=True):
    suggestions = []
    text = str(text)
    pat = ".*?".join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)
    for item in collection:
        to_search = key(item) if key else item
        r = regex.search(to_search)
        if r:
            suggestions.append((len(r.group()), r.start(), item))

    def sort_key(tup):
        if key:
            return tup[0], tup[1], key(tup[2])
        return tup

    if lazy:
        return (z for _, _, z in sorted(suggestions, key=sort_key))
    else:
        return [z for _, _, z in sorted(suggestions, key=sort_key)]


# Class SphinxObjectFileReader is taken from TechStruck/TechStruck-Bot
# https://github.com/TechStruck/TechStruck-Bot/blob/main/bot/utils/rtfm.py
class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode("utf-8")

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b""
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b"\n")
            while pos != -1:
                yield buf[:pos].decode("utf-8")
                buf = buf[pos + 1 :]
                pos = buf.find(b"\n")

    def parse_object_inv(self, url):
        # key: URL
        # n.b.: key doesn't have `discord` or `discord.ext.commands` namespaces
        result = {}

        # first line is version info
        inv_version = self.readline().rstrip()

        if inv_version != "# Sphinx inventory version 2":
            raise RuntimeError("Invalid objects.inv file version.")

        # next line is "# Project: <name>"
        # then after that is "# Version: <version>"
        projname = self.readline().rstrip()[11:]
        version = self.readline().rstrip()[11:]

        # next line says if it's a zlib header
        line = self.readline()
        if "zlib" not in line:
            raise RuntimeError("Invalid objects.inv file, not z-lib compatible.")

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r"(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)")
        for line in self.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(":")
            if directive == "py:module" and name in result:
                # From the Sphinx Repository:
                # due to a bug in 1.1 and below,
                # two inventory entries are created
                # for Python modules, and the first
                # one is correct
                continue

            # Most documentation pages have a label
            if directive == "std:doc":
                subdirective = "label"

            if location.endswith("$"):
                location = location[:-1] + name

            key = name if dispname == "-" else dispname
            prefix = f"{subdirective}:" if domain == "std" else ""

            if projname == "discord.py" or projname == "Pycord":
                key = key.replace("discord.ext.commands.", "").replace("discord.", "")

            result[f"{prefix}{key}"] = os.path.join(url, location)

        return result


class Dev(commands.Cog, name="🧑‍💻 Programowanie"):
    def __init__(self, bot: Atorin):
        self.bot = bot
        self.rtfm_cache = {}

    @slash_command(
        description="Informations about libraries from PyPi",
        description_localizations={"pl": "Informacje o bibliotekach z PyPi"},
        guild_ids=config["guild_ids"],
    )
    async def pypi(
        self,
        ctx: discord.ApplicationContext,
        package: Option(
            str,
            name="library",
            name_localizations={"pl": "biblioteka"},
            description="Library name",
            description_localizations={"pl": "Nazwa biblioteki"},
        ),
    ):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"https://pypi.org/pypi/{package}/json",
                headers={"User-agent": "Atorin"},
            )
        if r.status_code == 200:
            data = r.json()
            embed = discord.Embed()
            embed.title = f"PyPi - {data['info']['name']}"
            embed.add_field(
                name=data["info"]["summary"]
                if data["info"]["summary"]
                else f"{'Brak opisu' if ctx.interaction.locale == 'pl' else 'No description'}",
                value=f"```bash\npip install {data['info']['name']}```",
                inline=False,
            )
            embed.add_field(
                name="👨‍💻 Autor" if ctx.interaction.locale == "pl" else "👨‍💻 Author",
                value=data["info"]["author"]
                if data["info"]["author"]
                else f"{'Nieznany' if ctx.interaction.locale == 'pl' else 'Unknown'}",
            )
            embed.add_field(
                name="⚙️ Wersja" if ctx.interaction.locale == "pl" else "⚙️ Version",
                value=data["info"]["version"]
                if data["info"]["version"]
                else f"{'Nieznana' if ctx.interaction.locale == 'pl' else 'Unknown'}",
            )
            embed.add_field(
                name="📜 Licencja" if ctx.interaction.locale == "pl" else "📜 License",
                value=data["info"]["license"]
                if data["info"]["license"]
                else f"{'Brak' if ctx.interaction.locale == 'pl' else 'Missing'}",
            )
            if "project_urls" in data["info"]:
                links = []
                if "Documentation" in data["info"]["project_urls"]:
                    links.append(
                        f"[{'Dokumentacja' if ctx.interaction.locale == 'pl' else 'Documentation'}]({data['info']['project_urls']['Documentation']})"
                    )
                if "Homepage" in data["info"]["project_urls"]:
                    links.append(
                        f"[{'Strona' if ctx.interaction.locale == 'pl' else 'Website'}]({data['info']['project_urls']['Homepage']})"
                    )
                if "package_url" in data["info"]:
                    links.append(f"[PyPi]({data['info']['package_url']})")
                embed.add_field(
                    name="🔗 Linki" if ctx.interaction.locale == "pl" else "🔗 Links",
                    value=f"**{' | '.join(links)}**",
                )
            await ctx.send_followup(embed=embed)
        elif r.status_code == 404:
            raise commands.BadArgument(
                "Nie znaleziono biblioteki o podanej nazwie!"
                if ctx.interaction.locale == "pl"
                else "Library with the given name was not found!"
            )
        else:
            raise commands.CommandError(r.text)

    @slash_command(
        description="Informations about libraries from NPM",
        description_localizations={"pl": "Informacje o bibliotekach z NPM"},
        guild_ids=config["guild_ids"],
    )
    async def npm(
        self,
        ctx: discord.ApplicationContext,
        package: Option(
            str,
            name="library",
            name_localizations={"pl": "biblioteka"},
            description="Library name",
            description_localizations={"pl": "Nazwa biblioteki"},
        ),
    ):
        await ctx.defer()
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"https://registry.npmjs.org/{package}/",
                headers={"User-agent": "Atorin"},
            )
        if r.status_code == 200:
            data = r.json()
            embed = discord.Embed()
            embed.title = f"NPM - {data['name']}"
            embed.add_field(
                name=data["description"]
                if data["description"]
                else f"{'Brak opisu' if ctx.interaction.locale == 'pl' else 'No description'}",
                value=f"```bash\nnpm i {data['name']}```",
                inline=False,
            )
            if "author" in data:
                embed.add_field(
                    name="👨‍💻 Autor" if ctx.interaction.locale == "pl" else "👨‍💻 Author",
                    value=data["author"] if type(data["author"]) is str else data["author"]["name"],
                )
            embed.add_field(
                name="⚙️ Wersja" if ctx.interaction.locale == "pl" else "⚙️ Version", value=data["dist-tags"]["latest"]
            )
            embed.add_field(
                name="📜 Licencja" if ctx.interaction.locale == "pl" else "📜 License",
                value=data["license"] if data["license"] else "Brak",
            )
            links = []
            if "homepage" in data:
                links.append(f"[{'Strona' if ctx.interaction.locale == 'pl' else 'Website'}]({data['homepage']})")
            links.append(f"[NPM](https://npmjs.com/package/{data['name']})")
            embed.add_field(
                name="🔗 Linki" if ctx.interaction.locale == "pl" else "🔗 Links",
                value=f"**{' | '.join(links)}**",
            )
            await ctx.send_followup(embed=embed)
        elif r.status_code == 404:
            raise commands.BadArgument(
                "Nie znaleziono biblioteki o podanej nazwie!"
                if ctx.interaction.locale == "pl"
                else "Library with the given name was not found!"
            )
        else:
            raise commands.CommandError(r.text)

    @slash_command(
        description="Search through libraries documentation for Python",
        description_localizations={"pl": "Wyszukiwanie w dokumentacjach bibliotek do Pythona"},
        guild_ids=config["guild_ids"],
    )
    async def rtfm(
        self,
        ctx: discord.ApplicationContext,
        package: Option(
            str,
            name="library",
            name_localizations={"pl": "biblioteka"},
            description="Library name",
            description_localizations={"pl": "Nazwa biblioteki"},
        ),
        term: Option(
            str,
            name="phrase",
            name_localizations={"pl": "fraza"},
            description="Type what you want to find",
            description_localizations={"pl": "Wpisz, co chcesz znaleźć"},
        ),
    ):
        package = package.lower()
        await ctx.defer()
        embed = discord.Embed()
        embed.title = "Znalezione w dokumentacji"
        async with httpx.AsyncClient() as client:
            pypi = await client.get(
                f"https://pypi.org/pypi/{package}/json",
                headers={"User-agent": "Atorin"},
            )
        if pypi.status_code == 200:
            data = pypi.json()
            embed.add_field(
                name="🔤 Biblioteka" if ctx.interaction.locale == "pl" else "🔤 Package", value=data["info"]["name"]
            )
            embed.add_field(
                name="⚙️ Wersja" if ctx.interaction.locale == "pl" else "⚙️ Version", value=data["info"]["version"]
            )
        else:
            embed.add_field(name="🔤 Biblioteka" if ctx.interaction.locale == "pl" else "🔤 Package", value=package)
        if not self.rtfm_cache.get(package):
            url = docs.get(package)
            if not url:
                if "project_urls" in data["info"] and "Documentation" in data["info"]["project_urls"]:
                    url = data["info"]["project_urls"]["Documentation"]
                    if "readthedocs.io" in url and not "/en/latest" in url:
                        url = os.path.join(url, "en", "latest")
                else:
                    url = f"https://{package}.readthedocs.io/en/latest/"
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    os.path.join(url, "objects.inv"),
                    headers={"User-agent": "Atorin"},
                )
            if r.status_code == 200:
                self.rtfm_cache[package] = SphinxObjectFileReader(r.content).parse_object_inv(url)
            elif r.status_code == 404:
                raise commands.BadArgument(
                    "Nie znaleziono dokumentacji!" if ctx.interaction.locale == "pl" else "Documentation not found!"
                )
            else:
                raise commands.CommandError(
                    f"Wystąpił błąd przy pobieraniu dokumentacji! ({r.status_code})"
                    if ctx.interaction.locale == "pl"
                    else f"Error has occurred while retrieving documentation! ({r.status_code})"
                )
        cache = self.rtfm_cache.get(package)
        results = finder(term, list(cache.items()), key=lambda x: x[0], lazy=False)[:5]
        if results:
            embed.description = "\n".join([f"[`{key}`]({url})" for key, url in results])
        else:
            embed.description = "Brak wyników wyszukiwania" if ctx.interaction.locale == "pl" else "No search results"
        await ctx.send_followup(embed=embed)

    @slash_command(
        description="Execute code snippet",
        description_localizations={"pl": "Uruchamianie kodu"},
        guild_ids=config["guild_ids"],
    )
    async def exec(
        self,
        ctx: discord.ApplicationContext,
        language: Option(
            str,
            name="language",
            name_localizations={"pl": "język"},
            description="Select programming language of your code snippet",
            description_localizations={"pl": "Wybierz język programowania"},
            choices=[
                OptionChoice(name="Bash", value="bash"),
                OptionChoice(name="C#", value="csharp"),
                OptionChoice(name="C", value="c"),
                OptionChoice(name="C++", value="c++"),
                OptionChoice(name="Go", value="go"),
                OptionChoice(name="Java", value="java"),
                OptionChoice(name="JavaScript", value="javascript"),
                OptionChoice(name="PHP", value="php"),
                OptionChoice(name="PowerShell", value="powershell"),
                OptionChoice(name="Python", value="python"),
                OptionChoice(name="Rust", value="rust"),
                OptionChoice(name="Ruby", value="ruby"),
                OptionChoice(name="TypeScript", value="typescript"),
            ],
        ),
    ):
        class ExecModal(Modal):
            def __init__(self) -> None:
                super().__init__("Uruchamianie kodu" if ctx.interaction.locale == "pl" else "Execute code snippet")
                self.add_item(
                    InputText(
                        label="Twój kod" if ctx.interaction.locale == "pl" else "Your code",
                        placeholder="print('Hello world!')",
                        style=discord.InputTextStyle.multiline,
                    )
                )

            async def callback(self, interaction: discord.Interaction):
                async with httpx.AsyncClient() as client:
                    r = await client.post(
                        "https://emkc.org/api/v1/piston/execute",
                        json={
                            "language": language,
                            "source": self.children[0].value,
                        },
                    )
                if r.status_code != 200:
                    raise commands.CommandError(r.text)
                data = r.json()
                embed = discord.Embed()
                embed.title = (
                    f"Uruchamianie kodu {language.capitalize()}"
                    if ctx.interaction.locale == "pl"
                    else f"Executing code {language.capitalize()}"
                )
                result: str = (
                    data["output"][:4000]
                    if data["output"]
                    else f"{'Program wykonany pomyślnie' if ctx.interaction.locale == 'pl' else 'Code executed successfully'}"
                )
                embed.description = f"```{result}```"
                await interaction.response.send_message(embeds=[embed])

        modal = ExecModal()
        await ctx.interaction.response.send_modal(modal)

    base64_group = SlashCommandGroup(
        name="base64",
        description="Encode/Decode Base64",
        description_localizations={"pl": "Kodowanie/Dekodowanie tekstu/ciągu w Base64"},
        guild_ids=config["guild_ids"],
    )

    @base64_group.command(
        name="encode",
        name_localizations={"pl": "kodowanie"},
        description="Encode text in Base64",
        description_localizations={"pl": "Kodowanie tekstu w Base64"},
    )
    async def base64_encode(
        self,
        ctx: discord.ApplicationContext,
        content: Option(
            str,
            name="text",
            name_localizations={"pl": "tekst"},
            description="Type text you want to encode",
            description_localizations={"pl": "Wpisz tekst, który chcesz zakodować"},
        ),
    ):
        await ctx.defer()
        embed = discord.Embed()
        embed.title = "Base64"
        encoded = base64.b64encode(content.encode("utf-8", "ignore")).decode("utf-8", "ignore")
        embed.add_field(
            name="📋 Tekst" if ctx.interaction.locale == "pl" else "📋 Text", value=f"```{content}```", inline=False
        )
        embed.add_field(name="🔠 Base64", value=f"```{encoded}```", inline=False)
        await ctx.send_followup(embed=embed)

    @base64_group.command(
        name="decode",
        name_localizations={"pl": "dekodowanie"},
        description="Decode from Base64",
        description_localizations={"pl": "Dekodowanie Base64"},
    )
    async def base64_decode(
        self,
        ctx: discord.ApplicationContext,
        content: Option(
            str,
            name="text",
            name_localizations={"pl": "text"},
            description="Type or paste text you want to decode",
            description_localizations={"pl": "Podaj tekst, który chcesz dekodować"},
        ),
    ):
        await ctx.defer()
        embed = discord.Embed()
        embed.title = "Base64"
        decoded = base64.b64decode(content.encode("utf-8", "ignore")).decode("utf-8", "ignore")
        embed.add_field(name="🔠 Base64", value=f"```{content}```", inline=False)
        embed.add_field(
            name="📋 Tekst" if ctx.interaction.locale == "pl" else "📋 Text", value=f"```{decoded}```", inline=False
        )
        await ctx.send_followup(embed=embed)


def setup(bot):
    bot.add_cog(Dev(bot))
