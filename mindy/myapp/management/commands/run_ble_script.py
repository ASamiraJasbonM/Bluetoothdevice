'''from django.core.management.base import BaseCommand
import asyncio
import json
import re
from bleak import BleakScanner, BleakClient, AdvertisementData
from myapp.models import DatoSensor
import os
import django

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mindy.settings")
django.setup()

# UUIDs
SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
CHARACTERISTIC_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"
buffer = ""

# Utils
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

# BLE logic
async def connect_ble():
    print("🔍 Buscando dispositivo BLE...")

    target_device = None

    def detection_callback(device, advertisement_data: AdvertisementData):
        service_uuids = advertisement_data.service_uuids or []
        if SERVICE_UUID.lower() in [uuid.lower() for uuid in service_uuids]:
            print(f"🎯 Dispositivo objetivo detectado: {device.address} con servicio {SERVICE_UUID}")
            nonlocal target_device
            target_device = device

    scanner = BleakScanner(detection_callback)
    await scanner.start()
    await asyncio.sleep(5)
    await scanner.stop()

    if target_device:
        print(f"🔗 Intentando conectar con {target_device.address}...")
        client = BleakClient(target_device)
        try:
            await client.connect()
            print("✅ Conectado al dispositivo BLE")

            def notification_handler(sender, data):
                print(f"📥 Data received from {sender}: {data}")
                raw_data = clean_json_string(data)
                if raw_data:
                    procesar_datos(raw_data)

            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)

            print("📡 Recibiendo datos...")
            while True:
                await asyncio.sleep(1)

        except Exception as e:
            print(f"❌ Error al conectar o recibir datos: {e}")
        finally:
            if client.is_connected:
                await client.disconnect()
            print("🔒 Conexión BLE cerrada.")
    else:
        print("❌ Dispositivo con UUID objetivo no encontrado.")

# Django command
class Command(BaseCommand):
    help = "Conecta al dispositivo BLE y guarda datos en la base de datos"

    def handle(self, *args, **kwargs):
        asyncio.run(connect_ble())
'''

'''import asyncio
import logging
import json
import re
from myapp.models import DatoSensor
from bleak import BleakScanner, BleakClient, AdvertisementData

# Constants
SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
CHARACTERISTIC_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"
buffer = ""

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Utils for processing data
def clean_json_string(raw_data):
    if isinstance(raw_data, (bytes, bytearray)):
        raw_data = raw_data.decode("utf-8")
    if not isinstance(raw_data, str):
        return ""
    return raw_data.replace("\n", "").replace("\r", "").replace(" ", "")

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

def es_json_valido(cadena):
    return cadena.startswith("{") and cadena.endswith("}") and re.match(r'{.*}', cadena)

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
                    logger.info(f"Datos procesados: {data}")
                    insertar_datos_db(data)
                except json.JSONDecodeError:
                    logger.warning("⚠️ Error decodificando JSON: %s", json_str)
                    buffer = json_str

# BLE connection and notification handler
async def connect_ble():
    logger.info("🔍 Buscando dispositivo BLE...")

    target_device = None

    def detection_callback(device, advertisement_data: AdvertisementData):
        service_uuids = advertisement_data.service_uuids or []
        if SERVICE_UUID.lower() in [uuid.lower() for uuid in service_uuids]:
            logger.info(f"🎯 Dispositivo objetivo detectado: {device.address} con servicio {SERVICE_UUID}")
            nonlocal target_device
            target_device = device

    scanner = BleakScanner(detection_callback)
    await scanner.start()
    await asyncio.sleep(5)
    await scanner.stop()

    if target_device:
        logger.info(f"🔗 Intentando conectar con {target_device.address}...")
        client = BleakClient(target_device)
        try:
            await client.connect()
            logger.info("✅ Conectado al dispositivo BLE")

            # Read the characteristic data once (or on-demand)
            try:
                raw_data = await client.read_gatt_char(CHARACTERISTIC_UUID)
                logger.info(f"📥 Data read from GATT Characteristic: {raw_data}")
                raw_data = clean_json_string(raw_data)
                if raw_data:
                    procesar_datos(raw_data)
            except Exception as e:
                logger.error(f"❌ Error reading GATT characteristic: {e}")

            # Handler for receiving notifications
            def notification_handler(sender, data):
                logger.info(f"📥 Data received from {sender}: {data}")
                raw_data = clean_json_string(data)
                if raw_data:
                    procesar_datos(raw_data)

            # Start receiving notifications
            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)

            logger.info("📡 Recibiendo datos...")
            while True:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"❌ Error al conectar o recibir datos: {e}")
        finally:
            if client.is_connected:
                await client.disconnect()
            logger.info("🔒 Conexión BLE cerrada.")
    else:
        logger.error("❌ Dispositivo con UUID objetivo no encontrado.")

# Entry point for Django management command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Conecta al dispositivo BLE y guarda datos en la base de datos"

    def handle(self, *args, **kwargs):
        asyncio.run(connect_ble())'''



