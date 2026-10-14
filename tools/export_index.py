# Xuất audio-index.json: chỉ câu DÙNG ĐƯỢC (cắt đạt, không bị CONTENT_FLAGS) → {file, texts (chuỗi app đã chuẩn hóa = khóa tra), apps}
import json,os
last={}
for l in open('state/ledger.jsonl'):
    e=json.loads(l)
    if e.get('event')=='result': last[e['n']]=e
fl={f['n'] for f in json.load(open('state/content_flags.json'))}
out=[]
for u in json.load(open('state/queue.json')):
    e=last.get(u['n'])
    if u.get('skip') or not e or e['status']!='ok' or not os.path.exists(e['file']) or u['n'] in fl: continue
    out.append({'file':os.path.basename(e['file']),'texts':sorted(set(u['texts'])),'apps':sorted({x['app'] for x in u['uses']})})
json.dump({'voice':'Lea Brandt – Explainer (pMrwpTuGOma7Nubxs5jo)','model':'eleven_multilingual_v2','entries':out},open('audio-index.json','w'),ensure_ascii=False)
print(len(out),'entries',sum(len(x['texts']) for x in out),'texts')
