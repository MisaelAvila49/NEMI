import asyncio
import csv
import time
import threading
from bleak import BleakClient

class DeviceModel:
    def __init__(self, device_name, ble_device, callback_method, position):
        print("Inicializando modelo del dispositivo...")
        self.device_name = device_name
        self.ble_device = ble_device
        self.callback_method = callback_method
        self.position = position
        self.client = None
        self.writer_characteristic = None
        self.is_open = False
        self.device_data = {}
        self.temp_bytes = []
        self.timestamps = []

        # Variables para métricas de marcha
        self.start_time = None
        self.step_count = 0
        self.angz_last = None
        self.angz_threshold = 20
        self.step_timestamps = []

    async def open_device(self):
        print(f"\nAbriendo dispositivo {self.device_name} en posición {self.position}...")
        print("Presione ENTER para detener la captura...\n")
        
        try:
            async with BleakClient(self.ble_device) as client:
                self.client = client
                self.is_open = True

                # Configurar hilo para detectar entrada del usuario
                def check_input():
                    input()
                    self.is_open = False
                
                threading.Thread(target=check_input, daemon=True).start()

                service_uuid = "0000ffe5-0000-1000-8000-00805f9a34fb"
                read_characteristic_uuid = "0000ffe4-0000-1000-8000-00805f9a34fb"
                write_characteristic_uuid = "0000ffe9-0000-1000-8000-00805f9a34fb"

                print("Obteniendo servicios del dispositivo...")
                services = await client.get_services()
                notify_characteristic = None

                for service in services:
                    if service.uuid == service_uuid:
                        for char in service.characteristics:
                            if char.uuid == read_characteristic_uuid:
                                notify_characteristic = char
                            elif char.uuid == write_characteristic_uuid:
                                self.writer_characteristic = char
                        break

                if not notify_characteristic or not self.writer_characteristic:
                    print("Error: No se encontraron características necesarias.")
                    return

                await self.calibrate_device()
                print("Calibración completada. Comenzando captura...")

                await client.start_notify(notify_characteristic.uuid, self.on_data_received)

                while self.is_open:
                    await asyncio.sleep(0.1)

                await client.stop_notify(notify_characteristic.uuid)
                print("\nCaptura detenida por el usuario")

        except Exception as e:
            print(f"\nError al abrir el dispositivo {self.device_name}: {e}")
            raise

    async def calibrate_device(self):
        if not self.writer_characteristic or not self.client:
            print("Error: Característica de escritura no encontrada.")
            return

        try:
            print("Iniciando calibración...")
            await self.client.write_gatt_char(self.writer_characteristic, bytearray([0xFF, 0xAA, 0x01, 0x00]))
            await asyncio.sleep(1)
            await self.client.write_gatt_char(self.writer_characteristic, bytearray([0xFF, 0xAA, 0x02, 0x00]))
            await asyncio.sleep(1)
            await self.client.write_gatt_char(self.writer_characteristic, bytearray([0xFF, 0xAA, 0x03, 0x00]))
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Error durante la calibración: {e}")

    def close_device(self):
        self.is_open = False
        print(f"Dispositivo {self.device_name} cerrado.")

    def on_data_received(self, sender, data):
        current_time = time.time()
        delta_time = current_time - self.timestamps[-1] if self.timestamps else 0.0
        self.timestamps.append(current_time)

        self.temp_bytes.extend(data)
        if len(self.temp_bytes) >= 20:
            self.process_data(self.temp_bytes[:20], delta_time)
            self.temp_bytes = self.temp_bytes[20:]

    def process_data(self, bytes_data, delta_time):
        if bytes_data[1] == 0x61:
            ang_z = self.get_signed_int16(bytes_data[19] << 8 | bytes_data[18]) / 32768 * 180

            if self.start_time is None:
                self.start_time = time.time()

            if self.angz_last is not None and abs(ang_z - self.angz_last) > self.angz_threshold:
                self.step_count += 1
                self.step_timestamps.append(time.time())
                print(f"Paso detectado! Total: {self.step_count}")

            self.angz_last = ang_z

    def get_metrics(self):
        if not self.step_timestamps or self.start_time is None:
            return 0, 0.0, 0.0, 0.0
        
        total_time = self.step_timestamps[-1] - self.start_time
        cadencia = (self.step_count / total_time) * 60 if total_time > 0 else 0
        velocidad = 1.2 * cadencia / 120  # fórmula estimada
        longitud_paso = (velocidad * 60) / cadencia if cadencia > 0 else 0
        
        return (
            round(self.step_count), 
            round(cadencia, 2), 
            round(velocidad, 2), 
            round(longitud_paso, 2))
    
    @staticmethod
    def get_signed_int16(value):
        return value - 0x10000 if value >= 0x8000 else value

async def main():
    csv_filename = "parametros_marcha.csv"
    with open(csv_filename, mode="w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Pasos", "Cadencia (pasos/min)", "Velocidad (m/s)", "Longitud de paso (m)"])

        device = {"mac": "38:1e:c7:e4:f1:09", "nombre": "sensor 1", "position": "posición 1"}
        device_object = DeviceModel(device["nombre"], device["mac"], None, device["position"])

        try:
            await device_object.open_device()
        except Exception as e:
            import traceback
            traceback.print_exc()

        finally:
            pasos, cadencia, velocidad, longitud_paso = device_object.get_metrics()
            
            print("\n--- Métricas Finales de Marcha ---")
            print(f"Pasos totales: {pasos}")
            print(f"Cadencia: {cadencia} pasos/min")
            print(f"Velocidad: {velocidad} m/s")
            print(f"Longitud de paso promedio: {longitud_paso} m")

            csv_writer.writerow([pasos, cadencia, velocidad, longitud_paso])
            print(f"\nDatos guardados en {csv_filename}")

if __name__ == "__main__":
    asyncio.run(main())
