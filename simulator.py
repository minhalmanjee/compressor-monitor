import paho.mqtt.client as mqtt
import time 
import json 
import random


BROKER = "broker.emqx.io"
PORT = 1883
TOPIC = "compressor/pressure"


BASELINE = 150.0
NOISE = 2.0

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="simulator")
client.connect(BROKER, PORT)
client.loop_start()


print("Simulator running, publishes every 1 second")


reading_count = 0

try:
    while True:
        reading_count += 1

        #inject anomaly spike every 30 secs
        if reading_count % 30 == 0:
            pressure = BASELINE + random.uniform(15, 25) #spike
            print(f"[Anomaly Injected] Pressure: {pressure:.2f} PSI")
        else:
            pressure = BASELINE + random.gauss(0, NOISE)
            print(f"Pressure: {pressure:.2f} PSI")

        payload = json.dumps({"pressure": round(pressure,2)})
        client.publish(TOPIC, payload)

        time.sleep(1)

except KeyboardInterrupt:
    print("\nSimulator Stopped")
    client.loop_stop()
    client.disconnect()


