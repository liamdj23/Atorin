import distest
import os

test_collector = distest.TestCollector()


@test_collector()
async def test_ping(interface):
    await interface.assert_reply_contains("&ping", "Pong!")


if __name__ == '__main__':
    distest.run_command_line_bot(
        os.environ["TARGET"],
        os.environ["TESTER"],
        "all",
        615868692818952193,
        True,
        test_collector,
        10
    )
