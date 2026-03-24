import logging
from dataclasses import dataclass

import cv2
import numpy as np
import pytesseract

logger = logging.getLogger(__name__)


@dataclass
class Match:
    """Resultado de um template matching."""

    x: int
    y: int
    width: int
    height: int


def find_template(
    screenshot_path: str,
    template_path: str,
    threshold: float = 0.9,
) -> list[Match]:
    """Encontra ocorrências de um template em uma screenshot.

    Args:
        screenshot_path: Caminho da imagem de screenshot.
        template_path: Caminho da imagem template.
        threshold: Limiar mínimo de correlação (0.0 a 1.0).

    Returns:
        Lista de Match com coordenadas e dimensões de cada ocorrência.

    Raises:
        FileNotFoundError: Se screenshot ou template não puderem ser carregados.
    """
    screenshot = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    if screenshot is None:
        raise FileNotFoundError(f"Não foi possível carregar a imagem: {screenshot_path}")
    if template is None:
        raise FileNotFoundError(f"Não foi possível carregar o template: {template_path}")

    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    h, w = gray_template.shape

    result = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)

    matches = [
        Match(x=int(col), y=int(row), width=w, height=h)
        for row, col in zip(locations[0], locations[1])
    ]

    logger.debug("Template %s: %d ocorrência(s) (threshold=%.2f)", template_path, len(matches), threshold)
    return matches


def extract_text_from_region(
    image_path: str,
    x: int,
    y: int,
    width: int,
    height: int,
) -> str:
    """Extrai texto de uma região da imagem usando OCR (Tesseract).

    Args:
        image_path: Caminho da imagem.
        x: Coordenada X do canto superior esquerdo.
        y: Coordenada Y do canto superior esquerdo.
        width: Largura da região.
        height: Altura da região.

    Returns:
        Texto extraído da região.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Não foi possível carregar a imagem: {image_path}")

    region = image[y : y + height, x : x + width]
    gray = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    text = pytesseract.image_to_string(thresholded).strip()
    logger.debug("OCR região (%d,%d,%d,%d): '%s'", x, y, width, height, text)
    return text
