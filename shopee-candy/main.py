"""Script standalone de tap sequencial para o Shopee Candy (nível normal)."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ADB import ADB

HAMMER_X = 540
HAMMER_Y = 2160
TAP_DELAY = 2.5

NORMAL_LEVEL_COORDS = [
    (80, 1500),
    (200, 1400),
    (320, 1300),
    (440, 1200),
    (560, 1100),
    (680, 1000),
    (800, 800),
    (900, 700),
    (1000, 600),
]


def run_tap_sequence(coords: list[tuple[int, int]]) -> None:
    """Executa sequência de taps no martelo + coordenada de cada nível."""
    for x, y in coords:
        ADB.tap(HAMMER_X, HAMMER_Y)
        ADB.tap(x, y)
        time.sleep(TAP_DELAY)


if __name__ == "__main__":
    run_tap_sequence(NORMAL_LEVEL_COORDS)
