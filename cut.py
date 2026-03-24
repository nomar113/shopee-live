"""Utilitário interativo para recortar templates de screenshots."""

import sys

import cv2

SCREENSHOT_PATH = "./img/screenshot.png"
OUTPUT_PATH = "claim_button.png"
WINDOW_TITLE = "Selecione a região do template"


def crop_template() -> None:
    """Abre GUI para selecionar e recortar região de um screenshot."""
    screenshot = cv2.imread(SCREENSHOT_PATH, cv2.IMREAD_UNCHANGED)
    if screenshot is None:
        print(f"Erro ao carregar a imagem '{SCREENSHOT_PATH}'.")
        sys.exit(1)

    roi = cv2.selectROI(WINDOW_TITLE, screenshot, showCrosshair=True, fromCenter=False)
    cv2.destroyWindow(WINDOW_TITLE)

    x, y, w, h = roi
    cropped = screenshot[y : y + h, x : x + w]
    cv2.imwrite(OUTPUT_PATH, cropped)
    print(f"Template salvo como '{OUTPUT_PATH}'.")


if __name__ == "__main__":
    crop_template()
