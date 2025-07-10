import cv2
import numpy as np
import pytesseract
import re
import time

from ADB import ADB

class Live:
    def __init__(self):
        pass

    def clickLiveHome(self):
        ADB.tap(560, 147)

    def nextLive(self):
        adb = ADB(False)
        adb.scrool()
    
    def loadButtoms(self):
        time.sleep(7)

    def hasCoin(self):
        adb = ADB(False)
        adb.capture_screenshot()
        screenshot_path = "./img/screenshot.png"
        coin_path = "./img/lives/coin_v2.png"
        show_logs = True
        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
        coin = cv2.imread(coin_path, cv2.IMREAD_COLOR)
        if screenshot is None:
            if show_logs:
                raise FileNotFoundError(f"Não foi possível carregar a imagem: {screenshot_path}")
        if coin is None:
            if show_logs:
                raise FileNotFoundError(f"Não foi possível carregar o coin: {coin_path}")
        gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        gray_coin = cv2.cvtColor(coin, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray_screenshot, gray_coin, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.95)
        return len(loc[0]) > 0
    
    def waitToReceiveCoins(self):
        text = self.extractText(750, 305, 285, 110)
        match = re.search(r'(\d{1,2}):(\d{2})', text)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            if minutes > 15:
                minutes = 0
            total_seconds = minutes * 60 + seconds
            print(f"Esperando {total_seconds} segundos...")
            time.sleep(total_seconds)
    
    def claimCoin(self):
        text = self.extractText(750, 305, 285, 110)
        match = re.search(r'Resg', text)
        if match:
            ADB.tap(960, 380)

    def extractText(self, x, y, w, h):
        screenshot_path = "./img/screenshot.png"
        img = cv2.imread(screenshot_path)
        roi = img[y:y+h, x:x+w]
        cv2.imwrite('recorte_tempo.png', roi)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        cv2.imwrite('recorte_tempo_thresh.png', thresh)
        text = pytesseract.image_to_string(thresh) 
        print("Texto extraído:", text.strip())
        return text
    
    def validateClaimCoin(self):
        text = self.extractText(207, 1854, 680, 100)
        match = re.search(r'Resgate falhou', text)
        if match:
            adb = ADB(False)
            adb.scrool()
        
