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
    iteration = 0
    while True:
        iteration += 1
        logger.info("=== Iteração %d (scrolls: %d/%d) ===", iteration, scroll_count, MAX_SCROLLS_BEFORE_RESET)

        if live.is_on_watch_earn_screen():
            live.back_to_lives()
            scroll_count = 0
            await asyncio.sleep(2)
            continue

        live.claim_coin()

        if not live.has_coin():
            logger.info("Sem moeda disponível — scrollando para próxima live")
            live.next_live()
            live.wait_buttons_load()
            scroll_count += 1
            if scroll_count > MAX_SCROLLS_BEFORE_RESET:
                logger.info("Limite de scrolls atingido (%d) — resetando para tela inicial", MAX_SCROLLS_BEFORE_RESET)
                live.click_live_home()
                scroll_count = 0
        else:
            logger.info("Moeda disponível — aguardando timer para coletar")
            live.wait_to_receive_coins()
            live.claim_coin()

        await asyncio.sleep(0.1)


async def main() -> None:
    adb = ADB()
    live = Live(adb)
    await main_loop(live)


if __name__ == "__main__":
    asyncio.run(main())
