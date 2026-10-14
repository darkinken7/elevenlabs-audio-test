#!/bin/bash
# fin.sh <id> <master_url> <words_url>: tải, cắt/kiểm, map, commit, push, xác nhận remote
set -e; cd "$(dirname "$0")/.."
B=state/batches/$1; BR=claude/grammatik-audio-workflow-b5injh
[ -s $B.master.mp3 ] || curl -sSf --retry 3 -o $B.master.mp3 "$2"
curl -sSf --retry 3 -o $B.words.json "$3"
NS=$(python3 -c "import json;print(','.join(map(str,json.load(open('$B.plan.json'))['ns'])))")
python3 tools/cut.py "$1" $B.master.mp3 $B.words.json "$NS" | grep -v '^ok' || true
tail -1 state/ledger.jsonl | cut -c1-200
python3 tools/build_map.py
git add -A; git commit -qm "$1 cắt/kiểm

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Cg36AoxXTu5VnDkUM5CaKx"
for i in 2 4 8 16; do git push -q -u origin $BR 2>&1 && break; sleep $i; done
git fetch -q origin $BR; [ "$(git rev-parse HEAD)" = "$(git rev-parse origin/$BR)" ] && echo REMOTE_OK || echo REMOTE_MISMATCH
python3 tools/rec.py sum | tail -1
