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
    # Original
    "minefort.com","aternos.me","server.pro","mc.gg",
    "playit.gg","minehut.gg","mcserv.me","duckdns.org",

    # Free / popular MC hosts
    "aternos.org","minehut.com","ploudos.com","falixsrv.me",
    "freemc.host","exaroton.com","omgserv.com","scalacube.pro",
    "skynode.pro","pebble.host","sparked.host","revivenode.com",
    "bloom.host","titannodes.com","envyhost.net","winternode.com",

    # Paid / large hosting providers (commonly used)
    "apexmc.co","shockbyte.com","bisecthosting.com","ggservers.com",
    "mcprohosting.com","meloncube.net","nodecraft.games",
    "cubedhost.com","hosthorde.com","logicservers.com",
    "serverminer.com","zap-hosting.com","zaphosting.com",
    "g-portal.com","nitrado.net","pingperfect.com",

    # Panel / subdomain ecosystems
    "my.pebble.host","panel.ggservers.com","panel.bisecthosting.com",
    "panel.apexmc.co","panel.falixsrv.me","node.minehut.gg",

    # Dynamic DNS (very common for self-hosted servers)
    "no-ip.org","noip.me","ddns.net","duckdns.org","hopto.org",
    "servegame.com","serveftp.com","servehttp.com","myftp.biz",
    "dynu.net","dyndns.org","dynv6.net","afraid.org",
    "freedns.afraid.org","redirectme.net","dnsalias.net",
    "mooo.com","sytes.net","homeip.net",

    # Tunneling / NAT traversal (self-hosted MC)
    "playit.cloud","ngrok.io","ngrok-free.app","trycloudflare.com",
    "loca.lt","localto.net","tunnelto.dev","pagekite.me","bore.pub",

    # Generic MC-related / vanity domains
    "mcserver.ws","minecraft.host","minecraft.best",
    "minecraftserver.io","joinmc.link","joinserver.xyz",
    "playmc.net","playmc.org","playmc.xyz","playserver.net",
    "playserver.org","mcnode.net","multiplayer.gg"
]

COMMON_NAMES = [
    # Original
    "mc","play","survival","pvp","smp","lobby",
    "skyblock","bedwars","lifesteal","network",

    # Core gamemodes
    "factions","prison","creative","hardcore","anarchy",
    "kitpvp","uhc","duels","minigames","arcade",
    "practice","events","vanilla","modded","economy",

    # Popular modern modes
    "oneblock","earth","towny","gens","gen","opprison",
    "opskyblock","boxpvp","crystalpvp","roleplay",
    "rpg","pixelmon","cobblemon","forge","fabric",

    # Common server prefixes
    "hub","main","proxy","bungee","velocity","core",
    "global","central","official","public","premium",

    # Branding-style names frequently used
    "craft","crafting","block","blocks","cube","cubed",
    "mine","mines","mining","miners","realm","realms",
    "world","worlds","verse","land","lands","kingdom",
    "kingdoms","empire","empires","legacy","origins",

    # Competitive / PvP naming trends
    "arena","arenas","fight","combat","clan","clans",
    "wars","battle","battles","siege","ranked","elo",

    # Aesthetic / modern network styles
    "nova","zenith","cosmic","lunar","stellar",
    "nebula","eclipse","orbit","quantum","vertex",
    "apex","pulse","fusion","echo","vortex",

    # Misc commonly seen server naming patterns
    "test","dev","beta","alpha","season","seasonal",
    "new","classic","reborn","remastered","plus",
    "x","gg","live","online","host","server"
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
