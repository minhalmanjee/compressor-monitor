#This is the "cloud server" side. It subscribes to the same MQTT topic, receives every reading the simulator publishes, runs anomaly detection on it, and saves it to the database.
from platform import win32_edition
import paho.mqtt.client as mqtt
import json
import anomaly
from db import init_db, save_reading



BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "compressor/pressure"

WINDOW = []
WINDOW_SIZE = 30

def is_anomaly(pressure):
    if len(WINDOW) < 10:
        return False
    mean = sum(WINDOW) / len(WINDOW)
    std = (sum((x-mean) ** 2 for x in WINDOW) / len(WINDOW)) ** 0.5
    return pressure > mean + 2 * std #true if pressure > 

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to broker. Listening on '{TOPIC}' \n")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    pressure = data["pressure"]

    anomaly = is_anomaly(pressure)

    WINDOW.append(pressure)
    if len(WINDOW) > WINDOW_SIZE:
        WINDOW.pop(0)

    save_reading(pressure, is_anomaly=int(anomaly))

    status = "Anomaly found" if anomaly else "OK"
    print(f"[{status}] Pressure: {pressure: .2f} PSI") 


init_db()
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id = "ingestion")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT)
client.loop_forever()