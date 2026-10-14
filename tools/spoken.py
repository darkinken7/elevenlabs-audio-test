#!/usr/bin/env python3
"""Lời đọc chuẩn hóa (spoken form) cho các câu bị gắn cờ — KHÔNG đổi chữ hiển thị trong app.
Ghi state/spoken_forms.json: mỗi mục có `display` (nguyên văn trong app/hàng đợi) và `spoken` (chuỗi sẽ gửi TTS ở đợt sau).
Quy tắc (quyết định của James, 2026-10-14):
  - Không đọc ký hiệu: không „Schrägstrich“, không „Pfeil“.  „+“ trong công thức → „plus“.
  - jdn./jdm./jds./etw. → jemanden / jemandem / jemandes / etwas.  Akk./A. → Akkusativ · Dat./D. → Dativ · G. → Genitiv · N. → Nominativ.
  - „A/B“ (lựa chọn) → „A, oder, B“ (dấu phẩy = nghỉ nhẹ). Giới từ chung bổ ngữ → đọc trọn từng vế: „vor etwas, oder, über etwas“ (không tách giới từ khỏi bổ ngữ).
  - „/“ không phải lựa chọn (liệt kê dạng chia động từ…) → KHÔNG ép „oder“, ghi tay trong MANUAL.
  - Chỉ dẫn trong ngoặc cho việc dựng audio KHÔNG bao giờ được đọc: spoken chỉ chứa chữ thật (dấu nghỉ nếu dùng sẽ là thẻ <break>, thêm khi gửi, ghi ở `pauses`).
status: auto = luật tự động · manual = ghi tay · hold = chưa có lời đọc đủ an toàn (không tạo, cần quyết định) · skip = có tiếng Việt xen (mixed)
review: true = cần James/QC nghe trước khi tạo hàng loạt.
usage: python3 tools/spoken.py   (đọc state/content_flags.json + state/pending_flags.json)"""
import json, re, sys, collections

PREP = {'auf','über','gegen','gegenüber','zu','mit','vor','bei','von','in','an','durch','für','um','zwischen','aus','nach','wegen','im','am','unter'}
JD = {'jdn':'jemanden','jdm':'jemandem','jds':'jemandes','etw':'etwas'}
CASE = {'Akk':'Akkusativ','A':'Akkusativ','Dat':'Dativ','D':'Dativ','G':'Genitiv','N':'Nominativ','Gen':'Genitiv'}

