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

if __name__ == '__main__':
    distest.run_dtest_bot(sys.argv, test_collector)
