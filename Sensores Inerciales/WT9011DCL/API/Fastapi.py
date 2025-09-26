import asyncio
import csv
import time
import threading
from fastapi import FastAPI
from pydantic import BaseModel
from bleak import BleakClient

app = FastAPI()

device_instance = None
capture_task = None

class DeviceModel:
    def __init__(self, device_name, ble_device, position):
        self.device_name = device_name
        self.ble_device = ble_device
        self.position = position
        self.client = None
        self.writer_characteristic = None
        self.is_open = False
        self.device_data = {}
        self.temp_bytes = []
        self.timestamps = []

        self.start_time = None
        self.step_count = 0
        self.angz_last = None
        self.angz_threshold = 20
        self.step_timestamps = []

    async def open_device(self):
        try:
            async with BleakClient(self.ble_device) as client:
                self.client = client
                self.is_open = True

                service_uuid = "0000ffe5-0000-1000-8000-00805f9a34fb"
                read_characteristic_uuid = "0000ffe4-0000-1000-8000-00805f9a34fb"
                write_characteristic_uuid = "0000ffe9-0000-1000-8000-00805f9a34fb"

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
                    raise Exception("Características BLE no encontradas")

                await self.calibrate_device()
                await client.start_notify(notify_characteristic.uuid, self.on_data_received)

                while self.is_open:
                    await asyncio.sleep(0.1)

                await client.stop_notify(notify_characteristic.uuid)

        except Exception as e:
            print(f"Error al abrir dispositivo: {e}")

    async def calibrate_device(self):
        if not self.writer_characteristic or not self.client:
            return

        await self.client.write_gatt_char(self.writer_characteristic, bytearray([0xFF, 0xAA, 0x01, 0x00]))
        await asyncio.sleep(1)
        await self.client.write_gatt_char(self.writer_characteristic, bytearray([0xFF, 0xAA, 0x02, 0x00]))
        await asyncio.sleep(1)
        await self.client.write_gatt_char(self.writer_characteristic, bytearray([0xFF, 0xAA, 0x03, 0x00]))
        await asyncio.sleep(1)

    def stop(self):
        self.is_open = False

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

            self.angz_last = ang_z

    def get_metrics(self):
        if not self.step_timestamps or self.start_time is None:
            return 0, 0.0, 0.0, 0.0
        
        total_time = self.step_timestamps[-1] - self.start_time
        cadencia = (self.step_count / total_time) * 60 if total_time > 0 else 0
        velocidad = 1.2 * cadencia / 120
        longitud_paso = (velocidad * 60) / cadencia if cadencia > 0 else 0

        return round(self.step_count), round(cadencia, 2), round(velocidad, 2), round(longitud_paso, 2)

    @staticmethod
    def get_signed_int16(value):
        return value - 0x10000 if value >= 0x8000 else value


class StartRequest(BaseModel):
    mac: str
    name: str
    position: str

@app.post("/start")
async def start_capture(req: StartRequest):
    global device_instance, capture_task

    if capture_task and not capture_task.done():
        return {"status": "error", "message": "Ya se está capturando"}

    device_instance = DeviceModel(req.name, req.mac, req.position)
    capture_task = asyncio.create_task(device_instance.open_device())
    return {"status": "ok", "message": "Captura iniciada"}

@app.post("/stop")
async def stop_capture():
    global device_instance, capture_task

    if device_instance:
        device_instance.stop()
        await asyncio.sleep(2)  # dar tiempo a cerrar el notify

        pasos, cadencia, velocidad, longitud_paso = device_instance.get_metrics()
        with open("parametros_marcha.csv", mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Pasos", "Cadencia (pasos/min)", "Velocidad (m/s)", "Longitud de paso (m)"])
            writer.writerow([pasos, cadencia, velocidad, longitud_paso])

        return {
            "status": "ok",
            "message": "Captura detenida",
            "metrics": {
                "pasos": pasos,
                "cadencia": cadencia,
                "velocidad": velocidad,
                "longitud_paso": longitud_paso
            }
        }

    return {"status": "error", "message": "No hay captura activa"}

@app.get("/metrics")
async def get_metrics():
    global device_instance

    if device_instance:
        pasos, cadencia, velocidad, longitud_paso = device_instance.get_metrics()
        return {
            "steps": pasos,
            "cadence": cadencia,
            "speed": velocidad,
            "stride_length": longitud_paso
        }

    return {"status": "error", "message": "No hay captura activa"}

