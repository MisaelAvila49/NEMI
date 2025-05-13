import cv2
import numpy as np
import requests
from io import BytesIO

# Configuración de la API
API_URL = "http://127.0.0.1:8000/Arcos_Movilidad/"

def procesar_frame_con_api(frame):
    """Envía un frame a la API y devuelve el resultado procesado"""
    # Codificar el frame como JPEG
    _, img_encoded = cv2.imencode(".jpg", frame)
    bytes_imagen = BytesIO(img_encoded.tobytes())
    
    # Enviar a la API
    files = {"file": ("frame.jpg", bytes_imagen, "image/jpeg")}
    try:
        response = requests.post(API_URL, files=files)
        
        if response.status_code == 200:
            # Convertir la respuesta a imagen
            img_array = np.frombuffer(response.content, np.uint8)
            return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        else:
            print(f"Error en la API: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error al conectar con la API: {str(e)}")
        return None

# Iniciar captura de video
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error al abrir la cámara")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al capturar frame")
        break

    # Procesar cada frame con la API
    resultado = procesar_frame_con_api(frame)
    
    # Mostrar el frame procesado o el original si hay error
    if resultado is not None:
        cv2.imshow("Arcos de movilidad - API", resultado)
    else:
        cv2.imshow("Arcos de movilidad - API", frame)
    
    # Salir con ESC
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()