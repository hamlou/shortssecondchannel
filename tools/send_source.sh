#!/usr/bin/env bash
# PC side, network only: download one source video, encrypt it, upload it as release asset src-<nn>, delete the local copy.
# bash tools/send_source.sh <nn> <youtube-id>
set -e
N=$1; ID=$2
ROOT=$(cd "$(dirname "$0")/.." && pwd)
GH="$LOCALAPPDATA/ghcli/bin/gh.exe"
FF="C:\Users\hp\Desktop\100\tools\ffmpeg\ffmpeg.exe"
cd "$ROOT"
TMP=".tmp_src_$N"
rm -rf "$TMP"; mkdir -p "$TMP"
for i in 1 2 3; do
  py -m yt_dlp --no-warnings -f "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[ext=mp4]/b" --merge-output-format mp4 --ffmpeg-location "$FF" -o "$TMP/source.%(ext)s" -- "$ID" >/dev/null 2>&1 && [ -f "$TMP/source.mp4" ] && break
  sleep 60
done
[ -f "$TMP/source.mp4" ] || { echo "download failed $N"; exit 1; }
openssl enc -aes-256-cbc -pbkdf2 -pass file:tools/.srckey -in "$TMP/source.mp4" -out "$TMP/source.mp4.enc"
rm "$TMP/source.mp4"
"$GH" release view "src-$N" -R hamlou/shortssecondchannel >/dev/null 2>&1 || \
  "$GH" release create "src-$N" -R hamlou/shortssecondchannel --prerelease --title "src-$N (encrypted)" --notes "Encrypted working file for the build pipeline." >/dev/null
"$GH" release upload "src-$N" "$TMP/source.mp4.enc" -R hamlou/shortssecondchannel --clobber
rm -rf "$TMP"
echo "sent $N"
