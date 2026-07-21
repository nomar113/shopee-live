import logging
import os
import subprocess

logger = logging.getLogger(__name__)

SCREENSHOT_DIR = "./img"
SCREENSHOT_PATH = os.path.join(SCREENSHOT_DIR, "screenshot.png")

SWIPE_START_X = 500
SWIPE_START_Y = 1600
SWIPE_END_X = 500
SWIPE_END_Y = 300
SWIPE_DURATION_MS = 300


class ADB:
    def capture_screenshot(self, output_path: str = SCREENSHOT_PATH) -> bool:
        """Captura screenshot do dispositivo Android via ADB."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        device_path = "/sdcard/screenshot.png"
        capture = subprocess.run(
            ["adb", "shell", "screencap", "-p", device_path],
            capture_output=True,
        )
        if capture.returncode != 0:
            logger.error("Erro ao capturar screenshot: %s", capture.stderr.decode())
            return False
        pull = subprocess.run(
            ["adb", "pull", device_path, output_path],
            capture_output=True,
        )
        if pull.returncode != 0:
            logger.error("Erro ao copiar screenshot: %s", pull.stderr.decode())
            return False
        logger.info("Screenshot capturado: %s", output_path)
        return True

    def scroll_up(self) -> None:
        """Executa swipe de baixo para cima no dispositivo."""
        logger.info("Scroll up (swipe %d,%d → %d,%d)", SWIPE_START_X, SWIPE_START_Y, SWIPE_END_X, SWIPE_END_Y)
        self._run_shell_command(
            "input",
            "swipe",
            str(SWIPE_START_X),
            str(SWIPE_START_Y),
            str(SWIPE_END_X),
            str(SWIPE_END_Y),
            str(SWIPE_DURATION_MS),
        )

    @staticmethod
    def press_back() -> None:
        """Pressiona o botão voltar do Android."""
        command = ["adb", "shell", "input", "keyevent", "4"]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info("Botão voltar pressionado")
        except subprocess.CalledProcessError as error:
            logger.error("Erro ao pressionar voltar: %s", error)

    @staticmethod
    def tap(x: int, y: int) -> None:
        """Executa tap nas coordenadas (x, y) do dispositivo."""
        command = ["adb", "shell", "input", "tap", str(x), str(y)]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
            logger.info("Tap em (%d, %d)", x, y)
        except subprocess.CalledProcessError as error:
            logger.error("Erro ao executar tap(%d, %d): %s", x, y, error)

    @staticmethod
    def _run_shell_command(*args: str) -> None:
        """Executa comando adb shell genérico."""
        command = ["adb", "shell", *args]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as error:
            logger.error("Erro ao executar comando ADB: %s", error)
