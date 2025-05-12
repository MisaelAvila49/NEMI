import requests
import os
import time
from pathlib import Path

# Configuración de la API
API_URL = "http://127.0.0.1:8000/analizar_video/"
DOWNLOAD_VIDEO_URL = "http://127.0.0.1:8000/descargar_video/"
DOWNLOAD_CSV_URL = "http://127.0.0.1:8000/descargar_csv/"
CLEANUP_URL = "http://127.0.0.1:8000/cleanup/"

# Obtener el directorio actual
current_dir = os.path.dirname(__file__)

# Nombre entrada y salidas
input_video_path = os.path.abspath(os.path.join(current_dir, '..', 'Pruebas', 'Gait.mp4'))
output_video_path = os.path.abspath(os.path.join(current_dir, '..', 'Pruebas', 'Analyzed_Gait.mp4'))
csv_path = os.path.abspath(os.path.join(current_dir, '..', 'Pruebas', 'Analysis.csv'))

def process_video():
    # 1. Subir el video a la API
    with open(input_video_path, 'rb') as f:
        files = {'file': (os.path.basename(input_video_path), f, 'video/mp4')}
        response = requests.post(API_URL, files=files)
    
    if response.status_code != 200:
        print(f"Error al subir el video: {response.text}")
        return None
    
    session_data = response.json()
    session_id = session_data['session_id']
    print(f"Video subido correctamente. ID de sesión: {session_id}")
    
    # 2. Esperar un tiempo razonable para el procesamiento
    # (En una aplicación real, podrías implementar un polling para verificar el estado)
    print("Procesando video...")
    time.sleep(5)  # Ajusta este tiempo según la duración de tu video
    
    # 3. Descargar el video procesado
    video_url = f"{DOWNLOAD_VIDEO_URL}{session_id}"
    video_response = requests.get(video_url)
    
    if video_response.status_code == 200:
        with open(output_video_path, 'wb') as f:
            f.write(video_response.content)
        print(f"Video procesado guardado en: {output_video_path}")
    else:
        print(f"Error al descargar el video procesado: {video_response.text}")
    
    # 4. Descargar el CSV de análisis
    csv_url = f"{DOWNLOAD_CSV_URL}{session_id}"
    csv_response = requests.get(csv_url)
    
    if csv_response.status_code == 200:
        with open(csv_path, 'wb') as f:
            f.write(csv_response.content)
        print(f"CSV de análisis guardado en: {csv_path}")
    else:
        print(f"Error al descargar el CSV: {csv_response.text}")
    
    # 5. Opcional: Limpiar la sesión en el servidor
    cleanup_url = f"{CLEANUP_URL}{session_id}"
    cleanup_response = requests.delete(cleanup_url)
    
    if cleanup_response.status_code == 200:
        print("Sesión limpiada en el servidor")
    else:
        print(f"Error al limpiar la sesión: {cleanup_response.text}")

if __name__ == "__main__":
    # Crear directorio de salida si no existe
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
    
    process_video()