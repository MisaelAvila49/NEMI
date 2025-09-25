from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import cv2
import os
import mediapipe as mp
import numpy as np
import csv
from joblib import load
import tempfile
import uuid
from typing import Dict
import shutil
from pathlib import Path

app = FastAPI()

# Diccionario para almacenar las sesiones de procesamiento
processing_sessions: Dict[str, dict] = {}

# CARGAR ARCHIVOS
current_dir = os.path.dirname(__file__)

# Modelo y scaler
model_path = os.path.abspath(os.path.join(current_dir, 'ModelosML', 'PrediccionEtapas.joblib'))
model = load(model_path)
scaler_path = os.path.abspath(os.path.join(current_dir, 'ModelosML', 'Scaler.joblib'))
scaler = load(scaler_path)
scaler.feature_names_in_ = None

# INICIALIZAR MEDIAPIPE
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Colores y parametros
CL = (130,140,40)
CP = (205,218,56)
CCI, CRI, CTOI = (30,180,200), (30,120,200), (30,60,200)
CCD, CRD, CTOD = (200,180,30), (200,120,30), (200,60,30)
font = cv2.FONT_HERSHEY_PLAIN
text_color = (0, 0, 0)
T1 = 2
T2 = T1 + 1

# Diccionario de índices
indices = {
    'N': 0, 'H_I': 11, 'H_D': 12, 'C_I': 23, 'C_D': 24,
    'R_I': 25, 'R_D': 26, 'TO_I': 27, 'TO_D': 28,
    'TA_I': 29, 'TA_D': 30
}

