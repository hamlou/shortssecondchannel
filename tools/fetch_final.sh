#!/usr/bin/env bash
# PC side: download the encrypted Short built by the 'short' workflow and decrypt it into shorts/<nn>/build/.
# bash tools/fetch_final.sh <nn> [run-id]
set -e
N=$1; RUN=$2
ROOT=$(cd "$(dirname "$0")/.." && pwd)
GH="$LOCALAPPDATA/ghcli/bin/gh.exe"
[ -n "$RUN" ] || RUN=$("$GH" run list -R hamlou/shortssecondchannel -w short.yml -L 20 --json databaseId,displayTitle,conclusion --jq "[.[] | select(.displayTitle==\"short S$N\" and .conclusion==\"success\")][0].databaseId")
OUT="$ROOT/shorts/$N/build"
mkdir -p "$OUT"
rm -rf "$OUT/ci"
"$GH" run download "$RUN" -R hamlou/shortssecondchannel -n "short-$N" -D "$OUT/ci"
for f in final.mp4 final_sheet.jpg; do
  openssl enc -d -aes-256-cbc -pbkdf2 -pass file:"$ROOT/tools/.srckey" -in "$OUT/ci/$f.enc" -out "$OUT/$f"
done
cp "$OUT/ci/durations.json" "$ROOT/shorts/$N/durations.json"
cat "$OUT/ci/gate.txt" | tail -1; cat "$OUT/ci/pace.txt"
echo "-> $OUT/final.mp4"
