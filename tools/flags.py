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
    # 2026-10-14: mảnh âm tiết/hậu tố không phải từ (đáp án kiểu „ä“, „ie“, „-en“, „- n“): giọng đọc không có cách đọc đúng duy nhất và bước cắt (so chữ Scribe) dễ lệch → không tạo, giữ giọng trình duyệt
    if re.fullmatch(r'\s*[-–]\s*[a-zäöüß]{1,3}\.?\s*|\s*(?:[aeiouäöü]|ie|ei|au|äu|eu)\.?\s*',t,re.I): return '4_manh_am_tiet_khong_phai_tu'
    return None
OVF='state/flag_overrides.json'
OV={int(k) for k,v in json.load(open(OVF))['items'].items() if v.get('enable')} if os.path.exists(OVF) else set()   # file đã kiểm nhận dạng thật từng cái → bật lại
flags=[];usable={};D=[]
for u in Q:
    if u['n'] not in ok: continue
    c=None if u['n'] in OV else cat(u['tts'])
    if c: flags.append({'cat':c,'n':u['n'],'tts':u['tts'],'file':ok[u['n']]['file'],'uses':u['uses']})
    else:
        usable[u['tts']]=os.path.basename(ok[u['n']]['file'])
        if len(u['tts'].split())==1: D.append(u['tts'])
json.dump(flags,open('state/content_flags.json','w'),ensure_ascii=False,indent=1)
pend=[{'n':u['n'],'cat':cat(u['tts']),'tts':u['tts'],'uses':u['uses']} for u in Q if u['n'] not in ok and cat(u['tts'])]
json.dump(pend,open('state/pending_flags.json','w'),ensure_ascii=False,indent=1)   # chưa tạo + thuộc diện đánh dấu: plan_batch.py bỏ qua, inventory.mjs xếp riêng
m=json.load(open('audio-map.json')); m['files']=usable
json.dump(m,open('audio-map.usable.json','w'),ensure_ascii=False,indent=0)
C=collections.Counter(f['cat'] for f in flags)
L=['# Nội dung nguồn cần xem lại (2026-10-14)','','Các câu dưới đây CÓ file MP3 nhưng KHÔNG đưa vào audio-map.usable.json → app dùng speechSynthesis. Chưa sửa nội dung học.','',
 '1_loi_noi_dung = lỗi nội dung (câu sai ngữ pháp trong nguồn) · 2_de_bai_chua_hoan_chinh = đề bài/câu mẫu chưa hoàn chỉnh (có „…“ hoặc chỗ trống) · 4_manh_am_tiet_khong_phai_tu = đáp án chỉ là âm tiết/hậu tố (ä, ie, -en, - n) · 3_kho_doc_bang_TTS = cách viết khó đọc bằng TTS (+, /, ≠, jdm, etw. … — TTS đọc nguyên ký hiệu, cần nghe lại hoặc viết bản đọc riêng)','',
 *[f'- {k}: {v}' for k,v in sorted(C.items())],'']
for c in sorted(C):
    L+=['## '+c,'']
    for f in flags:
        if f['cat']==c: L.append(f"- „{f['tts']}“ — "+', '.join(sorted({f"{x['app']}:{x['ref']}" for x in f['uses']}))[:200])
    L.append('')
L+=['## Thông tin (vẫn dùng): câu một từ — đáp án dạng Partizip/từ đơn, hợp lệ','',f'{len(D)} câu, ví dụ: '+', '.join(D[:15]),'']
open('CONTENT_FLAGS.md','w').write('\n'.join(L))
print(C, 'usable', len(usable), 'ok', len(ok), 'unique files', len({e['file'] for e in ok.values()}))
