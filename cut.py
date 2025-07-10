import cv2

# Carrega a imagem da screenshot
screenshot = cv2.imread("./img/screenshot.png", cv2.IMREAD_UNCHANGED)

if screenshot is None:
    print("Erro ao carregar a imagem 'screenshot.png'. Verifique o caminho e o nome do arquivo.")
    exit(1)

# Exibe a imagem e permite selecionar a região de interesse (ROI) interativamente
roi = cv2.selectROI("Selecione o shopee_candy", screenshot, showCrosshair=True, fromCenter=False)
cv2.destroyWindow("Selecione o shopee_candy")

# A ROI retornada é uma tupla (x, y, w, h)
x, y, w, h = roi

# Recorta a imagem usando slicing do NumPy
candy_cropped = screenshot[y:y+h, x:x+w]

# Salva a imagem recortada para uso posterior (por exemplo, no matchTemplate)
cv2.imwrite("claim_button.png", candy_cropped)

print("Imagem recortada salva como 'claim_button.png'.")
