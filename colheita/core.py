import logging
import time

import requests

from ADB import ADB
from vision import extract_text_from_region, find_template

logger = logging.getLogger(__name__)

SCREENSHOT_PATH = "./img/screenshot.png"

COLHEITA_ICON_TEMPLATE_PATH = "./img/colheita/colheita_icon.png"
REGADOR_TEMPLATE_PATH = "./img/colheita/regador.png"

COLHEITA_ICON_THRESHOLD = 0.80
REGADOR_THRESHOLD = 0.80

# Badge de gotas no regador (ex.: "67"), abaixo do ícone.
DROPLET_COUNT_REGION_X = 845
DROPLET_COUNT_REGION_Y = 2185
DROPLET_COUNT_REGION_W = 90
DROPLET_COUNT_REGION_H = 50
DROPLET_COUNT_OCR_CONFIG = "--psm 7 -c tessedit_char_whitelist=0123456789"

NTFY_URL = "https://ntfy.sh/nomar113"
NTFY_MESSAGE_REGADOR_USADO = "Shopee: regador utilizado"

EU_TAB_X = 970
EU_TAB_Y = 2250

MOEDAS_ICON_X = 538
MOEDAS_ICON_Y = 1009

# A fileira de ícones "Explore Mais" corta o ícone da Colheita na borda direita;
# é preciso arrastar para a esquerda antes de tentar localizá-lo.
ICON_ROW_SWIPE_START_X = 850
ICON_ROW_SWIPE_END_X = 200
ICON_ROW_SWIPE_Y = 1594
ICON_ROW_SWIPE_DURATION_MS = 400

MOEDAS_LOAD_DELAY = 2
GAME_LOAD_TIMEOUT = 15
GAME_LOAD_POLL_INTERVAL = 1


class Colheita:
    """Gerencia interação com o jogo Colheita (Plante e Ganhe)."""

    def __init__(self, adb: ADB) -> None:
        self._adb = adb

    def water_plant(self) -> bool:
        """Abre o jogo Colheita, clica no regador vermelho e fecha o app.

        O app é sempre fechado ao final (regando ou não); o loop principal
        detecta que a Shopee saiu do primeiro plano e a reabre nas lives.
        """
        logger.info("Iniciando fluxo do jogo Colheita")
        try:
            self._open_game()
            return self._click_regador()
        finally:
            ADB.close_app()

    def _open_game(self) -> None:
        """Navega Eu > Moedas > (scroll) > ícone Colheita."""
        logger.info("Tocando na aba 'Eu'")
        ADB.tap(EU_TAB_X, EU_TAB_Y)
        time.sleep(MOEDAS_LOAD_DELAY)

        logger.info("Tocando em 'Moedas'")
        ADB.tap(MOEDAS_ICON_X, MOEDAS_ICON_Y)
        time.sleep(MOEDAS_LOAD_DELAY)

        logger.info("Arrastando fileira de ícones para revelar 'Plante e ganhe'")
        ADB.swipe(ICON_ROW_SWIPE_START_X, ICON_ROW_SWIPE_Y, ICON_ROW_SWIPE_END_X, ICON_ROW_SWIPE_Y, ICON_ROW_SWIPE_DURATION_MS)
        time.sleep(1)

        self._tap_template(COLHEITA_ICON_TEMPLATE_PATH, COLHEITA_ICON_THRESHOLD, "ícone Colheita")
        self._wait_game_load()

    def _wait_game_load(self) -> None:
        """Aguarda a tela de loading terminar e o regador aparecer."""
        logger.info("Aguardando carregamento do jogo Colheita...")
        elapsed = 0
        while elapsed < GAME_LOAD_TIMEOUT:
            self._adb.capture_screenshot()
            matches = find_template(SCREENSHOT_PATH, REGADOR_TEMPLATE_PATH, REGADOR_THRESHOLD)
            if matches:
                logger.info("Jogo Colheita carregado")
                return
            time.sleep(GAME_LOAD_POLL_INTERVAL)
            elapsed += GAME_LOAD_POLL_INTERVAL
        logger.warning("Timeout aguardando carregamento do jogo Colheita")

    def _click_regador(self) -> bool:
        """Localiza e clica no regador vermelho, e confirma o consumo das gotas.

        Sem gotas disponíveis, o toque no regador leva para uma tela diferente
        (lista de amigos / roleta) em vez de regar — por isso checamos antes.
        """
        droplet_count_before = self._get_droplet_count()
        if droplet_count_before == 0:
            logger.info("Sem gotas disponíveis (0) — pulando clique no regador")
            return False

        self._adb.capture_screenshot()
        matches = find_template(SCREENSHOT_PATH, REGADOR_TEMPLATE_PATH, REGADOR_THRESHOLD)
        if not matches:
            logger.warning("Regador não encontrado — pulando rega")
            return False

        match = matches[0]
        x = match.x + match.width // 2
        y = match.y + match.height // 2
        logger.info("Clicando no regador vermelho em (%d, %d)", x, y)
        ADB.tap(x, y)
        time.sleep(2)

        droplet_count_after = self._get_droplet_count()
        if droplet_count_after == 0:
            logger.info("Gotas zeradas após o clique — regador utilizado com sucesso")
            self._notify_regador_utilizado()
        else:
            logger.warning("Gotas não zeraram após o clique (valor lido: %s) — não notificando", droplet_count_after)
        return True

    def _get_droplet_count(self) -> int:
        """Lê via OCR a quantidade de gotas exibida no badge do regador."""
        self._adb.capture_screenshot()
        text = extract_text_from_region(
            SCREENSHOT_PATH,
            DROPLET_COUNT_REGION_X,
            DROPLET_COUNT_REGION_Y,
            DROPLET_COUNT_REGION_W,
            DROPLET_COUNT_REGION_H,
            config=DROPLET_COUNT_OCR_CONFIG,
        )
        logger.info("OCR gotas do regador: '%s'", text)
        if not text.isdigit():
            return -1
        return int(text)

    @staticmethod
    def _notify_regador_utilizado() -> None:
        """Envia notificação push via ntfy.sh."""
        try:
            requests.post(NTFY_URL, data=NTFY_MESSAGE_REGADOR_USADO.encode("utf-8"), timeout=10)
            logger.info("Notificação ntfy enviada: '%s'", NTFY_MESSAGE_REGADOR_USADO)
        except requests.RequestException as error:
            logger.error("Falha ao enviar notificação ntfy: %s", error)

    def _tap_template(self, template_path: str, threshold: float, label: str) -> None:
        """Localiza um template na tela atual e toca no centro do match."""
        self._adb.capture_screenshot()
        matches = find_template(SCREENSHOT_PATH, template_path, threshold)
        if not matches:
            logger.warning("%s não encontrado", label)
            return

        match = matches[0]
        x = match.x + match.width // 2
        y = match.y + match.height // 2
        logger.info("Tocando em %s em (%d, %d)", label, x, y)
        ADB.tap(x, y)
