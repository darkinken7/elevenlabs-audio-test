#!/bin/bash
# plan.sh <id> [maxchars]: lập batch, lưu plan.json, in thông tin + prompt
set -e; cd "$(dirname "$0")/.."
python3 tools/plan_batch.py ${2:-2800} "$1" > state/batches/$1.plan.json
python3 -c "import json;d=json.load(open('state/batches/$1.plan.json'));print(d['group'],len(d['ns']),'units',d['chars'],'chars, remaining_in_group',d.get('remaining_in_group'))"
python3 tools/rec.py sum | tail -1
echo ----; cat state/batches/$1.prompt.txt
