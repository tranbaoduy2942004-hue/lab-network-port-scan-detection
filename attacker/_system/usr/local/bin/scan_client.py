#!/usr/bin/env python3
import socket
import sys
from pathlib import Path

TARGET = "172.29.111.20"
LOG = Path("/home/ubuntu/scan-lab/client.log")

def connect(port):
    try:
        with socket.create_connection((TARGET, port), timeout=3) as s:
            response = s.recv(100).decode().strip()
            if response != "PORT_OPEN":
                return False
        return True
    except OSError:
        return False

def record(message):
    with LOG.open("a") as f:
        f.write(message + "\n")
    print(message, flush=True)

if len(sys.argv) != 2:
    sys.exit("Usage: scan_client.py normal|scan")

mode = sys.argv[1]

if mode == "normal":
    if not connect(9001):
        sys.exit("NORMAL_CONNECT_FAILED")
    record("NORMAL_CONNECT_OK port=9001")

elif mode == "scan":
    success = []
    for port in range(9001, 9009):
        if connect(port):
            success.append(port)
            print(f"TCP_OPEN: {port}")

    if len(success) != 8:
        sys.exit(f"SCAN_INCOMPLETE: {len(success)}/8")

    record("PORT_SCAN_COMPLETED count=8")

else:
    sys.exit("UNKNOWN_MODE")
