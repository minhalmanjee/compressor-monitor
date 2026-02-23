import paho.mqtt.client as mqtt
import json
import numpy as np
from datetime import datetime
from db import init_db, save_reading

BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "compressor/telemetry"

# Rolling window for each sensor (for Z-score)
WINDOWS = {
    "temp_f":                 [],
    "discharge_pressure_psi": [],
    "suction_pressure_psi":   [],
    "rpm":                    [],
    "oil_pressure_psi":       [],
    "vibration_mmps":         []
}
WINDOW_SIZE = 30

# Hard thresholds (backup layer)
THRESHOLDS = {
    "temp_f":                 {"max": 210},
    "discharge_pressure_psi": {"max": 250},
    "suction_pressure_psi":   {"max": 80},
    "rpm":                    {"min": 900},
    "oil_pressure_psi":       {"min": 20},
    "vibration_mmps":         {"max": 6.0}
}

def zscore_anomaly(key, value):
    window = WINDOWS[key]
    if len(window) < 10:
        return False
    mean = np.mean(window)
    std = np.std(window)
    if std == 0:
        return False
    z = abs((value - mean) / std)
    return z > 3.0

def threshold_anomaly(key, value):
    t = THRESHOLDS[key]
    if "max" in t and value > t["max"]:
        return True
    if "min" in t and value < t["min"]:
        return True
    return False

def update_window(key, value):
    WINDOWS[key].append(value)
    if len(WINDOWS[key]) > WINDOW_SIZE:
        WINDOWS[key].pop(0)

def detect_anomaly(data):
    anomalies = []
    for key in WINDOWS:
        value = data[key]
        z_flag = zscore_anomaly(key, value)
        t_flag = threshold_anomaly(key, value)
        update_window(key, value)
        if z_flag or t_flag:
            method = "Z-SCORE" if z_flag else "THRESHOLD"
            anomalies.append(f"{key}={value} [{method}]")
    return anomalies

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected to broker. Listening on '{TOPIC}'\n")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    anomalies = detect_anomaly(data)
    is_anomaly = len(anomalies) > 0

    save_reading(data, is_anomaly=int(is_anomaly))

    if is_anomaly:
        print(f" ANOMALY DETECTED [{data['timestamp']}]")
        for a in anomalies:
            print(f"   {a}")
    else:
        print(f"OK [{data['timestamp']}] "
              f"Temp:{data['temp_f']}°F | "
              f"RPM:{data['rpm']} | "
              f"Oil:{data['oil_pressure_psi']}PSI")

init_db()
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ingestion")
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT)
client.loop_forever()