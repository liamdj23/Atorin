import distest
import sys
from discord import Embed

test_collector = distest.TestCollector()


@test_collector()
async def test_shiba(interface):
    await interface.assert_reply_has_image("&shiba")


@test_collector()
async def test_tvp(interface):
    await interface.assert_reply_has_image("&tvp test")


@test_collector()
async def test_cat(interface):
    await interface.assert_reply_has_image("&cat")


@test_collector()
async def test_fox(interface):
    await interface.assert_reply_has_image("&fox")


@test_collector()
async def test_figlet(interface):
    await interface.assert_reply_contains("&figlet test", "```")


@test_collector()
async def test_commit(interface):
    await interface.assert_reply_contains("&commit", "git commit -m")


@test_collector()
async def test_achievement(interface):
    await interface.assert_reply_has_image("&achievement test")


@test_collector()
async def test_avatar(interface):
    await interface.assert_reply_has_image("&avatar AtorinBotTest")


@test_collector()
async def test_minecraft_skin(interface):
    await interface.assert_reply_has_image("&mc skin liamdj23")


@test_collector()
async def test_minecraft_server(interface):
    embed = (Embed(
        title="Status serwera Minecraft: mojemc.pl",
        color=0xc4c3eb)
    )
    interface.assert_reply_embed_equals("&mc srv mojemc.pl", embed)


if __name__ == '__main__':
    distest.run_dtest_bot(sys.argv, test_collector)