'''import logging, sys, signal, re, json, asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from bleak import BleakScanner, BleakClient, AdvertisementData
from asgiref.sync import sync_to_async
from myapp.models import DatoSensor
from django.core.management.base import BaseCommand

# Constants
SERVICE_UUID = "19B10000-E8F2-537E-4F6C-D104768A1214"
CHARACTERISTIC_UUID = "19B10001-E8F2-537E-4F6C-D104768A1214"
buffer = ""

# Logging setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ──────── Utility Functions ────────

def clean_json_string(raw_data):
    if isinstance(raw_data, (bytes, bytearray)):
        raw_data = raw_data.decode("utf-8")
    if not isinstance(raw_data, str):
        return ""
    return raw_data.replace("\n", "").replace("\r", "").replace(" ", "")

def es_json_valido(cadena):
    return cadena.startswith("{") and cadena.endswith("}") and re.match(r'{.*}', cadena)

@sync_to_async
def insertar_datos_db(data, name):
    try:
        DatoSensor.objects.create(
            device = name,
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

async def procesar_datos(datos, name):
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
                    logger.info(f"Datos procesados: {data}")
                    await insertar_datos_db(data, name)
                except json.JSONDecodeError:
                    logger.warning("⚠️ Error decodificando JSON: %s", json_str)
                    buffer = json_str

# ──────── BLE Connection and Notifications ────────

async def connect_ble():
    logger.info("🔍 Buscando dispositivo BLE...")
    target_device = None

    def detection_callback(device, advertisement_data: AdvertisementData):
        service_uuids = advertisement_data.service_uuids or []
        if SERVICE_UUID.lower() in [uuid.lower() for uuid in service_uuids]:
            logger.info(f"🎯 Dispositivo detectado: {device.address}")
            nonlocal target_device
            target_device = device

    scanner = BleakScanner(detection_callback)
    await scanner.start()
    await asyncio.sleep(5)
    await scanner.stop()

    if target_device:
        logger.info(f"🔗 Conectando a {target_device.address}... {target_device.name}")
        client = BleakClient(target_device)
        try:
            await client.connect()
            logger.info("✅ Conexión establecida con el dispositivo BLE")

            # Leer una vez al principio (opcional)
            try:
                raw_data = await client.read_gatt_char(CHARACTERISTIC_UUID)
                logger.info(f"📥 Datos iniciales del GATT: {raw_data}")
                raw_data = clean_json_string(raw_data)
                if raw_data:
                    await procesar_datos(raw_data, target_device.name)
            except Exception as e:
                logger.error(f"❌ Error al leer característica GATT: {e}")

            # Handler para notificaciones
            def notification_handler(sender, data):
                logger.info(f"📥 Notificación recibida de {sender}: {data}")
                raw_data = clean_json_string(data)
                if raw_data:
                    asyncio.create_task(procesar_datos(raw_data))

            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
            logger.info(f"is connected {client.is_connected()}")
            logger.info("📡 Esperando datos...")
            while True:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"❌ Error durante la conexión o lectura: {e}")
        finally:
            if client.is_connected:
                await client.disconnect()
            logger.info("🔒 Conexión BLE cerrada.")
    else:
        logger.error("❌ Dispositivo BLE con el UUID objetivo no encontrado.")

# ──────── Django Management Command ────────

class Command(BaseCommand):
    help = "Start BLE listener and run it every 3 hours"

    def handle(self, *args, **kwargs):
        scheduler = BackgroundScheduler()

        def run_job():
            logger.info("📅 Running BLE job...")
            asyncio.run(connect_ble())

        # Run every 3 hours
        scheduler.add_job(run_job, 'interval', seconds=15)

        logger.info("⏳ Scheduler started. First BLE job running now...")
        run_job()  # Run immediately first time

        scheduler.start()

        # Keep the command alive
        try:
            signal.pause()  # Wait for signals
        except (KeyboardInterrupt, SystemExit):
            logger.info("🛑 Scheduler stopped by user.")
            scheduler.shutdown()
            sys.exit()

'''

# myapp/management/commands/run_ble_loop.py

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
