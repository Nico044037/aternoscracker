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

# Only these servers will be logged (even if others are found)
WHITELIST = {
    "play.minefort.com",
    "mc.minefort.com",
    "survival.minefort.com"
}

seen_servers = set()
lock = threading.Lock()

def generate_name():
    base = random.choice(COMMON_NAMES)
    return f"{base}{random.randint(1,999)}"

def is_whitelisted(address: str) -> bool:
    address = address.lower()
    return address in WHITELIST

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
    while True:
        try:
            name = generate_name()
            domain = random.choice(DOMAINS)
            address = f"{name}.{domain}".lower()

            # Skip instantly if not whitelisted (VERY IMPORTANT)
            if not is_whitelisted(address):
                continue

            # Prevent duplicate logs
            with lock:
                if address in seen_servers:
                    continue

            server = JavaServer.lookup(address, timeout=TIMEOUT)
            status = server.status()

            if not status:
                continue
            if status.players.max == 0:
                continue

            version = status.version.name if status.version else "unknown"

            # Final duplicate protection (thread-safe)
            with lock:
                if address in seen_servers:
                    continue
                seen_servers.add(address)

            print(f"[WHITELIST LOGGED] {address} | {status.players.online}/{status.players.max} | {version}")

            send_to_api(address, status.players.online, status.players.max, version)

        except Exception:
            continue

def main():
    for _ in range(THREADS):
        threading.Thread(target=scan, daemon=True).start()

    while True:
        time.sleep(10)

if __name__ == "__main__":
    main()
