#!/usr/bin/env python3
"""Stop the build if version numbers disagree, a JSON file doesn't parse, or an
item points at a texture that isn't there."""
import glob, json, os, re, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
bad, data = [], {}
for path in glob.glob("behavior_pack/**/*.json", recursive=True) + glob.glob("resource_pack/**/*.json", recursive=True):
    try:
        data[path] = json.load(open(path))
    except ValueError as e:
        bad.append(f"{path}: {e}")
if bad:
    sys.exit("\n".join(bad))

bp, rp = data["behavior_pack/manifest.json"], data["resource_pack/manifest.json"]
v = bp["header"]["version"]
s = ".".join(map(str, v))
js = re.search(r'^export const VERSION = "(.*)";', open("behavior_pack/scripts/main.js").read(), re.M).group(1)
checks = {
    "resource pack version": rp["header"]["version"] == v,
    "module versions": all(m["version"] == v for m in bp["modules"] + rp["modules"]),
    "behavior pack name": bp["header"]["name"] == f"Boom Hammer {s}",
    "resource pack name": rp["header"]["name"] == f"Boom Hammer {s} (art)",
    "behavior -> resource dependency": {"uuid": rp["header"]["uuid"], "version": v} in bp["dependencies"],
    "resource -> behavior dependency": {"uuid": bp["header"]["uuid"], "version": v} in rp["dependencies"],
    "VERSION in main.js": js == s,
}
bad += [f"version {s} mismatch: {k}" for k, ok in checks.items() if not ok]
atlas = data["resource_pack/textures/item_texture.json"]["texture_data"]
for key, t in atlas.items():
    if not os.path.exists(f"resource_pack/{t['textures']}.png"):
        bad.append(f"item_texture.json: missing {t['textures']}.png")
for path, d in data.items():
    if "/items/" in path:
        icon = d["minecraft:item"]["components"]["minecraft:icon"]["textures"]["default"]
        if icon not in atlas:
            bad.append(f"{path}: icon {icon} isn't in item_texture.json")
if bad:
    sys.exit("\n".join(bad))
print(f"Boom Hammer {s}: versions agree, {len(data)} JSON files parse, art is all there")
