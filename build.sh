#!/bin/sh
# Build BoomHammer.mcaddon (behavior pack + resource pack) after checking that every
# version number agrees and that every file the packs point at exists.
cd "$(dirname "$0")" || exit 1
python3 tools/check_pack.py || exit 1
rm -f BoomHammer.mcaddon && zip -qrX BoomHammer.mcaddon behavior_pack resource_pack -x '*.DS_Store' && echo "built BoomHammer.mcaddon"
