#!/bin/bash
# sub.sh <id> <flow> <tts_session> <gen> <credits>: ghi batch_submitted (ns từ plan.json)
set -e; cd "$(dirname "$0")/.."
NS=$(python3 -c "import json;print(','.join(map(str,json.load(open('state/batches/$1.plan.json'))['ns'])))")
python3 tools/rec.py bsubmit "$1" "$2" "$3" "$4" "$5" "$NS" | tail -1
