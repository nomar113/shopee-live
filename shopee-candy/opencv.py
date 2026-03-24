"""Bot automático do Shopee Candy com detecção de UI via template matching."""

import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests

from ADB import ADB
from vision import find_template

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SCREENSHOT_PATH = "screenshot.png"
SHOPEE_CANDY_TEMPLATE = "shopee_candy.png"
YES_BUTTON_TEMPLATE = "yes_button.png"
PURPLE_HAMMER_TEMPLATE = "purple_hammer.png"

DETECTION_THRESHOLD = 0.95
HAMMER_X = 540
HAMMER_Y = 2160

UI_LOAD_DELAY = 10
HAMMER_TAP_DELAY = 3

NTFY_URL = "https://ntfy.sh/nomar113"

CANDY_COORDS = [
    (168, 1800),
    (168, 1700),
    (282, 1700),
    (282, 1600),
    (512, 1600),
    (740, 1800),
]


def notify_error(message: str) -> None:
    """Envia notificação push via ntfy.sh."""
    try:
        requests.post(NTFY_URL, data=message, timeout=10)
    except requests.RequestException as e:
        logger.error("Falha ao enviar notificação: %s", e)


def detect_and_tap_ui(adb: ADB) -> None:
    """Detecta botões do Shopee Candy e entra no jogo."""
    adb.capture_screenshot(SCREENSHOT_PATH)

    for template in [SHOPEE_CANDY_TEMPLATE, YES_BUTTON_TEMPLATE]:
        matches = find_template(SCREENSHOT_PATH, template, DETECTION_THRESHOLD)
        if matches:
            ADB.tap(matches[0].x, matches[0].y)
            time.sleep(UI_LOAD_DELAY)


def play_candy_round(adb: ADB) -> bool:
    """Executa uma rodada do jogo. Retorna False se o jogo terminou."""
    coord_index = 0

    while True:
        adb.capture_screenshot(SCREENSHOT_PATH)
        hammer_matches = find_template(SCREENSHOT_PATH, PURPLE_HAMMER_TEMPLATE, DETECTION_THRESHOLD)

        if not hammer_matches:
            notify_error("erro no app")
            return False

        ADB.tap(HAMMER_X, HAMMER_Y)
        x, y = CANDY_COORDS[coord_index]
        ADB.tap(x, y)
        logger.info("Tap martelo + candy (%d, %d)", x, y)

        coord_index = (coord_index + 1) % len(CANDY_COORDS)
        time.sleep(HAMMER_TAP_DELAY)


def main() -> None:
    adb = ADB()

    while True:
        detect_and_tap_ui(adb)
        play_candy_round(adb)


if __name__ == "__main__":
    main()
