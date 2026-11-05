# Network Port Scan Detection

Lab ID: lab-network-port-scan-detection

## Topology
- attacker: 172.29.111.10
- target: 172.29.111.20
- soc: 172.29.111.30

## Installation on Labtainer HOST
imodule https://raw.githubusercontent.com/tranbaoduy2942004-hue/lab-network-port-scan-detection/main/imodule.tar
labtainer lab-network-port-scan-detection

## Practice

ATTACKER:
python3 /usr/local/bin/scan_client.py normal
python3 /usr/local/bin/scan_client.py scan

TARGET:
tail -n 10 /home/ubuntu/scan-lab/connections.log

SOC:
python3 /usr/local/bin/soc_detect.py collect
python3 /usr/local/bin/soc_detect.py detect

HOST:
checkwork lab-network-port-scan-detection

Expected: 5/5 Y

## Safety
Run only in the authorized isolated lab network.
