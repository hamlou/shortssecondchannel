#!/usr/bin/env bash
# PC side: download the encrypted Short built by the 'short' workflow and decrypt it into shorts/<nn>/build/.
# bash tools/fetch_final.sh <nn> [run-id]
set -e
N=$1; RUN=$2
ROOT=$(cd "$(dirname "$0")/.." && pwd)
GH="$LOCALAPPDATA/ghcli/bin/gh.exe"
[ -n "$RUN" ] || RUN=$("$GH" run list -R hamlou/shortssecondchannel -w short.yml -L 20 --json databaseId,displayTitle,conclusion --jq "[.[] | select(.displayTitle==\"short S$N\" and .conclusion==\"success\")][0].databaseId")
cd "$ROOT"
OUT="shorts/$N/build"
mkdir -p "$OUT"
rm -rf "$OUT/ci"
"$GH" run download "$RUN" -R hamlou/shortssecondchannel -n "short-$N" -D "$OUT/ci"
for f in final.mp4 final_sheet.jpg src_sheet.jpg; do
  if [ -f "$OUT/ci/$f.enc" ]; then openssl enc -d -aes-256-cbc -pbkdf2 -pass file:tools/.srckey -in "$OUT/ci/$f.enc" -out "$OUT/$f"; fi
done
cp "$OUT/ci/durations.json" "shorts/$N/durations.json"
cat "$OUT/ci/gate.txt" | tail -1; cat "$OUT/ci/pace.txt"
echo "-> $OUT/final.mp4"
