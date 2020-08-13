import distest
import sys

test_collector = distest.TestCollector()


@test_collector()
async def test_ping(interface):
    await interface.assert_reply_contains("&ping", "Pong!")


@test_collector()
async def test_shiba(interface):
    await interface.assert_reply_has_image("&shiba")

if __name__ == '__main__':
    distest.run_dtest_bot(sys.argv, test_collector)
