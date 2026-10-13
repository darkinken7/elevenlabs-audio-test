#!/usr/bin/env python3
# audio-map.json: câu (đúng chuỗi speakDe chuẩn hóa) → file MP3; chỉ câu status ok. Mọi biến thể chữ cùng key đều trỏ cùng file.
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q = json.load(open(R + '/state/queue.json')); ok = {}
for l in open(R + '/state/ledger.jsonl'):
    r = json.loads(l)
    if r.get('event') == 'result' and r['status'] == 'ok': ok[r['key']] = r
files = {}
for e in Q:
    if e['key'] in ok:
        for t in [e['speak']] + e['texts']: files[t] = e['key'] + '.mp3'
json.dump({'base': 'mp3/', 'voice': 'Lea Brandt – Explainer (pMrwpTuGOma7Nubxs5jo)', 'model': 'eleven_multilingual_v2', 'files': files}, open(R + '/audio-map.json', 'w'), ensure_ascii=False, indent=0)
print(len(ok), 'file,', len(files), 'chuỗi tra')
