import paho.mqtt.client as mqtt
import time
import json
import random
import numpy as np
from datetime import datetime, timezone
import ssl

# AWS IoT Core
ENDPOINT  = "a30inna2hxfw26-ats.iot.us-east-2.amazonaws.com"
PORT      = 8883
TOPIC     = "compressor/telemetry"

# Certificates
CERT_DIR  = "certs/"
CA_CERT   = CERT_DIR + "AmazonRootCA1.pem"
CERT_FILE = CERT_DIR + "compressor.cert.pem"
KEY_FILE  = CERT_DIR + "compressor.private.key"

# MQTT setup with TLS
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to AWS IoT Core successfully")
    else:
        print(f"Connection failed: {reason_code}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="compressor")
client.tls_set(
    ca_certs=CA_CERT,
    certfile=CERT_FILE,
    keyfile=KEY_FILE,
    tls_version=ssl.PROTOCOL_TLSv1_2
)
client.on_connect = on_connect
client.connect(ENDPOINT, PORT)
client.loop_start()


# Realistic gas compressor parameters
CONFIG = {
    "unit_id": "COMP-001",
    "site": "EMIT-SITE-TX-01",
    "suction_pressure":   {"base": 50,   "noise": 2,   "fault_delta": +25},
    "discharge_pressure": {"base": 200,  "noise": 5,   "fault_delta": +50},
    "temp_f":             {"base": 180,  "noise": 3,   "fault_delta": +40},
    "rpm":                {"base": 1200, "noise": 10,  "fault_delta": -300},
    "oil_pressure":       {"base": 35,   "noise": 1.5, "fault_delta": -18},
    "vibration_mmps":     {"base": 2.5,  "noise": 0.3, "fault_delta": +4.5},
}

FAULT_TYPES = [
    "HIGH_TEMP",
    "HIGH_DISCHARGE_PRESSURE",
    "LOW_OIL_PRESSURE",
    "RPM_DROP",
    "VIBRATION_SPIKE"
]

def generate_reading(fault_type=None):
    is_fault = fault_type is not None

    def val(key):
        c = CONFIG[key]
        noise = np.random.normal(0, c["noise"])
        delta = c["fault_delta"] if is_fault else 0
        return round(c["base"] + noise + delta, 2)

    return {
        "unit_id":                CONFIG["unit_id"],
        "site":                   CONFIG["site"],
        "timestamp":              datetime.now(timezone.utc).isoformat(),
        "unix_ts":                round(time.time(), 3),
        "suction_pressure_psi":   val("suction_pressure"),
        "discharge_pressure_psi": val("discharge_pressure"),
        "temp_f":                 val("temp_f"),
        "rpm":                    val("rpm"),
        "oil_pressure_psi":       val("oil_pressure"),
        "vibration_mmps":         val("vibration_mmps"),
        "fault_type":             fault_type if is_fault else "NONE",
        "status":                 "FAULT" if is_fault else "NORMAL"
    }

def pick_fault():
    return random.choice(FAULT_TYPES) if random.random() < 0.05 else None

# MQTT setup


print("=" * 55)
print("  COMPRESSOR SIMULATOR ")
print("=" * 55)

reading_count = 0
try:
    while True:
        reading_count += 1
        fault = pick_fault()
        reading = generate_reading(fault_type=fault)

        payload = json.dumps(reading)
        client.publish(TOPIC, payload)

        icon = "FAULT" if fault else "NORMAL"
        print(f"\n{icon} [{reading['timestamp']}]")
        print(f"   Temp:      {reading['temp_f']} °F")
        print(f"   Discharge: {reading['discharge_pressure_psi']} PSI")
        print(f"   Suction:   {reading['suction_pressure_psi']} PSI")
        print(f"   RPM:       {reading['rpm']}")
        print(f"   Oil:       {reading['oil_pressure_psi']} PSI")
        print(f"   Vibration: {reading['vibration_mmps']} mm/s")
        if fault:
            print(f" FAULT: {fault}")

        time.sleep(2)

except KeyboardInterrupt:
    print("\nSimulator stopped.")
    client.loop_stop()
    client.disconnect()