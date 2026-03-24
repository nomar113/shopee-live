import logging
import re
import time

from ADB import ADB
from vision import extract_text_from_region, find_template

logger = logging.getLogger(__name__)

SCREENSHOT_PATH = "./img/screenshot.png"
COIN_TEMPLATE_PATH = "./img/lives/coin_v2.png"
CLAIM_BUTTON_TEMPLATE_PATH = "./img/lives/claim_buttom_v2.png"

COIN_THRESHOLD = 0.95
CLAIM_BUTTON_THRESHOLD = 0.80

LIVE_HOME_X = 560
LIVE_HOME_Y = 147

TIMER_REGION_X = 750
TIMER_REGION_Y = 200
TIMER_REGION_W = 285
TIMER_REGION_H = 430

CLAIM_VALIDATION_X = 207
CLAIM_VALIDATION_Y = 1854
CLAIM_VALIDATION_W = 680
CLAIM_VALIDATION_H = 100

MAX_TIMER_MINUTES = 15
BUTTON_LOAD_DELAY = 7


class Live:
    """Gerencia interação com lives da Shopee para coleta de moedas."""

    def __init__(self, adb: ADB) -> None:
        self._adb = adb

    def click_live_home(self) -> None:
        """Toca no botão de lives na tela inicial."""
        ADB.tap(LIVE_HOME_X, LIVE_HOME_Y)

    def next_live(self) -> None:
        """Rola para a próxima live."""
        self._adb.scroll_up()

    def wait_buttons_load(self) -> None:
        """Aguarda carregamento dos botões na live."""
        time.sleep(BUTTON_LOAD_DELAY)

    def has_coin(self) -> bool:
        """Verifica se há moeda disponível na live atual."""
        self._adb.capture_screenshot()
        matches = find_template(SCREENSHOT_PATH, COIN_TEMPLATE_PATH, COIN_THRESHOLD)
        return len(matches) > 0

    def wait_to_receive_coins(self) -> None:
        """Lê o timer de countdown via OCR e aguarda o tempo indicado."""
        text = extract_text_from_region(
            SCREENSHOT_PATH,
            TIMER_REGION_X,
            TIMER_REGION_Y,
            TIMER_REGION_W,
            TIMER_REGION_H,
        )
        match = re.search(r"(\d{1,2}):(\d{2})", text)
        if not match:
            return

        minutes = int(match.group(1))
        seconds = int(match.group(2))

        if minutes > MAX_TIMER_MINUTES:
            minutes = 0

        total_seconds = minutes * 60 + seconds
        logger.info("Esperando %d segundos...", total_seconds)
        time.sleep(total_seconds)

    def claim_coin(self) -> None:
        """Tenta coletar a moeda e valida o resultado."""
        self._adb.capture_screenshot()
        matches = find_template(SCREENSHOT_PATH, CLAIM_BUTTON_TEMPLATE_PATH, CLAIM_BUTTON_THRESHOLD)

        if matches:
            first = matches[0]
            ADB.tap(first.x, first.y)

        self._validate_claim()

    def _validate_claim(self) -> None:
        """Verifica se o resgate falhou e rola para próxima live se necessário."""
        text = extract_text_from_region(
            SCREENSHOT_PATH,
            CLAIM_VALIDATION_X,
            CLAIM_VALIDATION_Y,
            CLAIM_VALIDATION_W,
            CLAIM_VALIDATION_H,
        )
        if re.search(r"Resgate falhou", text):
            self._adb.scroll_up()
