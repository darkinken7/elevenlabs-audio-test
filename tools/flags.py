# Đánh dấu nội dung nguồn sai/chưa hoàn chỉnh; tạo audio-map.usable.json (chỉ câu đạt + không bị đánh dấu)
import json,re,os,collections
last={}
for l in open('state/ledger.jsonl'):
    e=json.loads(l)
    if e.get('event')=='result': last[e['n']]=e   # kết quả mới nhất quyết định
ok={n:e for n,e in last.items() if e['status']=='ok' and os.path.exists(e['file'])}
Q=json.load(open('state/queue.json'))
def cat(t):
    if re.search(r'\bIch ist\b|\bDu ist\b|\bEr bin\b',t): return '1_loi_noi_dung'
    if re.search(r'…|\.\.\.|_{2,}',t): return '2_de_bai_chua_hoan_chinh'
    if re.search(r'≠|=|\+|\bjd[mns]?\b|\betw\.|\bAkk\.|\bDat\.|\bD\.|/',t): return '3_kho_doc_bang_TTS'
    return None
flags=[];usable={};D=[]
for u in Q:
    if u['n'] not in ok: continue
    c=cat(u['tts'])
    if c: flags.append({'cat':c,'n':u['n'],'tts':u['tts'],'file':ok[u['n']]['file'],'uses':u['uses']})
    else:
        usable[u['tts']]=os.path.basename(ok[u['n']]['file'])
        if len(u['tts'].split())==1: D.append(u['tts'])
json.dump(flags,open('state/content_flags.json','w'),ensure_ascii=False,indent=1)
m=json.load(open('audio-map.json')); m['files']=usable
json.dump(m,open('audio-map.usable.json','w'),ensure_ascii=False,indent=0)
C=collections.Counter(f['cat'] for f in flags)
L=['# Nội dung nguồn cần xem lại (2026-10-14)','','Các câu dưới đây CÓ file MP3 nhưng KHÔNG đưa vào audio-map.usable.json → app dùng speechSynthesis. Chưa sửa nội dung học.','',
 '1_loi_noi_dung = lỗi nội dung (câu sai ngữ pháp trong nguồn) · 2_de_bai_chua_hoan_chinh = đề bài/câu mẫu chưa hoàn chỉnh (có „…“ hoặc chỗ trống) · 3_kho_doc_bang_TTS = cách viết khó đọc bằng TTS (+, /, ≠, jdm, etw. … — TTS đọc nguyên ký hiệu, cần nghe lại hoặc viết bản đọc riêng)','',
 *[f'- {k}: {v}' for k,v in sorted(C.items())],'']
for c in sorted(C):
    L+=['## '+c,'']
    for f in flags:
        if f['cat']==c: L.append(f"- „{f['tts']}“ — "+', '.join(sorted({f"{x['app']}:{x['ref']}" for x in f['uses']}))[:200])
    L.append('')
L+=['## Thông tin (vẫn dùng): câu một từ — đáp án dạng Partizip/từ đơn, hợp lệ','',f'{len(D)} câu, ví dụ: '+', '.join(D[:15]),'']
open('CONTENT_FLAGS.md','w').write('\n'.join(L))
print(C, 'usable', len(usable), 'ok', len(ok), 'unique files', len({e['file'] for e in ok.values()}))
