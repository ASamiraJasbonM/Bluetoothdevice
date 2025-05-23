# myapp/management/commands/run_ble_script.py

import asyncio
import logging
import json
import re
import sys
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from bleak import BleakScanner, BleakClient, AdvertisementData
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from myapp.models import DatoSensor

# ───── Constants ─────
SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
CHARACTERISTIC_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"
_buffer = ""

# ───── Logging ─────
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ───── Utility Functions ─────
def clean_json_string(raw_data):
    if isinstance(raw_data, (bytes, bytearray)):
        raw_data = raw_data.decode("utf-8")
    if not isinstance(raw_data, str):
        return ""
    return raw_data.replace("\n", "").replace("\r", "").replace(" ", "")

def es_json_valido(cadena):
    return cadena.startswith("{") and cadena.endswith("}") and re.match(r'{.*}', cadena)

@sync_to_async
def insertar_datos_db(data, device_name):
    try:
        DatoSensor.objects.create(
            device=device_name,
            temperatura_corporal=data.get("temperatura_corporal", 0),
            temperatura_ambiental=data.get("temperatura_ambiental", 0),
            bpm=data.get("bpm", 0),
            avg_bpm=data.get("avg_bpm", 0),
            humedad=data.get("humedad", 0),
            estado="Conectado"
        )
        logger.info(f"✅ Datos insertados: {data}")
    except Exception as e:
        logger.error(f"❌ Error al insertar en la DB: {e}")

async def procesar_datos_segmentos(device_name, segmentos):
    global _buffer
    _buffer += segmentos
    while "{" in _buffer and "}" in _buffer:
        inicio = _buffer.find("{")
        fin = _buffer.find("}") + 1
        if fin > inicio:
            json_str = _buffer[inicio:fin]
            _buffer = _buffer[fin:]
            if es_json_valido(json_str):
                try:
                    data = json.loads(json_str)
                    logger.info(f"📊 Datos procesados: {data}")
                    await insertar_datos_db(data, device_name)
                except json.JSONDecodeError:
                    logger.warning(f"⚠️ JSON inválido: {json_str}")
                    _buffer = json_str

# ───── BLE Connect & Notify ─────
async def connect_ble_once():
    logger.info("🔍 Escaneando BLE...")
    target = None

    def detection_cb(device, adv: AdvertisementData):
        uuids = adv.service_uuids or []
        if SERVICE_UUID.lower() in [u.lower() for u in uuids]:
            nonlocal target
            target = device

    scanner = BleakScanner(detection_cb)
    await scanner.start()
    await asyncio.sleep(5)
    await scanner.stop()

    if not target:
        logger.error("❌ Dispositivo no encontrado.")
        return

    logger.info(f"🔗 Conectando a {target.name} ({target.address})")
    client = BleakClient(target)
    try:
        await client.connect()
        if client.is_connected:
            logger.info(f"✅ Conectado a {target.name}")

        # Read once immediately
        try:
            raw = await client.read_gatt_char(CHARACTERISTIC_UUID)
            texto = clean_json_string(raw)
            if texto:
                await procesar_datos_segmentos(target.name, texto)
        except Exception as e:
            logger.error(f"❌ Error lectura inicial: {e}")

        # Subscribe to notifications
        def notif_handler(_, data):
            segmento = clean_json_string(data)
            if segmento:
                asyncio.create_task(procesar_datos_segmentos(target.name, segmento))

        await client.start_notify(CHARACTERISTIC_UUID, notif_handler)
        logger.info("📡 Esperando notificaciones...")
        await asyncio.sleep(5)
        await client.stop_notify(CHARACTERISTIC_UUID)

    except Exception as e:
        logger.error(f"❌ Error en BLE: {e}")
    finally:
        if client.is_connected:
            await client.disconnect()
        logger.info("🔒 Desconectado.")

# ───── Management Command ─────
class Command(BaseCommand):
    help = "Run BLE connector every 15 seconds"

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler()

        def job_wrapper():
            logger.info("📅 Ejecutando tarea BLE programada")
            asyncio.run(connect_ble_once())

        # Schedule every 15 seconds, first run now
        scheduler.add_job(
            job_wrapper,
            trigger='interval',
            seconds=15,
            next_run_time=datetime.now()
        )

        scheduler.start()
        logger.info("⌛ Scheduler iniciado, tarea cada 15s.")

        # Keep process alive (Windows-safe)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler detenido por Ctrl+C.")
            scheduler.shutdown()
            sys.exit()
