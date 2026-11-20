"""Make the Lightning Zombie's look: a yellow zombie with red eyes.

    python3 tools/make_zombie.py

It reads the game's own zombie files (skin and client entity) from the Mac
install, recolours the skin, and writes a copy of the client entity that picks
the yellow skin when the zombie is named "Lightning Zombie". Needs Pillow.
Run it again after a game update that changes the zombie.
"""
import io, json, os, struct, glob
from PIL import Image

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RP = os.path.join(HERE, "resource_pack")
VERSIONS = os.path.expanduser("~/Library/Application Support/mcpelauncher/versions")
NAMES = ["Lightning Zombie", "§eLightning Zombie"]  # the second is what 0.1.9 used
CONTROLLER = "controller.render.boomhammer_zombie"


def vkey(path):
    """Sort key for a vanilla pack folder: 'vanilla' first, then by version."""
    name = path.split("/resource_packs/")[1].split("/")[0]
    tail = name.partition("_")[2]
    return tuple(int(n) for n in tail.split(".")) if tail.replace(".", "").isdigit() else (0,)


def entries(path):
    b = open(path, "rb").read()
    (n,) = struct.unpack_from("<I", b, 8)
    base = 16 + n * 256
    for i in range(n):
        e = 16 + i * 256
        name = b[e + 1 : e + 1 + b[e]].decode()
        off, size = struct.unpack_from("<II", b, e + 248)
        yield name, b[base + off : base + off + size]


def newest(game, archive, wanted):
    """The newest vanilla pack's copy of a file."""
    found = None
    for path in sorted(glob.glob(f"{game}/assets/assets/resource_packs/vanilla*/__brarchive/{archive}"), key=vkey):
        for name, data in entries(path):
            if name == wanted:
                found = data
    if found is None:
        raise SystemExit(f"{wanted} not found in {archive}")
    return found


def recolour(data):
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if not a:
                continue
            if (r, g, b) == (0x1A, 0x1A, 0x1A):  # eyes
                px[x, y] = (230, 20, 20, a)
            elif g > r and g > b:  # green skin
                px[x, y] = (min(255, int(g * 2.1)), min(255, int(g * 1.75)), int(g * 0.35), a)
    return im


def main():
    games = [p for p in glob.glob(f"{VERSIONS}/*") if os.path.basename(p).replace(".", "").isdigit()]
    game = sorted(games, key=lambda p: tuple(int(n) for n in os.path.basename(p).split(".")))[-1]
    tex = os.path.join(RP, "textures", "entity", "boomhammer")
    os.makedirs(tex, exist_ok=True)
    recolour(newest(game, "textures/entity/zombie.brarchive", "zombie.png")).save(os.path.join(tex, "lightning_zombie.png"))
    recolour(newest(game, "textures/entity/zombie.brarchive", "zombie_baby.png")).save(os.path.join(tex, "lightning_zombie_baby.png"))

    entity = json.loads(newest(game, "entity.brarchive", "zombie.entity.json"))
    desc = entity["minecraft:client_entity"]["description"]
    assert set(desc["textures"]) == {"default", "baby"}, desc["textures"]
    desc["textures"]["lightning"] = "textures/entity/boomhammer/lightning_zombie"
    desc["textures"]["lightning_baby"] = "textures/entity/boomhammer/lightning_zombie_baby"
    desc["render_controllers"] = [CONTROLLER]
    os.makedirs(os.path.join(RP, "entity"), exist_ok=True)
    with open(os.path.join(RP, "entity", "zombie.entity.json"), "w") as f:
        json.dump(entity, f, indent=1)

    named = "query.is_name_any(" + ", ".join(f"'{n}'" for n in NAMES) + ")"
    controller = {
        "format_version": "1.8.0",
        "render_controllers": {
            CONTROLLER: {
                "geometry": "query.is_baby ? Geometry.baby : Geometry.default",
                "materials": [{"*": "Material.default"}],
                "textures": [
                    f"{named} ? (query.is_baby ? Texture.lightning_baby : Texture.lightning) : (query.is_baby ? Texture.baby : Texture.default)"
                ],
            }
        },
    }
    os.makedirs(os.path.join(RP, "render_controllers"), exist_ok=True)
    with open(os.path.join(RP, "render_controllers", "boomhammer_zombie.render_controllers.json"), "w") as f:
        json.dump(controller, f, indent=1, ensure_ascii=False)
    print("Lightning Zombie look written from", os.path.basename(game))
    skeleton(game, tex)


