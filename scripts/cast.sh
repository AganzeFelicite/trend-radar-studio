#!/usr/bin/env bash
# V7.1 (D22): render the three character candidates for comparison. For each: voice test line (Kokoro, $0),
# character sheet PNG and a ~10 s lip-synced talking clip (Remotion in the renderer container), into assets/cast/<who>/.
# Then opens assets/cast/compare.html in Arc. Usage: scripts/cast.sh [patch|auntie|coach ...]  (default: all three)
set -euo pipefail
cd "$(dirname "$0")/.."
who_list=${*:-patch auntie coach}

(cd api && uv run python -m studio.voice cast)
render() {  # render <who> <remotion args...>
  docker compose run --rm -T \
    -v "$PWD/renderer/src:/app/src:ro" -v "$PWD/renderer/public/test:/app/public/test:ro" \
    -v "$PWD/renderer/out:/app/props:ro" -v "$PWD/assets/cast/$1:/app/out" renderer "${@:2}"
}
for who in $who_list; do
  mkdir -p "assets/cast/$who"
  echo "== $who: sheet"
  render "$who" npx remotion still src/index.ts CharacterSheet out/sheet.png --props="{\"who\":\"$who\"}" --bundle-cache=false
  echo "== $who: talking clip"
  render "$who" npx remotion render src/index.ts TalkingClip out/talk.mp4 --props="props/$who-props.json" --bundle-cache=false
done
ls -lh assets/cast/*/
open -a Arc "$PWD/assets/cast/compare.html"
