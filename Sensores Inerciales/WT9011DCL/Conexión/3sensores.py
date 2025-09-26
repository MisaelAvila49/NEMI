import asyncio
from bleak import BleakClient

# Lista con las MAC de tus 3 sensores
SENSORS = [
    {"mac": "dd:70:a7:9c:c7:0f", "name": "Sensor 1"},
    {"mac": "dd:70:a7:9c:c7:10", "name": "Sensor 2"},
    {"mac": "dd:70:a7:9c:c7:11", "name": "Sensor 3"},
]

# UUID de característica de lectura
READ_CHARACTERISTIC_UUID = "0000ffe4-0000-1000-8000-00805f9a34fb"


def get_signed_int16(value):
    if value >= 0x8000:
        value -= 0x10000
    return value


def make_callback(sensor_name):
    def on_data_received(sender, data: bytearray):
        if len(data) < 20:
            return
        packet_type = data[1]

        if packet_type == 0x61:  # Acelerómetro + Giroscopio
            ax = get_signed_int16(data[3] << 8 | data[2]) / 32768 * 16
            ay = get_signed_int16(data[5] << 8 | data[4]) / 32768 * 16
            az = get_signed_int16(data[7] << 8 | data[6]) / 32768 * 16
            gx = get_signed_int16(data[9] << 8 | data[8]) / 32768 * 2000
            gy = get_signed_int16(data[11] << 8 | data[10]) / 32768 * 2000
            gz = get_signed_int16(data[13] << 8 | data[12]) / 32768 * 2000
            print(f"[{sensor_name}] ACEL/GYRO -> "
                f"Ax={ax:.3f}, Ay={ay:.3f}, Az={az:.3f}, "
                f"Gx={gx:.3f}, Gy={gy:.3f}, Gz={gz:.3f}")

        elif packet_type == 0x71:  # Magnetómetro
            mx = get_signed_int16(data[3] << 8 | data[2])
            my = get_signed_int16(data[5] << 8 | data[4])
            mz = get_signed_int16(data[7] << 8 | data[6])
            print(f"[{sensor_name}] MAG -> Mx={mx}, My={my}, Mz={mz}")
    return on_data_received


async def connect_sensor(sensor):
    async with BleakClient(sensor["mac"]) as client:
        print(f"✅ Conectado a {sensor['name']} ({sensor['mac']})")
        await client.start_notify(
            READ_CHARACTERISTIC_UUID,
            make_callback(sensor["name"])
        )
        while True:  # Mantener conexión activa
            await asyncio.sleep(1)


async def main():
    await asyncio.gather(*(connect_sensor(s) for s in SENSORS))


if __name__ == "__main__":
    asyncio.run(main())
