import time
import os
from db import get_recent, get_anomalies

THRESHOLDS = {
    "temp_f":                 {"max": 210},
    "discharge_pressure_psi": {"max": 250},
    "suction_pressure_psi":   {"max": 80},
    "rpm":                    {"min": 900},
    "oil_pressure_psi":       {"min": 20},
    "vibration_mmps":         {"max": 6.0}
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_latest():
    rows = get_recent(1)
    return rows[-1] if rows else None

def get_stats():
    rows = get_recent(200)
    total = len(rows)
    anomalies = sum(1 for r in rows if r[11] == 1)
    rate = (anomalies / total * 100) if total > 0 else 0
    return total, anomalies, round(rate, 1)

def format_status(key, value):
    t = THRESHOLDS.get(key, {})
    if "max" in t and value > t["max"]:
        return "FAULT"
    if "min" in t and value < t["min"]:
        return "FAULT"
    return "NORMAL"

def print_dashboard(latest, stats, anomalies):
    div = "=" * 59
    thin = "-" * 59

    print(div)
    print("  EMIT COMPRESSOR MONITORING SYSTEM")
    if latest:
        print(f"  Unit: {latest[1]}  |  Site: {latest[2]}")
        print(f"  Last Updated: {latest[0]}")
    print(div)

    print()
    print("  LIVE READINGS")
    print(f"  {thin}")

    if latest:
        sensors = [
            ("Temperature",      "temp_f",                 latest[5],  "F"),
            ("Discharge Press",  "discharge_pressure_psi", latest[4],  "PSI"),
            ("Suction Press",    "suction_pressure_psi",   latest[3],  "PSI"),
            ("RPM",              "rpm",                    latest[6],  ""),
            ("Oil Pressure",     "oil_pressure_psi",       latest[7],  "PSI"),
            ("Vibration",        "vibration_mmps",         latest[8],  "mm/s"),
        ]
        for label, key, value, unit in sensors:
            status = format_status(key, value)
            val_str = f"{value} {unit}".strip()
            print(f"  {label:<20} {val_str:<18} {status}")
    else:
        print("  No data yet. Start simulator and ingestion.")

    print()
    print(div)
    print()
    print("  STATISTICS  (last 200 readings)")
    print(f"  {thin}")
    total, anomaly_count, rate = stats
    print(f"  Total Readings       {total}")
    print(f"  Anomalies            {anomaly_count}")
    print(f"  Anomaly Rate         {rate}%")

    print()
    print(div)
    print()
    print("  RECENT ANOMALIES")
    print(f"  {thin}")

    if anomalies:
        for row in anomalies[-5:]:
            ts    = row[0]
            unit  = row[1]
            fault = row[2]
            temp  = row[3]
            print(f"  {ts}   {fault:<28} Temp: {temp} F")
    else:
        print("  No anomalies recorded yet.")

    print()
    print(div)

def main():
    print("Starting Compressor Dashboard...")
    time.sleep(1)
    while True:
        clear_screen()
        latest  = get_latest()
        stats   = get_stats()
        anomalies = get_anomalies(5)
        print_dashboard(latest, stats, anomalies)
        time.sleep(2)

if __name__ == "__main__":
    main()