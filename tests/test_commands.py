import distest
import sys
import random
import string

test_collector = distest.TestCollector()


@test_collector()
async def test_ping(interface):
    await interface.assert_reply_contains("&ping", "Pong!")


@test_collector()
async def test_shiba(interface):
    await interface.assert_reply_has_image("&shiba")


@test_collector()
async def test_tvp_no_argument(interface):
    await interface.assert_reply_contains("&tvp", "❌ Poprawne użycie: `&tvp <tekst>`")


@test_collector()
async def test_tvp_bad_argument(interface):
    random_text = ''.join(random.choices(string.ascii_letters, k=49))
    await interface.assert_reply_contains("&tvp " + random_text, "❌ Zbyt duża ilość znaków, limit to 48 znaków.")


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
async def test_figlet_no_argument(interface):
    await interface.assert_reply_contains("&figlet", "❌ Poprawne użycie: `&figlet <tekst>`")


@test_collector()
async def test_figlet(interface):
    await interface.assert_reply_contains("&figlet test", "```")


@test_collector()
async def test_commit(interface):
    await interface.assert_reply_contains("&commit", "git commit -m")


@test_collector()
async def test_achievement_no_argument(interface):
    await interface.assert_reply_contains("&achievement", "❌ Poprawne użycie: `&achievement <tekst>`")


@test_collector()
async def test_achievement_bad_argument(interface):
    random_text = ''.join(random.choices(string.ascii_letters, k=26))
    await interface.assert_reply_contains("&achievement " + random_text, "❌ Zbyt duża ilość znaków, limit to 25 znaków.")


@test_collector()
async def test_achievement(interface):
    await interface.assert_reply_has_image("&achievement test")


@test_collector()
async def test_kick_no_argument(interface):
    await interface.assert_reply_contains("&kick", "❌ Poprawne użycie: &kick <użytkownik>")


@test_collector()
async def test_kick_bad_argument(interface):
    random_text = ''.join(random.choices(string.ascii_letters, k=15))
    await interface.assert_reply_contains("&kick " + random_text, "❌ Nie znaleziono użytkownika o podanej nazwie.")


@test_collector()
async def test_ban_no_argument(interface):
    await interface.assert_reply_contains("&ban", "❌ Poprawne użycie: &ban <użytkownik> [powód]")


@test_collector()
async def test_ban_bad_argument(interface):
    random_text = ''.join(random.choices(string.ascii_letters, k=15))
    await interface.assert_reply_contains("&ban " + random_text, "❌ Nie znaleziono użytkownika o podanej nazwie.")


@test_collector()
async def test_unban_no_argument(interface):
    await interface.assert_reply_contains("&unban", "❌ Poprawne użycie: &unban <użytkownik>")


@test_collector()
async def test_unban_bad_argument(interface):
    random_text = ''.join(random.choices(string.ascii_letters, k=15))
    await interface.assert_reply_contains("&unban " + random_text, "❌ Nie znaleziono użytkownika na liście zbanowanych.")


@test_collector()
async def test_avatar(interface):
    await interface.assert_reply_has_image("&avatar AtorinBotTest")


if __name__ == '__main__':
    distest.run_dtest_bot(sys.argv, test_collector)
