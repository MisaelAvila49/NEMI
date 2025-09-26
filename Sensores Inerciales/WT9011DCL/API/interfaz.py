import customtkinter as ctk
import requests
import threading
from PIL import Image, ImageTk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# Colores personalizados
COLOR_MORADO = "#6a0dad"
COLOR_NARANJA = "#ff7f50"
COLOR_VERDE_MENTA = "#98ff98"

# API URL
API_URL = "http://localhost:8000"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Captura de Marcha Humana")
        self.geometry("600x450")
        self.configure(bg=COLOR_VERDE_MENTA)

        self.frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Logo
        self.logo_img = ImageTk.PhotoImage(Image.open("logo.png").resize((150, 75)))
        self.logo_label = ctk.CTkLabel(self.frame, image=self.logo_img, text="", anchor="w")
        self.logo_label.place(x=10, y=10)

        # Título
        self.label_title = ctk.CTkLabel(self.frame, text="Captura de datos", font=("Times new roman", 30, "bold"), text_color=COLOR_MORADO)
        self.label_title.pack(pady=(10, 20))

        # Botones
        self.start_button = ctk.CTkButton(self.frame, text="Iniciar Captura", fg_color=COLOR_MORADO, command=self.iniciar_captura)
        self.start_button.pack(pady=5)

        self.stop_button = ctk.CTkButton(self.frame, text="Detener y Ver Métricas", fg_color=COLOR_NARANJA, command=self.detener_captura)
        self.stop_button.pack(pady=5)

        # Estado
        self.status_label = ctk.CTkLabel(self.frame, text="", font=("Arial", 14), text_color=COLOR_MORADO)
        self.status_label.pack(pady=(10, 10))

        # Tabla de métricas
        self.metric_frame = ctk.CTkFrame(self.frame, fg_color=COLOR_VERDE_MENTA)
        self.metric_frame.pack(pady=10)

        self.metric_labels = {
            "pasos": self._crear_fila("Pasos"),
            "cadencia": self._crear_fila("Cadencia (pasos/min)"),
            "velocidad": self._crear_fila("Velocidad (m/s)"),
            "longitud_paso": self._crear_fila("Longitud de paso (m)")
        }

    def _crear_fila(self, etiqueta):
        fila = ctk.CTkFrame(self.metric_frame, fg_color="white")
        fila.pack(fill="x", pady=3, padx=5)

        label = ctk.CTkLabel(fila, text=etiqueta, font=("Arial", 13), width=180, anchor="w", text_color=COLOR_MORADO)
        label.pack(side="left", padx=5)

        valor = ctk.CTkLabel(fila, text="-", font=("Arial", 13, "bold"), text_color="black")
        valor.pack(side="left", padx=5)

        return valor

    def iniciar_captura(self):
        self.status_label.configure(text="Iniciando captura...")
        threading.Thread(target=self._iniciar_backend, daemon=True).start()

    def _iniciar_backend(self):
        try:
            res = requests.post(f"{API_URL}/start", json={
                "mac": "d2:3a:3d:8a:20:19",
                "name": "sensor 1",
                "position": "cadera"
            })
            if res.status_code == 200 and res.json()["status"] == "ok":
                self.status_label.configure(text="Captura en progreso...")
            else:
                self.status_label.configure(text="Error al iniciar")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")

    def detener_captura(self):
        self.status_label.configure(text="Deteniendo...")
        threading.Thread(target=self._detener_backend, daemon=True).start()

    def _detener_backend(self):
        try:
            res = requests.post(f"{API_URL}/stop")
            if res.status_code == 200:
                data = res.json()["metrics"]
                self.status_label.configure(text="Captura detenida")
                self.metric_labels["pasos"].configure(text=str(data["pasos"]))
                self.metric_labels["cadencia"].configure(text=f"{data['cadencia']} pasos/min")
                self.metric_labels["velocidad"].configure(text=f"{data['velocidad']} m/s")
                self.metric_labels["longitud_paso"].configure(text=f"{data['longitud_paso']} m")
            else:
                self.status_label.configure(text="Error al detener")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
