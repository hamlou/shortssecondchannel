#!/usr/bin/env bash
# Auto checker: prints one line whenever something finishes — a source reaching GitHub, or any workflow run ending.
# bash tools/watch.sh   (runs until killed; polls every 60 s)
GH="$LOCALAPPDATA/ghcli/bin/gh.exe"
R=hamlou/shortssecondchannel
seen_src=$("$GH" release list -R $R -L 200 --json tagName --jq '.[].tagName' 2>/dev/null | sort)
seen_run=$("$GH" run list -R $R -L 30 --json databaseId,status --jq '.[]|select(.status=="completed")|.databaseId' 2>/dev/null | sort)
echo "watching: $(echo "$seen_src" | grep -c src-) sources on GitHub"
while true; do
  sleep 60
  src=$("$GH" release list -R $R -L 200 --json tagName --jq '.[].tagName' 2>/dev/null | sort) || continue
  for t in $(comm -13 <(echo "$seen_src") <(echo "$src")); do echo "SOURCE READY $t"; done
  [ -n "$src" ] && seen_src=$src
  runs=$("$GH" run list -R $R -L 30 --json databaseId,status,conclusion,displayTitle --jq '.[]|select(.status=="completed")|"\(.databaseId)\t\(.conclusion)\t\(.displayTitle)"' 2>/dev/null) || continue
  while IFS=$'\t' read -r id c t; do
    [ -z "$id" ] && continue
    echo "$seen_run" | grep -qx "$id" && continue
    echo "RUN $(echo $c | tr a-z A-Z): $t ($id)"
    seen_run=$(printf '%s\n%s' "$seen_run" "$id")
  done <<< "$runs"
done
