#!/usr/bin/env bash
# Small download (~100 KB) to check a build: 1.2 fps contact sheet + gate/pace/plan -> shorts/<nn>/build/review.jpg
# bash tools/fetch_review.sh <nn> [run-id]
set -e
N=$1; RUN=$2
ROOT=$(cd "$(dirname "$0")/.." && pwd)
GH="$LOCALAPPDATA/ghcli/bin/gh.exe"
[ -n "$RUN" ] || RUN=$("$GH" run list -R hamlou/shortssecondchannel -w short.yml -L 30 --json databaseId,displayTitle,conclusion --jq "[.[] | select(.displayTitle==\"short S$N\" and .conclusion==\"success\")][0].databaseId")
cd "$ROOT"; OUT="shorts/$N/build"; mkdir -p "$OUT"; rm -rf "$OUT/rv"
"$GH" run download "$RUN" -R hamlou/shortssecondchannel -n "review-$N" -D "$OUT/rv"
openssl enc -d -aes-256-cbc -pbkdf2 -pass file:tools/.srckey -in "$OUT/rv/review.jpg.enc" -out "$OUT/review.jpg"
cp "$OUT/rv/durations.json" "shorts/$N/durations.json"; tail -1 "$OUT/rv/gate.txt"
echo "-> $OUT/review.jpg"