def fiery(data):
    """The skeleton's grey bones in fire colours: bright bone goes orange, shadow goes dark red."""
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a:
                light = max(r, g, b)
                px[x, y] = (min(255, int(light * 1.25) + 30), int(light * light / 255 * 0.62), int(light * 0.08), a)
    return im


def skeleton(game, tex):
    """The Fire Skeleton: the same trick as the zombie, on the vanilla skeleton, by the name "Fire Skeleton"."""
    fiery(newest(game, "textures/entity/skeleton.brarchive", "skeleton.png")).save(os.path.join(tex, "fire_skeleton.png"))
    entity = json.loads(newest(game, "entity.brarchive", "skeleton.entity.json"))
    desc = entity["minecraft:client_entity"]["description"]
    assert set(desc["textures"]) == {"default"}, desc["textures"]
    assert desc["render_controllers"] == ["controller.render.skeleton"], desc["render_controllers"]
    desc["textures"]["fire"] = "textures/entity/boomhammer/fire_skeleton"
    desc["render_controllers"] = ["controller.render.boomhammer_skeleton"]
    with open(os.path.join(RP, "entity", "skeleton.entity.json"), "w") as f:
        json.dump(entity, f, indent=1)
    controller = {
        "format_version": "1.8.0",
        "render_controllers": {
            "controller.render.boomhammer_skeleton": {
                "geometry": "Geometry.default",
                "materials": [{"*": "Material.default"}],
                "textures": ["query.is_name_any('Fire Skeleton') ? Texture.fire : Texture.default"],
            }
        },
    }
    with open(os.path.join(RP, "render_controllers", "boomhammer_skeleton.render_controllers.json"), "w") as f:
        json.dump(controller, f, indent=1)
    print("Fire Skeleton look written")
    creeper(game, tex)


def sleepless(data):
    """The creeper in near-black, with a pale face."""
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    px = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a:
                light = max(r, g, b)
                px[x, y] = (225, 225, 255, a) if light < 40 else (int(light * 0.16), int(light * 0.14), int(light * 0.2) + 6, a)
    return im


def creeper(game, tex):
    """The Insomnia Creeper: the same trick on the vanilla creeper, by the name "Insomnia Creeper"."""
    sleepless(newest(game, "textures/entity/creeper.brarchive", "creeper.png")).save(os.path.join(tex, "insomnia_creeper.png"))
    entity = json.loads(newest(game, "entity.brarchive", "creeper.entity.json"))
    desc = entity["minecraft:client_entity"]["description"]
    assert set(desc["textures"]) == {"default", "charged"}, desc["textures"]
    assert desc["render_controllers"][0] == "controller.render.creeper", desc["render_controllers"]
    desc["textures"]["insomnia"] = "textures/entity/boomhammer/insomnia_creeper"
    desc["render_controllers"][0] = "controller.render.boomhammer_creeper"
    with open(os.path.join(RP, "entity", "creeper.entity.json"), "w") as f:
        json.dump(entity, f, indent=1)
    vanilla = json.loads(newest(game, "render_controllers.brarchive", "creeper.render_controllers.json"))
    body = vanilla["render_controllers"]["controller.render.creeper"]
    assert body["textures"] == ["Texture.default"], body["textures"]
    body["textures"] = ["query.is_name_any('Insomnia Creeper') ? Texture.insomnia : Texture.default"]
    controller = {"format_version": vanilla["format_version"], "render_controllers": {"controller.render.boomhammer_creeper": body}}
    with open(os.path.join(RP, "render_controllers", "boomhammer_creeper.render_controllers.json"), "w") as f:
        json.dump(controller, f, indent=1)
    print("Insomnia Creeper look written")


main()
