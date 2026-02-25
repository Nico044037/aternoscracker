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
    "minefort.com"
]

COMMON_NAMES = [
    "mc","play","survival","pvp","smp","lobby",
    "skyblock","bedwars","lifesteal","network"
]

# Thread-safe storage for seen servers
seen_servers = set()
lock = threading.Lock()

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
        print(f"[API FAILED] {address} -> {e}")

def scan():
    global seen_servers

    while True:
        try:
            name = generate_name()
            domain = random.choice(DOMAINS)
            address = f"{name}.{domain}"

            # Prevent duplicate scans/logs
            with lock:
                if address in seen_servers:
                    continue
                seen_servers.add(address)

            server = JavaServer.lookup(address, timeout=TIMEOUT)
            status = server.status()

            # Skip invalid or empty servers
            if not status or status.players.max == 0:
                return
            if status.players.online == 0 and status.players.max == 0:
                return

            version = status.version.name if status.version else "unknown"

            # Extra Minefort validation (ensures it's really a Minefort host)
            if not address.endswith(".minefort.com"):
                return

            print(f"[FOUND MINEFORT] {address} | {status.players.online}/{status.players.max} | {version}")

            send_to_api(address, status.players.online, status.players.max, version)

        except Exception:
            pass

def main():
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=scan, daemon=True)
        t.start()
        threads.append(t)

    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
