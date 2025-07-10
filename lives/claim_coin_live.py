import cv2
import numpy as np
import subprocess
import time

def find_items(screenshot_path, template_path, threshold=0.9):
    """
    Encontra todas as posições do doce rosa na imagem de screenshot,
    retornando uma lista de (x, y, w, h).
    """
    # Carrega a imagem do jogo (screenshot) e o template (doce rosa)
    screenshot = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    if screenshot is None:
        raise FileNotFoundError(f"Não foi possível carregar a imagem: {screenshot_path}")
    if template is None:
        raise FileNotFoundError(f"Não foi possível carregar o template: {template_path}")

    # Converte para tons de cinza
    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Obtém as dimensões do template
    h, w = gray_template.shape

    # Aplica o matchTemplate
    res = cv2.matchTemplate(gray_screenshot, gray_template, cv2.TM_CCOEFF_NORMED)

    # Localiza onde o valor de correlação é maior ou igual ao threshold
    loc = np.where(res >= threshold)
    for i, j in zip(loc[0], loc[1]):
        print(f"res[{i}, {j}] = {res[i, j]}")

    # Monta a lista de bounding boxes (x, y, w, h)
    boxes = []
    for pt in zip(*loc[::-1]):  # loc vem no formato (row, col), invertendo para (col, row)
        x, y = pt[0], pt[1]
        boxes.append((x, y, w, h))

    return boxes

def tap(x, y):
    """
    Simulates a tap on the Android device screen at the position (x, y) using ADB.
    
    Parameters:
        x (int): The x-coordinate of the tap.
        y (int): The y-coordinate of the tap.
    """
    # Build the adb command
    command = ["adb", "shell", "input", "tap", str(x), str(y)]
    
    try:
        # Execute the command and wait for completion
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Command executed successfully!")
        if result.stdout:
            print("Output:", result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except subprocess.CalledProcessError as error:
        print("Error executing the command:", error)
        print("Output:", error.stdout)
        print("Errors:", error.stderr)

def capture_screenshot(output_file="screenshot.png"):
    with open(output_file, "wb") as f:
        process = subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=f, stderr=subprocess.PIPE)

    if process.returncode == 0:
        print(f"Screenshot salvo como {output_file}")
    else:
        print(f"Erro ao capturar screenshot: {process.stderr.decode()}")

def refresh():
    command = ["adb", "shell", "input", "swipe", "500", "300", "500", "1000", "300"]
    try:
        # Execute the command and wait for completion
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Command executed successfully!")
        if result.stdout:
            print("Output:", result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except subprocess.CalledProcessError as error:
        print("Error executing the command:", error)
        print("Output:", error.stdout)
        print("Errors:", error.stderr)

def close_live():
    tap(1010, 110)

def find_more_live():
    command = ["adb", "shell", "input", "swipe", "500", "1600", "500", "300", "300"]
    try:
        # Execute the command and wait for completion
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("Command executed successfully!")
        if result.stdout:
            print("Output:", result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
    except subprocess.CalledProcessError as error:
        print("Error executing the command:", error)
        print("Output:", error.stdout)
        print("Errors:", error.stderr)

flag = True

class Ponto:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Criar uma lista de objetos
# normal level: [Ponto(80, 1500), Ponto(200, 1400), Ponto(320, 1300), Ponto(440, 1200),Ponto(560, 1100), Ponto(680, 1000), Ponto(800, 800), Ponto(900, 700), Ponto(1000, 600)]
# boss level: [Ponto(55, 1837), Ponto(55, 1039), Ponto(55, 1268), Ponto(168, 1700), Ponto(282, 1600), Ponto(396, 926), Ponto(512, 1609),Ponto(624, 1100), Ponto(740, 1495), Ponto(854, 1268), Ponto(967, 1039)]
coordenadas = [Ponto(55, 1837), Ponto(55, 1039), Ponto(55, 1268), Ponto(168, 1700), Ponto(282, 1600), Ponto(396, 926), Ponto(512, 1609),Ponto(624, 1100), Ponto(740, 1495), Ponto(854, 1268), Ponto(967, 1039)]

cont_coordenadas = 1


while(flag):
    capture_screenshot()
    detections = []
    # Ajuste o caminho da sua screenshot e do template do doce rosa
    screenshot_path = "screenshot.png"
    max_coins_path = "max_coins.png"
    live_coins_path = "live_coins.png"
    watch_and_gain_path = "watch_and_gain.png"
    claim_path = "claim.png"
    explorer_path = "explorer.png"

    # Encontra todas as correspondências
    max_coins_detection = find_items(screenshot_path, max_coins_path, threshold=0.95)
    has_coin_detection = find_items(screenshot_path, live_coins_path, threshold=0.95)
    watch_and_gain_detection = find_items(screenshot_path, watch_and_gain_path, threshold=0.95)
    claim_detection = find_items(screenshot_path, claim_path, threshold=0.95)

    if (len(max_coins_detection) > 0):
        detections = max_coins_detection
    if (len(claim_detection) > 0):
        detections = claim_detection
    # Exibe as coordenadas de cada detecção
    for (x, y, w, h) in detections:
        print(f"Encontrado em x={x}, y={y}, largura={w}, altura={h}")

    print(f"Total de encontrados: {len(detections)}")

    screenshot = cv2.imread(screenshot_path)
    # Verifica se a imagem foi carregada corretamente
    if screenshot is None:
        print("Erro ao carregar a imagem. Verifique o caminho e o nome do arquivo.")
    else:
        print("Imagem carregada com sucesso!")

    if(not has_coin_detection and watch_and_gain_detection):
        close_live()
        time.sleep(3)
        capture_screenshot()
        time.sleep(5)
        print("wait 5 seconds")
        explorer_detection = find_items(screenshot_path, explorer_path, threshold=0.95)
        print('explorer detection: ', len(explorer_detection))
        if (len(explorer_detection) > 0):
            print("click em explorar")
            for (x, y, w, h) in explorer_detection:
                try:
                    cv2.rectangle(screenshot, (x, y), (x + w, y + h), (0, 0, 255), 2)    
                    cv2.imwrite("resultado.png", screenshot)
                    tap(x, y)
                except:
                    flag = False
        time.sleep(10)

    print("detections:", len(detections))
    if (len(detections) > 0):
        for (x, y, w, h) in detections:
            try:
                cv2.rectangle(screenshot, (x, y), (x + w, y + h), (0, 0, 255), 2)    
                cv2.imwrite("resultado.png", screenshot)
                tap(x, y)
            except:
                flag = False
    elif(has_coin_detection):
        time.sleep(2*60)
    else:
        find_more_live()
    time.sleep(10)
