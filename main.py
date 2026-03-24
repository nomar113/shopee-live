import asyncio
import logging

from ADB import ADB
from lives import Live

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MAX_SCROLLS_BEFORE_RESET = 10


async def main_loop(live: Live) -> None:
    """Loop principal que percorre lives coletando moedas."""
    scroll_count = 0
    while True:
        live.claim_coin()

        if not live.has_coin():
            live.next_live()
            live.wait_buttons_load()
            scroll_count += 1
            if scroll_count > MAX_SCROLLS_BEFORE_RESET:
                live.click_live_home()
                scroll_count = 0
        else:
            live.wait_to_receive_coins()
            live.claim_coin()

        await asyncio.sleep(0.1)


async def main() -> None:
    adb = ADB()
    live = Live(adb)
    await main_loop(live)


if __name__ == "__main__":
    asyncio.run(main())
