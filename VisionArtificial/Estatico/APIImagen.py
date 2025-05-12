# COMANDOS NECESARIOS PARA EJECUTAR, UBICARSE EN:
# cd NEMI
# Ejecutar el comando:
# uvicorn VisionArtificial.Estatico.APIImagen:app

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import numpy as np
import cv2
import mediapipe as mp
from io import BytesIO

app = FastAPI()

# Inicializar mediapipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Configuración de constantes
CL = (130, 140, 40)        # Color para líneas
CP = (205, 218, 56)        # Color para puntos
CCI, CRI, CTOI = (30, 180, 200), (30, 120, 200), (30, 60, 200)  # Colores izquierdos
CCD, CRD, CTOD = (200, 180, 30), (200, 120, 30), (200, 60, 30)  # Colores derechos
font = cv2.FONT_HERSHEY_PLAIN
T1 = 2                     # Grosor texto 1
T2 = T1 + 1                # Grosor texto 2

# Diccionario de índices de landmarks
INDICES = {
    'N': 0, 'H_I': 11, 'H_D': 12, 'C_I': 23, 'C_D': 24,
    'R_I': 25, 'R_D': 26, 'TO_I': 27, 'TO_D': 28,
    'TA_I': 29, 'TA_D': 30
}

# FUNCIÓN PARA CALCULAR ANGULOS
def angle(a, b, c):
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)
    ang = np.degrees(np.arccos(cosine_angle))
    if ang > 180:
        ang = ang - 180
    if ang < 90:
        ang = 180 - ang
    ang = abs(round(ang))
    return ang, b  # Devuelve una tupla (ángulo, punto)

def procesar_imagen(img):
    # Obtener dimensiones del frame
    H, W, _ = img.shape
    CXI, CXD = round(W/55), -round(W/17)

    with mp_pose.Pose(static_image_mode=True, 
                     model_complexity=2, 
                     min_detection_confidence=0.5) as pose:
        
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)
        image = img.copy()

        # Verificar si se detectó una persona
        if results.pose_landmarks is None:
            cv2.putText(image, "Persona fuera de cuadro", (W//4, H//2), 
                       font, 2, (0, 0, 255), 3)
        else:
            try:
                landmarks = results.pose_landmarks.landmark

                # Obtener puntos relevantes
                puntos = {}
                for k, i in INDICES.items():
                    puntos[k] = np.multiply([landmarks[i].x, landmarks[i].y], [W, H]).astype(int)

                # Dibujar pose
                mp_drawing.draw_landmarks(
                    image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(CL, T2, T2),
                    mp_drawing.DrawingSpec(CP, T2, T2)
                )

                # Procesar lado derecho
                if all(landmarks[i].visibility > 0.5 for i in [24, 26, 28]):
                    DCD_ang, DCD_pos = angle(puntos['H_D'], puntos['C_D'], puntos['R_D'])
                    DRD_ang, DRD_pos = angle(puntos['C_D'], puntos['R_D'], puntos['TO_D'])
                    DTOD_ang, DTOD_pos = angle(puntos['R_D'], puntos['TO_D'], puntos['TA_D'])
                    
                    DRD_ang = 180 - DRD_ang
                    DTOD_ang = 180 - (DTOD_ang - 45)

                    # Dibujar ángulos derecho
                    for ang, pos, color in zip([DCD_ang, DRD_ang, DTOD_ang],
                                            [DCD_pos, DRD_pos, DTOD_pos],
                                            [CCD, CRD, CTOD]):
                        cv2.circle(image, pos, T2*2, color, -1)
                        cv2.putText(image, str(ang), pos + [CXI, -1], font, T1, color, T2)

                # Procesar lado izquierdo
                if all(landmarks[i].visibility > 0.5 for i in [23, 25, 27]):
                    DCI_ang, DCI_pos = angle(puntos['H_I'], puntos['C_I'], puntos['R_I'])
                    DRI_ang, DRI_pos = angle(puntos['C_I'], puntos['R_I'], puntos['TO_I'])
                    DTOI_ang, DTOI_pos = angle(puntos['R_I'], puntos['TO_I'], puntos['TA_I'])
                    
                    DRI_ang = 180 - DRI_ang
                    DTOI_ang = 180 - (DTOI_ang - 45)

                    # Dibujar ángulos izquierdo
                    for ang, pos, color in zip([DCI_ang, DRI_ang, DTOI_ang],
                                            [DCI_pos, DRI_pos, DTOI_pos],
                                            [CCI, CRI, CTOI]):
                        cv2.circle(image, pos, T2*2, color, -1)
                        cv2.putText(image, str(ang), pos + [CXD, -1], font, T1, color, T2)

            except Exception as e:
                return None, f"Error {str(e)}"

    return image, None

@app.post("/Arcos_Movilidad/")
async def endpoint_procesar_imagen(file: UploadFile = File(...)):
    contents = await file.read()
    np_img = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    
    result_img, error = procesar_imagen(img)

    if error:
        return {"error": error}

    # Codificar imagen como JPEG
    _, img_encoded = cv2.imencode(".jpg", result_img)
    return StreamingResponse(BytesIO(img_encoded.tobytes()), media_type="image/jpeg")