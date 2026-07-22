import logging
import re
import time

from ADB import ADB
from vision import extract_text_from_region, find_template

logger = logging.getLogger(__name__)

SCREENSHOT_PATH = "./img/screenshot.png"
COIN_TEMPLATE_PATH = "./img/lives/coin_v2.png"
CLAIM_BUTTON_TEMPLATE_PATH = "./img/lives/claim_buttom_v2.png"
WATCH_EARN_BANNER_TEMPLATE_PATH = "./img/lives/watch_earn_banner.png"

COIN_THRESHOLD = 0.95
CLAIM_BUTTON_THRESHOLD = 0.80
WATCH_EARN_BANNER_THRESHOLD = 0.80

LIVE_HOME_X = 560
LIVE_HOME_Y = 147

LIVE_NAV_X = 540
LIVE_NAV_Y = 2250

TIMER_REGION_X = 750
TIMER_REGION_Y = 200
TIMER_REGION_W = 285
TIMER_REGION_H = 430

CLAIM_VALIDATION_X = 207
CLAIM_VALIDATION_Y = 1854
CLAIM_VALIDATION_W = 680
CLAIM_VALIDATION_H = 100

MAX_TIMER_MINUTES = 15
BUTTON_LOAD_DELAY = 10
APP_OPEN_DELAY = 5


class Live:
    """Gerencia interação com lives da Shopee para coleta de moedas."""

    def __init__(self, adb: ADB) -> None:
        self._adb = adb

    def is_on_watch_earn_screen(self) -> bool:
        """Verifica se a tela atual é a tela 'Assista e Ganhe'."""
        self._adb.capture_screenshot()
        matches = find_template(SCREENSHOT_PATH, WATCH_EARN_BANNER_TEMPLATE_PATH, WATCH_EARN_BANNER_THRESHOLD)
        found = len(matches) > 0
        if found:
            logger.info("Tela 'Assista e Ganhe' detectada — pressionar voltar")
        return found

    def back_to_lives(self) -> None:
        """Volta para a listagem de lives pressionando o botão voltar."""
        logger.info("Voltando para a tela de lives")
        ADB.press_back()

    def recover_to_lives(self) -> None:
        """Reabre o app Shopee e navega até a seção de lives."""
        logger.info("Reabrindo app Shopee e navegando para lives...")
        ADB.open_app()
        logger.info("Aguardando %ds para o app carregar...", APP_OPEN_DELAY)
        time.sleep(APP_OPEN_DELAY)
        logger.info("Tocando em 'Live e Vídeo' na barra inferior (%d, %d)", LIVE_NAV_X, LIVE_NAV_Y)
        ADB.tap(LIVE_NAV_X, LIVE_NAV_Y)

    def click_live_home(self) -> None:
        """Toca no botão de lives na tela inicial."""
        logger.info("Voltando para tela inicial de lives")
        ADB.tap(LIVE_HOME_X, LIVE_HOME_Y)

    def next_live(self) -> None:
        """Rola para a próxima live."""
        logger.info("Passando para próxima live")
        self._adb.scroll_up()

    def wait_buttons_load(self) -> None:
        """Aguarda carregamento dos botões na live."""
        logger.info("Aguardando %ds para botões carregarem...", BUTTON_LOAD_DELAY)
        time.sleep(BUTTON_LOAD_DELAY)

    def has_coin(self) -> bool:
        """Verifica se há moeda disponível na live atual."""
        self._adb.capture_screenshot()
        logger.info("Buscando moeda (template: %s, threshold: %.2f)", COIN_TEMPLATE_PATH, COIN_THRESHOLD)
        matches = find_template(SCREENSHOT_PATH, COIN_TEMPLATE_PATH, COIN_THRESHOLD)
        found = len(matches) > 0
        logger.info("Moeda %s (%d match(es))", "ENCONTRADA" if found else "NÃO encontrada", len(matches))
        return found

    def wait_to_receive_coins(self) -> None:
        """Lê o timer de countdown via OCR e aguarda o tempo indicado."""
        logger.info("Lendo timer via OCR na região (%d,%d,%d,%d)", TIMER_REGION_X, TIMER_REGION_Y, TIMER_REGION_W, TIMER_REGION_H)
        text = extract_text_from_region(
            SCREENSHOT_PATH,
            TIMER_REGION_X,
            TIMER_REGION_Y,
            TIMER_REGION_W,
            TIMER_REGION_H,
        )
        logger.info("OCR timer resultado: '%s'", text)
        match = re.search(r"(\d{1,2}):(\d{2})", text)
        if not match:
            logger.info("Timer não encontrado no texto OCR, pulando espera")
            return

        minutes = int(match.group(1))
        seconds = int(match.group(2))
        logger.info("Timer detectado: %d:%02d", minutes, seconds)

        if minutes > MAX_TIMER_MINUTES:
            logger.info("Timer %d min excede máximo (%d min), resetando para 0", minutes, MAX_TIMER_MINUTES)
            minutes = 0

        total_seconds = minutes * 60 + seconds
        logger.info("Aguardando %d segundos para receber moedas...", total_seconds)
        time.sleep(total_seconds)

    def claim_coin(self) -> None:
        """Tenta coletar a moeda e valida o resultado."""
        self._adb.capture_screenshot()
        logger.info("Buscando botão de claim (template: %s, threshold: %.2f)", CLAIM_BUTTON_TEMPLATE_PATH, CLAIM_BUTTON_THRESHOLD)
        matches = find_template(SCREENSHOT_PATH, CLAIM_BUTTON_TEMPLATE_PATH, CLAIM_BUTTON_THRESHOLD)

        if matches:
            first = matches[0]
            logger.info("Botão de claim ENCONTRADO em (%d, %d) — clicando", first.x, first.y)
            ADB.tap(first.x, first.y)
        else:
            logger.info("Botão de claim NÃO encontrado")

        self._validate_claim()

    def _validate_claim(self) -> None:
        """Verifica se o resgate falhou e rola para próxima live se necessário."""
        logger.info("Validando claim via OCR na região (%d,%d,%d,%d)", CLAIM_VALIDATION_X, CLAIM_VALIDATION_Y, CLAIM_VALIDATION_W, CLAIM_VALIDATION_H)
        text = extract_text_from_region(
            SCREENSHOT_PATH,
            CLAIM_VALIDATION_X,
            CLAIM_VALIDATION_Y,
            CLAIM_VALIDATION_W,
            CLAIM_VALIDATION_H,
        )
        logger.info("OCR validação resultado: '%s'", text)
        if re.search(r"Resgate falhou", text):
            logger.info("Resgate FALHOU — passando para próxima live")
            self._adb.scroll_up()
        else:
            logger.info("Validação OK (sem 'Resgate falhou')")
