import sqlite3
from datetime import datetime

DB_NAME = "compressor.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id                      INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp               TEXT,
            unit_id                 TEXT,
            site                    TEXT,
            suction_pressure_psi    REAL,
            discharge_pressure_psi  REAL,
            temp_f                  REAL,
            rpm                     REAL,
            oil_pressure_psi        REAL,
            vibration_mmps          REAL,
            fault_type              TEXT,
            status                  TEXT,
            is_anomaly              INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized")

def save_reading(data, is_anomaly=0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO readings (
            timestamp, unit_id, site,
            suction_pressure_psi, discharge_pressure_psi,
            temp_f, rpm, oil_pressure_psi, vibration_mmps,
            fault_type, status, is_anomaly
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        data.get("timestamp", datetime.now().isoformat()),
        data.get("unit_id", "COMP-001"),
        data.get("site", "EMIT-SITE-TX-01"),
        data.get("suction_pressure_psi"),
        data.get("discharge_pressure_psi"),
        data.get("temp_f"),
        data.get("rpm"),
        data.get("oil_pressure_psi"),
        data.get("vibration_mmps"),
        data.get("fault_type", "NONE"),
        data.get("status", "NORMAL"),
        is_anomaly
    ))
    conn.commit()
    conn.close()

def get_recent(n=200):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, unit_id, site,
               suction_pressure_psi, discharge_pressure_psi,
               temp_f, rpm, oil_pressure_psi, vibration_mmps,
               fault_type, status, is_anomaly
        FROM readings
        ORDER BY id DESC
        LIMIT ?
    """, (n,))
    rows = cursor.fetchall()
    conn.close()
    return list(reversed(rows))

def get_anomalies(n=50):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, unit_id, fault_type, 
               temp_f, discharge_pressure_psi, rpm, oil_pressure_psi
        FROM readings
        WHERE is_anomaly = 1
        ORDER BY id DESC
        LIMIT ?
    """, (n,))
    rows = cursor.fetchall()
    conn.close()
    return list(reversed(rows))