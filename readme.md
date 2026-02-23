# Gas Compressor Digital Twin & Predictive Alert System

A real-time IIoT monitoring system that simulates an industrial gas compressor, detects faults using anomaly detection, streams live data to AWS cloud infrastructure, and visualizes sensor telemetry on a live Grafana dashboard.

---

## Architecture

```
[Simulator] → [AWS IoT Core] → [IoT Rule] → [Lambda] → [DynamoDB]
                                                     ↓
                                                   [SNS]
                                                     ↓
                                               [Email Alert]

[DynamoDB] → [Flask API] → [Grafana Cloud Dashboard]
```

---

## Stack

| Layer | Technology |
|---|---|
| Edge Simulation | Python |
| Messaging Protocol | MQTT over TLS (port 8883) |
| Cloud Broker | AWS IoT Core |
| Serverless Processing | AWS Lambda |
| Database | AWS DynamoDB |
| Alerting | AWS SNS |
| Visualization | Grafana Cloud + Infinity Datasource |
| Local API | Flask |

---

## Sensors Monitored

| Sensor | Unit | Normal Range |
|---|---|---|
| Temperature | °F | < 210 |
| Discharge Pressure | PSI | < 250 |
| Suction Pressure | PSI | < 80 |
| RPM | — | > 900 |
| Oil Pressure | PSI | > 20 |
| Vibration | mm/s | < 6.0 |

---

## Fault Types

- `HIGH_TEMP`
- `HIGH_DISCHARGE_PRESSURE`
- `LOW_OIL_PRESSURE`
- `RPM_DROP`
- `VIBRATION_SPIKE`

---

## Fault Detection

Dual-layer detection:

- **Edge layer** — Z-score anomaly detection on rolling 30-reading window
- **Cloud layer** — hard threshold checks in Lambda on every incoming message

---

## Project Structure

```
compressor-monitor/
├── simulator.py          # Generates sensor readings, publishes to AWS IoT Core
├── ingestion.py          # Subscribes to MQTT, runs local anomaly detection
├── db.py                 # SQLite schema and read/write functions
├── dashboard.py          # Terminal-based live monitoring dashboard
├── api.py                # Flask API serving DynamoDB data to Grafana
├── requirements.txt
├── certs/
│   ├── AmazonRootCA1.pem
│   ├── compressor.cert.pem
│   └── compressor.private.key
└── aws/
    └── lambda_function.py
```

---

## Running Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run all components in separate terminals:

```bash
# Terminal 1 — publish sensor data to AWS IoT Core
python simulator.py

# Terminal 2 — local anomaly detection and SQLite storage
python ingestion.py

# Terminal 3 — terminal monitoring dashboard
python dashboard.py

# Terminal 4 — Flask API for Grafana
python api.py
```

Expose API publicly for Grafana:

```bash
ngrok http 5050
```

---

## AWS Infrastructure

- **IoT Core Thing** — `COMP-001` registered with X.509 certificates
- **IoT Rule** — forwards all messages on `compressor/telemetry` to Lambda
- **Lambda** — processes each reading, stores to DynamoDB, triggers SNS on fault
- **DynamoDB Table** — `CompressorTelemetry` (partition key: `unit_id`, sort key: `unix_ts`)
- **SNS Topic** — `CompressorAlerts` with email subscription

---

## Data Schema

Each reading published to AWS:

```json
{
  "unit_id": "COMP-001",
  "site": "EMIT-SITE-TX-01",
  "timestamp": "2026-02-23T00:10:01Z",
  "unix_ts": 1740268201.123,
  "suction_pressure_psi": 51.3,
  "discharge_pressure_psi": 198.7,
  "temp_f": 181.2,
  "rpm": 1198.4,
  "oil_pressure_psi": 34.6,
  "vibration_mmps": 2.4,
  "fault_type": "NONE",
  "status": "NORMAL"
}
```

---

## Grafana Dashboard

Live dashboard panels:

- Temperature over time
- Discharge Pressure over time
- RPM over time
- Oil Pressure over time
- Vibration over time
- Fault Log table (most recent faults)

Auto-refreshes every 5 seconds via Infinity datasource connected to Flask API.