# Diccionario para cambiar etiquetas
mapa_etiquetas = {
    "CONTACTO INICIAL": "INITIAL CONTACT",
    "RESPUESTA A LA CARGA": "LOADING RESPONSE",
    "APOYO MEDIO": "MID-STANCE",
    "APOYO FINAL": "TERMINAL STANCE",
    "PRE OSCILACION": "PRE-SWING",
    "OSCILACION INICIAL": "INITIAL SWING",
    "OSCILACION MEDIA": "MID-SWING",
    "OSCILACION FINAL": "TERMINAL SWING",
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
    return ang, b

@app.post("/procesar_grabacion/")
async def process_recording(request_data: dict):
    # Extraer parámetros del JSON recibido
    frames_dir = request_data.get("frames_dir", "")
    fps = request_data.get("fps", 24)
    
    if not frames_dir:
        raise HTTPException(status_code=400, detail="Se requiere el parámetro 'frames_dir'")

    # Crear un ID único para esta sesión
    session_id = str(uuid.uuid4())
    
    # Crear directorio temporal para esta sesión
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, f"processed_{session_id}.mp4")
    csv_path = os.path.join(temp_dir, f"analysis_{session_id}.csv")
    
    # Usar la ruta completa recibida directamente
    frames_folder = Path(frames_dir)
    if not frames_folder.exists():
        raise HTTPException(
            status_code=400,
            detail=f"No se encontró la carpeta especificada: {frames_dir}"
        )
    
    # Obtener lista de frames ordenados
    frame_files = sorted(frames_folder.glob("Frame_*.png"))
    if not frame_files:
        raise HTTPException(
            status_code=400,
            detail=f"No se encontraron frames (Frame_*.png) en: {frames_dir}"
        )
    
    # Obtener dimensiones del primer frame
    first_frame = cv2.imread(str(frame_files[0]))
    if first_frame is None:
        raise HTTPException(status_code=400, detail="Error al leer los frames")
    
    H, W = first_frame.shape[:2]
    
    # Configurar el video de salida
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (W, H))
    
    # Procesamiento de los frames
    with mp_pose.Pose(static_image_mode=False, model_complexity=2, min_detection_confidence=0.5) as pose:
        with open(csv_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time [s]','Phase', 'Hip Joint Angle (R)','Knee Joint Angle (R)','Ankle Joint Angle (R)',
                           'Hip Joint Angle (L)','Knee Joint Angle (L)','Ankle Joint Angle (L)'])
            
            for i, frame_file in enumerate(frame_files):
                image = cv2.imread(str(frame_file))
                if image is None:
                    continue
                
                ts = i / fps  # Tiempo en segundos
                
                CXI, CXD = round(W/55), -round(W/17)
                top_left = (5,5)
                BCX, BCY = round(W/4.8), round(W/24)
                TX, TY = round(W/120), round(W/38)
                bottom_right = (600, BCY)

                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = pose.process(image_rgb)
                image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

                if results.pose_landmarks is None:
                    cv2.putText(image, "Persona fuera de cuadro", (W//4, H//2), 
                               font, 2, (0, 0, 255), 3)
                    writer.writerow([ts, "NO PERSON", 0, 0, 0, 0, 0, 0])
                else:
                    try:
                        landmarks = results.pose_landmarks.landmark
                        
                        puntos = {}
                        for k, i in indices.items():
                            puntos[k] = np.multiply([landmarks[i].x, landmarks[i].y], [W, H]).astype(int)

                        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                                mp_drawing.DrawingSpec(CL, T2, T2),
                                                mp_drawing.DrawingSpec(CP, T2, T2))

                        DCD_ang, DRD_ang, DTOD_ang = 0, 0, 0
                        DCI_ang, DRI_ang, DTOI_ang = 0, 0, 0

                        if all(landmarks[i].visibility > 0.5 for i in [24, 26, 28]):
                            DCD_ang, DCD_pos = angle(puntos['H_D'], puntos['C_D'], puntos['R_D'])
                            DRD_ang, DRD_pos = angle(puntos['C_D'], puntos['R_D'], puntos['TO_D'])
                            DTOD_ang, DTOD_pos = angle(puntos['R_D'], puntos['TO_D'], puntos['TA_D'])
                            DRD_ang = 180 - DRD_ang
                            DTOD_ang = 180 - (DTOD_ang - 45)

                            for ang, pos, color in zip([DCD_ang, DRD_ang, DTOD_ang], 
                                                      [DCD_pos, DRD_pos, DTOD_pos], 
                                                      [CCD, CRD, CTOD]):
                                cv2.circle(image, pos, T2*2, color, -1)
                                cv2.putText(image, str(ang), np.array(pos) + [CXI, -1], font, T1, color, T2)

                        if all(landmarks[i].visibility > 0.5 for i in [23, 25, 27]):
                            DCI_ang, DCI_pos = angle(puntos['H_I'], puntos['C_I'], puntos['R_I'])
                            DRI_ang, DRI_pos = angle(puntos['C_I'], puntos['R_I'], puntos['TO_I'])
                            DTOI_ang, DTOI_pos = angle(puntos['R_I'], puntos['TO_I'], puntos['TA_I'])
                            DRI_ang = 180 - DRI_ang
                            DTOI_ang = 180 - (DTOI_ang - 45)

                            for ang, pos, color in zip([DCI_ang, DRI_ang, DTOI_ang], 
                                                      [DCI_pos, DRI_pos, DTOI_pos], 
                                                      [CCI, CRI, CTOI]):
                                cv2.circle(image, pos, T2*2, color, -1)
                                cv2.putText(image, str(ang), np.array(pos) + [CXD, -1], font, T1, color, T2)

                            if puntos['N'][0] > puntos['C_I'][0]:  
                                dif_ac = DCI_ang - DCD_ang
                                dif_ar = DRI_ang - DRD_ang
                                dif_at = DTOI_ang - DTOD_ang
                                dif_pcy = landmarks[23].y - landmarks[24].y
                                dif_pry = landmarks[25].y - landmarks[26].y
                                dif_pty = landmarks[27].y - landmarks[28].y
                            else:  
                                dif_ac = DCD_ang - DCI_ang
                                dif_ar = DRD_ang - DRI_ang
                                dif_at = DTOD_ang - DTOI_ang
                                dif_pcy = landmarks[24].y - landmarks[23].y
                                dif_pry = landmarks[26].y - landmarks[25].y
                                dif_pty = landmarks[28].y - landmarks[27].y

                            dif_pcx = landmarks[23].x - landmarks[24].x
                            dif_prx = landmarks[25].x - landmarks[26].x
                            dif_ptx = landmarks[27].x - landmarks[28].x

                            X = [[dif_ac, dif_ar, dif_at, dif_pcx, dif_pcy, dif_prx, dif_pry, dif_ptx, dif_pty]]
                            X = scaler.transform(X)
                            y_pred = model.predict(X)
                            text = [mapa_etiquetas.get(label, label) for label in y_pred][0]

                            (text_width, text_height), baseline = cv2.getTextSize(text, font, T1, T2)
                            center_x = (top_left[0] + bottom_right[0]) // 2
                            center_y = (top_left[1] + bottom_right[1]) // 2
                            text_x = center_x - text_width // 2
                            text_y = center_y + text_height // 2

                            cv2.rectangle(image, top_left, bottom_right, (255,255,255), -1)
                            cv2.rectangle(image, top_left, bottom_right, (0,0,0), T2)
                            cv2.putText(image, text, (text_x, text_y), font, T1, text_color, T2)

                            writer.writerow([ts, text, DCD_ang, DRD_ang, DTOD_ang, 
                                           DCI_ang, DRI_ang, DTOI_ang])

                    except Exception as e:
                        print(f"Error procesando frame {frame_file}: {e}")

                out.write(image)

    # Liberar recursos
    out.release()
    cv2.destroyAllWindows()
    
    # Almacenar información de la sesión
    processing_sessions[session_id] = {
        "temp_dir": temp_dir,
        "processed_video": output_path,
        "csv_file": csv_path
    }
    
    return {
        "session_id": session_id,
        "message": "Grabación procesada exitosamente",
        "frames_processed": len(frame_files),
        "duration_seconds": len(frame_files) / fps
    }

# Los endpoints para descargar y limpiar permanecen igual que en tu versión original
@app.get("/descargar_video/{session_id}")
async def download_video(session_id: str):
    if session_id not in processing_sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    video_path = processing_sessions[session_id]["processed_video"]
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"processed_video_{session_id}.mp4"
    )

@app.get("/descargar_csv/{session_id}")
async def download_csv(session_id: str):
    if session_id not in processing_sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    csv_path = processing_sessions[session_id]["csv_file"]
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="CSV no encontrado")
    
    return FileResponse(
        csv_path,
        media_type="text/csv",
        filename=f"analysis_{session_id}.csv"
    )

@app.delete("/cleanup/{session_id}")
async def cleanup_session(session_id: str):
    if session_id not in processing_sessions:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    try:
        temp_dir = processing_sessions[session_id]["temp_dir"]
        # Eliminar archivos temporales
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Error al eliminar {file_path}. Razón: {e}')
        
        # Eliminar el directorio temporal
        os.rmdir(temp_dir)
        
        # Eliminar la sesión del diccionario
        del processing_sessions[session_id]
        
        return {"message": "Sesión limpiada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar la sesión: {str(e)}")