# ghi tay: n → (spoken, status, review, ghi chú)
MANUAL = {
  3926: ('Erbe ist nicht gleich Tradition.', 'hold', True, '„≠“ → „ist nicht gleich“: thêm từ không có trong nguồn, cần James duyệt'),
  3971: (None, 'hold', True, 'nguồn: „empfinden für/gegenüber jdn“ — gegenüber đi với Dativ (jdm); sửa nguồn trước khi tạo'),
  4714: ('Nominativ Singular plus Akkusativ Singular, Neutrum und Femininum.', 'hold', True, 'viết tắt Nom Sg/Akk Sg N & F: bản đọc đầy đủ là phỏng đoán, cần James duyệt'),
  4704: ('der Herr. den, dem, des Herrn.', 'manual', True, 'liệt kê dạng biến cách, không phải lựa chọn → không „oder“'),
  5044: ('dass-Satz. zu-Infinitiv. ob-Satz, oder, W-Satz.', 'manual', True, '„ob-/W-Satz“ là hai loại câu, ghi tay'),
  5083: (None, 'hold', True, 'tiền tố „in-/il-/im-/ir-“ là mảnh âm tiết, không có cách đọc đúng duy nhất (cùng nhóm 4)'),
  6034: ('bin, bist, ist. war. gewesen.', 'manual', True, 'liệt kê chia động từ, không phải lựa chọn → không „oder“'),
  6035: ('habe, hast, hat. hatte. gehabt.', 'manual', True, 'liệt kê chia động từ, không phải lựa chọn → không „oder“'),
  773:  ('denn. weil, oder, da. wegen plus Genitiv. nämlich.', 'manual', True, 'giữ ranh giới câu sau „G.“'),
  1171: ('Verb Position zwei, denn plus Subjekt plus Verb.', 'manual', True, '„S + V“ → Subjekt/Verb: chữ cái đơn lẻ sẽ bị đọc tên chữ'),
  3956: (None, 'hold', True, 'nguồn: „gegen/gegenüber jdm“ — gegen đi với Akkusativ (jdn); sửa nguồn trước khi tạo'),
  926:  (None, 'hold', True, '„+ -s-“ là mảnh âm tiết (Fugenelement), không có cách đọc đúng duy nhất'),
  927:  (None, 'hold', True, '„+ -er-“ là mảnh âm tiết (Fugenelement), không có cách đọc đúng duy nhất'),
  667:  (None, 'hold', True, '„Infinitivstamm + e“: chữ „e“ đơn lẻ, TTS có thể đọc tên chữ cái hoặc âm — cần nghe'),
  4007: ('wütend auf jemanden oder etwas, oder, über jemanden oder etwas.', 'manual', True, 'hai tầng lựa chọn (giới từ × jdn/etw.): „oder“ trong cụm giữ liền, „, oder,“ giữa hai vế'),
  4034: ('um jemanden, oder, um etwas weinen.', 'manual', True, 'lặp giới từ „um“ để không tách giới từ khỏi bổ ngữ'),
  3133: ('Ja, oder, Genau, in Köln.', 'manual', True, 'hai câu trả lời thay thế; dấu — và ngoặc bỏ'),
  3935: ('jemandem treu sein, oder, jemandem treu bleiben.', 'manual', True, 'đọc trọn từng vế'),
  3949: ('jemandem untreu werden, oder, jemandem untreu sein.', 'manual', True, 'đọc trọn từng vế'),
  3958: ('jemanden nicht leiden können, oder, jemanden nicht mögen.', 'manual', True, 'đọc trọn từng vế'),
  3966: ('auf dem Kriegsfuß mit jemandem stehen, oder, auf dem Kriegsfuß mit jemandem leben.', 'manual', True, 'đọc trọn từng vế'),
  3991: ('jemandem eine Heidenangst einjagen, oder, jemandem eine Heidenangst machen.', 'manual', True, 'đọc trọn từng vế'),
  4070: ('auf Wolke sieben schweben, oder, auf Wolke sieben sein.', 'manual', True, 'đọc trọn từng vế'),
  4165: ('eine Tradition fortsetzen, oder, eine Tradition pflegen.', 'manual', True, 'đọc trọn từng vế'),
  5176: ('an dem plus Zeitnomen, oder, in dem plus Zeitnomen.', 'manual', True, 'giới từ + bổ ngữ giữ liền'),
  5879: ('der Reisende, oder, die Reisende.', 'manual', True, 'giữ trọn cụm danh từ'),
  5880: ('der Angestellte, oder, die Angestellte.', 'manual', True, 'giữ trọn cụm danh từ'),
}
# đáp án hoặc đề có tiếng Việt xen → không thuộc phạm vi giọng Đức
MIXED = {5144, 5339}

def tidy(s):
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\s+([.,;:!?])', r'\1', s)
    return s

def expand_prep_alts(s):
    """„vor/über etw.“ → „vor etwas, oder, über etwas“ (giới từ + bổ ngữ liền nhau). Chạy trước khi thay jdn/etw."""
    def rep(m):
        preps = m.group(1).split('/'); comp = m.group(2)
        return ', oder, '.join(f'{p} {comp}' for p in preps)
    pat = r'\b((?:' + '|'.join(sorted(PREP, key=len, reverse=True)) + r')(?:/(?:' + '|'.join(sorted(PREP, key=len, reverse=True)) + r'))+) (jdn|jdm|jds|etw\.?|[A-ZÄÖÜ][\wäöüß]+)'
    return re.sub(pat, rep, s)

