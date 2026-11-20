# Boom Hammer

A Minecraft Bedrock add-on designed by kids: a hammer that blasts a crater, a staff that shoots fire, a bow that calls lightning, and three new monsters.

## Install

On the device that **hosts** the world (iPad, phone, or Windows):

1. Download **[BoomHammer.mcaddon](https://github.com/redswoop/boom-hammer/releases/latest/download/BoomHammer.mcaddon)** and open it. Minecraft imports it.
2. Edit the world → **Behavior Packs** → **Available** → **Boom Hammer x.y.z** → **Activate** (its art pack, **Boom Hammer x.y.z (art)**, comes along automatically; if not, activate it under **Resource Packs**).
3. Play. Anyone who joins downloads the pack automatically.

Chat says which version is running when you join.

## What's in it

Everyone gets a Boom Hammer, a Fire Staff, a Lightning Bow, a Lightning House and an Insomnia Creeper Egg the first time they join. On touch screens, tap a *block* (the ground), not the sky.

- **Boom Hammer**: smash the ground and BOOM, a crater much bigger than TNT. The smasher isn't hurt. Recipe: like a stone pickaxe, with TNT in place of the stone.
- **Fire Staff**: shoots a fireball that explodes and sets fire. Recipe: a flint and steel on top of two sticks.
- **Lightning Bow**: shoots an arrow, and lightning strikes where it lands. Each shot uses one Lightning Arrow (free in creative).
- **Lightning Zombie**: a zombie hit by lightning turns yellow with red eyes and gets fast. It drops 8 **Lightning Shards**.
- **Lightning Arrow**: a normal arrow surrounded by 8 Lightning Shards makes 8.
- **Lightning House**: tap the ground to build a big yellow house. While somebody is inside, a Lightning Zombie spawns every minute. Smash the house and it stops.
- **Fire Skeleton**: a skeleton hit by the Fire Staff turns orange. Its arrows are on fire.
- **Insomnia Creeper**: a black creeper that comes at night if you skipped a night's sleep. When it explodes, everything around turns black and it goes dark. The egg makes one right away.

## Good to know

- The yellow zombie, orange skeleton and black creeper are the game's own mobs with a new skin, chosen by their name. A zombie you name "Lightning Zombie" with a name tag turns yellow too.
- The Lightning Bow and the Lightning House have no crafting recipe yet.
- Made for Minecraft Bedrock 1.26.20 or newer.

## Building it

`./build.sh` checks the pack and writes `BoomHammer.mcaddon`. `python3 tools/make_art.py` repaints the item icons, and `python3 tools/make_zombie.py` remakes the monster skins from the game's own files (both need Pillow).
