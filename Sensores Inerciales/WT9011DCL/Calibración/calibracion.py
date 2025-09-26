import asyncio
import csv
import time
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
        self.data_list = []

        # Comandos de calibración
        self.CALIB_ACCEL = bytearray([0xFF, 0xAA, 0x01, 0x01, 0x00])
        self.CALIB_MAGNET = bytearray([0xFF, 0xAA, 0x01, 0x07, 0x00])
        self.EXIT_CALIB = bytearray([0xFF, 0xAA, 0x01, 0x00, 0x00])

    async def open_device(self):
        print(f"Abriendo dispositivo {self.device_name} en posición {self.position}...")
        try:
            async with BleakClient(self.ble_device) as client:
                self.client = client
                self.is_open = True

                service_uuid = "0000ffe5-0000-1000-8000-00805f9a34fb"
                read_characteristic_uuid = "0000ffe4-0000-1000-8000-00805f9a34fb"
                write_characteristic_uuid = "0000ffe9-0000-1000-8000-00805f9a34fb"

                print("Obteniendo servicios del dispositivo...")
                services = await client.get_services()
                notify_characteristic = None

                for service in services:
                    if service.uuid == service_uuid:
                        print(f"Servicio encontrado: {service}")
                        for char in service.characteristics:
                            if char.uuid == read_characteristic_uuid:
                                notify_characteristic = char
                            elif char.uuid == write_characteristic_uuid:
                                self.writer_characteristic = char
                        break

                if not notify_characteristic or not self.writer_characteristic:
                    print("No se encontraron características necesarias.")
                    return

                print(f"Notificando característica: {notify_characteristic.uuid}")
                await client.start_notify(notify_characteristic.uuid, self.on_data_received)

                # Calibrar magnetómetro
                print("Iniciando calibración del magnetómetro...")
                await self.send_command(self.CALIB_MAGNET)
                print("Gira el sensor 360° en todos los ejes (x3 veces)")
                await asyncio.sleep(10)  # Espera durante la calibración
                await self.send_command(self.EXIT_CALIB)
                print("Calibración completada.")

                # Registrar datos después de la calibración (10 segundos)
                print("Recopilando datos calibrados...")
                await asyncio.sleep(10)

                while self.is_open:
                    await asyncio.sleep(1)

                await client.stop_notify(notify_characteristic.uuid)

        except Exception as e:
            print(f"Error al abrir el dispositivo {self.device_name}: {e}")

    async def send_command(self, command):
        """Envía un comando al sensor WT901BLE"""
        await self.client.write_gatt_char(self.writer_characteristic.uuid, command)
        await asyncio.sleep(0.1)  # Pequeña pausa para permitir ejecución

    def close_device(self):
        self.is_open = False
        print(f"Dispositivo {self.device_name} cerrado.")

    def on_data_received(self, sender, data):
        current_time = time.time()
        delta_time = current_time - self.timestamps[-1] if self.timestamps else 0.0
        self.timestamps.append(current_time)
        print(f"Datos recibidos de {sender} ({self.position}) con Δt={delta_time:.3f}s: {data}")

        self.temp_bytes.extend(data)
        if len(self.temp_bytes) >= 20:
            self.process_data(self.temp_bytes[:20], delta_time)
            self.temp_bytes = self.temp_bytes[20:]

    def process_data(self, bytes_data, delta_time):
        print(f"Procesando datos del sensor en {self.position}...")
        if bytes_data[1] == 0x61:
            ax = self.get_signed_int16(bytes_data[3] << 8 | bytes_data[2]) / 32768 * 16
            ay = self.get_signed_int16(bytes_data[5] << 8 | bytes_data[4]) / 32768 * 16
            az = self.get_signed_int16(bytes_data[7] << 8 | bytes_data[6]) / 32768 * 16
            gx = self.get_signed_int16(bytes_data[9] << 8 | bytes_data[8]) / 32768 * 2000
            gy = self.get_signed_int16(bytes_data[11] << 8 | bytes_data[10]) / 32768 * 2000
            gz = self.get_signed_int16(bytes_data[13] << 8 | bytes_data[12]) / 32768 * 2000
            ang_x = self.get_signed_int16(bytes_data[15] << 8 | bytes_data[14]) / 32768 * 180
            ang_y = self.get_signed_int16(bytes_data[17] << 8 | bytes_data[16]) / 32768 * 180
            ang_z = self.get_signed_int16(bytes_data[19] << 8 | bytes_data[18]) / 32768 * 180

            self.device_data.update({
                "Position": self.position,
                "DeltaTime": round(delta_time, 3),
                "Ax": round(ax, 3),
                "Ay": round(ay, 3),
                "Az": round(az, 3),
                "Gx": round(gx, 3),
                "Gy": round(gy, 3),
                "Gz": round(gz, 3),
                "AngX": round(ang_x, 3),
                "AngY": round(ang_y, 3),
                "AngZ": round(ang_z, 3)
            })
            self.callback_method(self.device_data)

            # Almacenar datos para CSV
            self.data_list.append([time.time(), self.device_data])

    @staticmethod
    def get_signed_int16(value):
        if value >= 0x8000:
            value -= 0x10000
        return value

    async def save_to_csv(self, filename):
        """Guarda los datos recopilados en un archivo CSV"""
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Data"])  # Escribe encabezado
            for entry in self.data_list:
                writer.writerow(entry)
        print(f"Datos guardados en el CSV.")

async def main():
    csv_filename = "datos_sensor.csv"
    with open(csv_filename, mode="w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([ 
            "nombre", "DeltaTime", "Ax", "Ay", "Az", "Gx", "Gy", "Gz", "AngX", "AngY", "AngZ"
        ])

        def write_to_csv(data):
            csv_writer.writerow([
                data["Position"], data["DeltaTime"],
                data["Ax"], data["Ay"], data["Az"],
                data["Gx"], data["Gy"], data["Gz"],
                data["AngX"], data["AngY"], data["AngZ"]
            ])
            print(f"Datos escritos en el CSV: {data}")

        # Aquí debes editar la dirección MAC del sensor que quieres conectar
        device = {"mac": "dd:70:a7:9c:c7:0f", "nombre": "sensor 1", "position": "posición 1"}
        device_object = DeviceModel(device["nombre"], device["mac"], write_to_csv, device["position"])
        await device_object.open_device()
        await device_object.save_to_csv(csv_filename)

if __name__ == '__main__':
    asyncio.run(main())