def to_spoken(t):
    s = t
    s = s.replace('„', '').replace('“', '').replace('"', '')
    s = re.sub(r'\s*—\s*', ', ', s)
    s = expand_prep_alts(s)
    s = re.sub(r'\bjd([mns])\b', lambda m: JD['jd' + m.group(1)], s)
    s = re.sub(r'\betw\.$', 'etwas.', s)
    s = re.sub(r'\betw\.(?=\s|[,;:])', 'etwas', s)
    s = re.sub(r'\bPII\b', 'Partizip zwei', s)
    s = re.sub(r'\bPartizip II\b', 'Partizip zwei', s)
    s = re.sub(r'\bKonjunktiv II\b', 'Konjunktiv zwei', s)
    s = re.sub(r'\bKII\b', 'Konjunktiv zwei', s)
    s = re.sub(r'\bPos\.\s?2\b', 'Position zwei', s)
    s = re.sub(r'\bNS\b', 'Nebensatz', s)
    s = re.sub(r'\bAdj\.(?=\s+[A-ZÄÖÜ]|$)', 'Adjektiv.', s)
    s = re.sub(r'\bAdj\b\.?', 'Adjektiv', s)
    s = re.sub(r'\bzu-Inf\b\.?', 'zu-Infinitiv.', s)
    s = re.sub(r'\bInf-Nomen\b', 'Infinitiv-Nomen', s)
    s = re.sub(r'\b(Akk|Dat|Gen|A|D|G|N)\.(?=$|\s*\S+(?:\s+\S+)?\s*\+)', lambda m: CASE[m.group(1)] + '.', s)
    s = re.sub(r'\b(Akk|Dat|Gen|A|D|G|N)\.(?=\s|[,;:])', lambda m: CASE[m.group(1)], s)
    s = re.sub(r'(?<=\w)\s*\+\s*(?=\w)', ' plus ', s)          # „bei+D“ / „wird + PII“
    s = re.sub(r'\s*\+\s*', ' plus ', s)
    s = s.replace(' & ', ' und ')
    # còn lại: „A/B“ = lựa chọn từ đơn → „A, oder, B“
    s = re.sub(r'(?<=[\wäöüßÄÖÜ])/(?=[\wäöüßÄÖÜ])', ', oder, ', s)
    s = re.sub(r'(?<=,) (?=,)', '', s)
    s = re.sub(r'([.!?]) ?\.$', r'\1', s)                       # „…?.“ do cắt câu
    s = re.sub(r'\.\.+', '.', s)
    s = re.sub(r'(\w)\.\.', r'\1.', s)
    return tidy(s)

def residual(sp):
    """ký hiệu còn sót sau khi chuẩn hóa (nếu có → không được đưa vào TTS)"""
    return re.findall(r'[+/≠=→&]|\bjd[mns]?\b|\betw\.|\bAkk\.|\bDat\.|\b[ADGN]\.|\bPII\b|…|\.\.\.', sp)

def main():
    C = json.load(open('state/content_flags.json')); P = json.load(open('state/pending_flags.json'))
    out = []; st = collections.Counter()
    for src, lst in (('co_file', C), ('chua_tao', P)):
        for x in lst:
            n, cat, t = x['n'], x['cat'], x['tts']
            e = {'n': n, 'cat': cat, 'display': t, 'has_file': src == 'co_file', 'file': x.get('file'),
                 'uses': sorted({f"{u['app']}:{u['ref']}" for u in x['uses']})[:6]}
            if cat == '3_kho_doc_bang_TTS':
                if n in MIXED:
                    e.update(spoken=None, status='skip', review=False, note='có tiếng Việt xen trong chuỗi (mixed) — không tạo bằng giọng Đức')
                elif n in MANUAL:
                    sp, s, rv, note = MANUAL[n]; e.update(spoken=sp, status=s, review=rv, note=note)
                else:
                    sp = to_spoken(t); r = residual(sp)
                    e.update(spoken=sp, status='auto' if not r else 'hold', review='/' in t, note=('còn ký hiệu: ' + ' '.join(r)) if r else '',
                             slash=('/' in t))
            elif cat == '2_de_bai_chua_hoan_chinh':
                e.update(spoken=None, status='hold', review=True, note='đề chưa hoàn chỉnh („…“ bị đọc „äh“ khi kiểm bằng nhận dạng thật). Đề xuất: thay „…“ bằng thẻ <break time="0.7s" /> khi dựng audio — chưa tạo, cần James quyết',
                         proposal=re.sub(r'\s*…\s*', ' <break time="0.7s" /> ', t).strip())
            elif cat == '4_manh_am_tiet_khong_phai_tu':
                e.update(spoken=None, status='hold', review=True, note='mảnh âm tiết/hậu tố — không có cách đọc đúng duy nhất')
            else:
                e.update(spoken=None, status='hold', review=True, note='lỗi nội dung nguồn — sửa nguồn trước')
            st[(cat[:1], e['status'], 'co_file' if e['has_file'] else 'chua_tao')] += 1
            out.append(e)
    import os
    if os.path.exists('state/flag_overrides.json'):
        ov = json.load(open('state/flag_overrides.json'))['items']
        for e in out:
            v = ov.get(str(e['n']))
            if v: e['asr'] = {'enable': v['enable'], 'heard': v['heard'], 'reason': v['reason']}
    json.dump({'_doc': __doc__.split('\n')[0], 'items': out}, open('state/spoken_forms.json', 'w'), ensure_ascii=False, indent=1)
    for k, v in sorted(st.items()): print(k, v)
    print('tổng', len(out))
if __name__ == '__main__': main()
