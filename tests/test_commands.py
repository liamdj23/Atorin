import distest
import sys

test_collector = distest.TestCollector()


@test_collector()
async def test_ping(interface):
    await interface.assert_reply_contains("&ping", "Pong!")


if __name__ == '__main__':
    distest.run_dtest_bot(sys.argv, test_collector)
