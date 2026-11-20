#!/usr/bin/env python3
"""Turn La Forge on in the existing "Boom" world without remaking it (keeps the craters).
Only run with the game closed."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORLD = os.path.expanduser("~/Library/Application Support/mcpelauncher/games/com.mojang/minecraftWorlds/boomhammer_lab")
if subprocess.run(["pgrep", "-f", "mcpelauncher-[c]lient"], capture_output=True).returncode == 0:
    sys.exit("The game is running; not touching worlds.")
for kind in ("behavior", "resource"):
    h = json.load(open(os.path.join(os.path.dirname(ROOT), "la-forge", f"{kind}_pack", "manifest.json")))["header"]
    path = os.path.join(WORLD, f"world_{kind}_packs.json")
    packs = [p for p in json.load(open(path)) if p["pack_id"] != h["uuid"]]
    packs.append({"pack_id": h["uuid"], "version": h["version"]})
    json.dump(packs, open(path, "w"))
    print(kind, packs)
