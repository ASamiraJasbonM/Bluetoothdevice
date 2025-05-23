import asyncio
import json
import re
from bleak import BleakScanner, BleakClient
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")
django.setup()
from .models import DatoSensor

SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
CHARACTERISTIC_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"
buffer = ""

def clean_json_string(raw_data):
    if isinstance(raw_data, (bytes, bytearray)):  
        raw_data = raw_data.decode("utf-8")  
    if not isinstance(raw_data, str):
        return ""
    return raw_data.replace("\n", "").replace("\r", "").replace(" ", "")

def es_json_valido(cadena):
    return cadena.startswith("{") and cadena.endswith("}") and re.match(r'{.*}', cadena)

def insertar_datos_db(data):
    try:
        DatoSensor.objects.create(
            temperatura_corporal=data.get("temperatura_corporal", 0),
            temperatura_ambiental=data.get("temperatura_ambiental", 0),
            bpm=data.get("bpm", 0),
            avg_bpm=data.get("avg_bpm", 0),
            humedad=data.get("humedad", 0),
            estado="Conectado"
        )
        print("✅ Datos insertados:", data)
    except Exception as e:
        print("❌ Error al insertar en la DB:", e)

def procesar_datos(datos):
    global buffer
    buffer += datos

    while "{" in buffer and "}" in buffer:
        inicio = buffer.find("{")
        fin = buffer.find("}") + 1
        
        if fin > inicio:
            json_str = buffer[inicio:fin]
            buffer = buffer[fin:]
            
            if es_json_valido(json_str):  
                try:
                    data = json.loads(json_str)
                    insertar_datos_db(data)
                except json.JSONDecodeError:
                    print("⚠️ Error decodificando JSON:", json_str)
                    buffer = json_str

async def connect_ble():
    print("🔍 Buscando dispositivo BLE...")
    devices = await BleakScanner.discover()
    
    for device in devices:
        if device.name and "Seeed Studio XIAO nRF52840" in device.name:
            print(f"🔗 Dispositivo encontrado: {device.name} - {device.address}")
            client = BleakClient(device.address)
            try:
                await client.connect()
                print("✅ Conectado al dispositivo BLE")

                def notification_handler(sender, data):
                    raw_data = clean_json_string(data)
                    if raw_data:
                        procesar_datos(raw_data)

                await client.start_notify(CHARACTERISTIC_UUID, notification_handler)

                print("📡 Recibiendo datos...")
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("🛑 Conexión finalizada por el usuario.")
            finally:
                if client.is_connected:
                    await client.disconnect()
                print("🔒 Conexión BLE cerrada.")
    print("❌ Dispositivo no encontrado.")