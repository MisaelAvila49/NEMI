import asyncio
import time
from bleak import BleakClient

# Dirección MAC del sensor (edítala por la de tu dispositivo)
SENSOR_MAC = "dd:70:a7:9c:c7:0f"

# UUIDs de comunicación
SERVICE_UUID = "0000ffe5-0000-1000-8000-00805f9a34fb"
READ_CHARACTERISTIC_UUID = "0000ffe4-0000-1000-8000-00805f9a34fb"


def get_signed_int16(value):
    """Convierte un entero de 16 bits en número con signo"""
    if value >= 0x8000:
        value -= 0x10000
    return value


def on_data_received(sender, data: bytearray):
    """Callback cuando llegan datos del sensor"""
    if len(data) < 20:
        return

    # Tipo de paquete (0x61: acel/gyro/ángulo, 0x71: magnetómetro)
    packet_type = data[1]

    if packet_type == 0x61:  # Acelerómetro + Giroscopio
        ax = get_signed_int16(data[3] << 8 | data[2]) / 32768 * 16
        ay = get_signed_int16(data[5] << 8 | data[4]) / 32768 * 16
        az = get_signed_int16(data[7] << 8 | data[6]) / 32768 * 16
        gx = get_signed_int16(data[9] << 8 | data[8]) / 32768 * 2000
        gy = get_signed_int16(data[11] << 8 | data[10]) / 32768 * 2000
        gz = get_signed_int16(data[13] << 8 | data[12]) / 32768 * 2000

        print(f"[ACEL/GYRO] Ax={ax:.3f}, Ay={ay:.3f}, Az={az:.3f}, "
              f"Gx={gx:.3f}, Gy={gy:.3f}, Gz={gz:.3f}")

    elif packet_type == 0x71:  # Magnetómetro
        mx = get_signed_int16(data[3] << 8 | data[2])
        my = get_signed_int16(data[5] << 8 | data[4])
        mz = get_signed_int16(data[7] << 8 | data[6])

        print(f"[MAG] Mx={mx}, My={my}, Mz={mz}")


async def main():
    async with BleakClient(SENSOR_MAC) as client:
        print("Conectado al sensor WT901BLE")

        # Iniciar notificaciones
        await client.start_notify(READ_CHARACTERISTIC_UUID, on_data_received)

        print("Recibiendo datos... (Ctrl+C para salir)")
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())

