import threading
import random
import time
import requests
from mcstatus import JavaServer

API_URL = "https://web-production-79e19.up.railway.app/log"
API_KEY = "secret123"

THREADS = 25
TIMEOUT = 2

DOMAINS = [
    "aternos.me",
    "aternos.org"
]

COMMON_NAMES = [
    "mc","play","survival","pvp","smp","lobby",
    "skyblock","bedwars","lifesteal","network"
]
def generate_name():
    base = random.choice(COMMON_NAMES)
    return f"{base}{random.randint(1,999)}"

def send_to_api(address, online, max_players, version):
    payload = {
        "ip": address,
        "info": {
            "players": online,
            "max_players": max_players,
            "version": version,
            "source": "railway-finder"
        }
    }

    headers = {"x-api-key": API_KEY}

    try:
        r = requests.post(API_URL, json=payload, headers=headers, timeout=5)
        print(f"[API {r.status_code}] {address}")
    except Exception as e:
        print(f"[API FAILED] {e}")

def scan():
    while True:
        try:
            name = generate_name()
            domain = random.choice(DOMAINS)
            address = f"{name}.{domain}"

            server = JavaServer.lookup(address, timeout=TIMEOUT)
            status = server.status()

            if status.players.max == 0:
                continue
            if status.players.online == 0 and status.players.max == 0:
                continue

            version = status.version.name if status.version else "unknown"
            print(f"[FOUND] {address}")

            send_to_api(address, status.players.online, status.players.max, version)

        except:
            pass

def main():
    for _ in range(THREADS):
        threading.Thread(target=scan, daemon=True).start()

    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
