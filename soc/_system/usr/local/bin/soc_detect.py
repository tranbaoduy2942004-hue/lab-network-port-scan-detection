#!/usr/bin/env python3
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from urllib.request import urlopen

BASE = Path("/home/ubuntu/scan-lab")
EVENTS = BASE / "events.log"
ALERTS = BASE / "alerts.log"

def collect():
    with urlopen("http://172.29.111.20:8080/events",
                 timeout=8) as response:
        records = json.load(response)["events"]

    with EVENTS.open("w") as f:
        for event in records:
            f.write(json.dumps(event) + "\n")

    print(f"SOC_COLLECT_OK: {len(records)} events")

def detect():
    if not EVENTS.exists():
        sys.exit("RUN_COLLECT_FIRST")

    records = [json.loads(x) for x in
               EVENTS.read_text().splitlines() if x.strip()]

    records.sort(key=lambda x: x["time"])
    found = {}

    for event in records:
        ip = event["source_ip"]
        now = datetime.fromisoformat(event["time"])
        history = found.setdefault(ip, [])
        history.append((now, event["destination_port"]))
        history[:] = [(t, p) for t, p in history
                      if now - t <= timedelta(seconds=120)]

        ports = {p for _, p in history}
        if len(ports) >= 5:
            alert = {"event": "PORT_SCAN_DETECTED",
                     "source_ip": ip,
                     "unique_ports": len(ports)}
            with ALERTS.open("a") as f:
                f.write(json.dumps(alert) + "\n")
            print(json.dumps(alert))
            print("SOC_DETECTION_OK")
            return

    print("NO_PORT_SCAN_DETECTED")

if len(sys.argv) != 2:
    sys.exit("Usage: soc_detect.py collect|detect")

if sys.argv[1] == "collect":
    collect()
elif sys.argv[1] == "detect":
    detect()
else:
    sys.exit("UNKNOWN_MODE")
