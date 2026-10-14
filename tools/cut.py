#!/usr/bin/env python3
# Cắt file gộp thành từng câu theo mốc từ của Scribe; KIỂM TRA từng đoạn.
# usage: cut.py <batch_id> <master.mp3> <words.json> <n,n,n,...>
# Kiểm: (1) chuỗi từ Scribe khớp đúng từng câu theo thứ tự, không dư/thiếu; (2) ranh giới cắt nằm giữa khe hở (≤0.2s mỗi bên) và
# 30 ms đầu/cuối đoạn gần như im lặng (không cắt vào âm đầu/cuối, không dính câu bên cạnh); (3) thời lượng đoạn ≈ từ đầu→từ cuối + đệm.
import json, re, sys, os, subprocess, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bid, master, wj, ns = sys.argv[1], sys.argv[2], sys.argv[3], [int(x) for x in sys.argv[4].split(',')]
Q = json.load(open(R + '/state/queue.json')); W = json.load(open(wj)); W = W.get('words', W) if isinstance(W, dict) else W
W = [w for w in W if w.get('type', 'word') == 'word']
tok = lambda s: re.sub(r'[^\wäöüßÄÖÜ]+', ' ', s.lower()).split()
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', master], capture_output=True, text=True).stdout)
now = lambda: datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
spans = []; i = 0; err = []
for n in ns:
    need = tok(Q[n]['tts']); j = i; got = []
    while j < len(W) and len(got) < len(need):
        t = tok(W[j]['text']); got += t; j += 1
    if got != need: err.append((n, 'mismatch', need[:6], got[:6]))
    spans.append((n, i, j - 1)); i = j
if i != len(W): err.append(('*', 'thừa từ cuối', len(W) - i))
if err: print('FAIL tokens', err); sys.exit(2)
PAD = 0.12
import array, math
def rms(p, a, b):
    o = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{max(0, a):.3f}', '-t', f'{b - a:.3f}', '-i', p, '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True)
    x = array.array('h'); x.frombytes(o.stdout[:len(o.stdout) // 2 * 2])
    if not len(x): return -99.0
    return round(20 * math.log10(max(1e-9, math.sqrt(sum(v * v for v in x) / len(x)) / 32768)), 1)
WIN, MINSIL, SILDB = 0.15, 0.08, -50
def silence(p, a, b):
    # khung 10 ms; trả (đầu, cuối) của đoạn lặng dài nhất ≤ SILDB, None nếu < MINSIL
    a = max(0.0, a); o = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', p, '-f', 's16le', '-ac', '1', '-ar', '16000', '-'], capture_output=True).stdout
    x = array.array('h'); x.frombytes(o[:len(o) // 2 * 2]); n = 160; best = None; st = None
    fr = [20 * math.log10(max(1e-9, math.sqrt(sum(v * v for v in x[i:i + n]) / n) / 32768)) <= SILDB for i in range(0, len(x) - n + 1, n)] + [False]
    for k, q in enumerate(fr):
        if q and st is None: st = k
        if not q and st is not None:
            if best is None or k - st > best[1] - best[0]: best = (st, k)
            st = None
    return (a + best[0] * 0.01, a + best[1] * 0.01) if best and (best[1] - best[0]) * 0.01 >= MINSIL else None
DRY = os.environ.get('DRY') == '1'
res = []; bad = 0
for k, (n, a, b) in enumerate(spans):
    a0 = a
    while a0 < b and not re.search(r'\w', W[a0]['text']): a0 += 1   # token mở đầu không có chữ (vd „…,“) → bỏ khỏi mốc bắt đầu
    fw, lw = W[a0], W[b]
    prev_end = W[a0 - 1]['end'] if a0 > 0 else 0.0; next_start = W[b + 1]['start'] if b + 1 < len(W) else dur
    # 2026-10-14: mốc Scribe hay lệch vào khoảng lặng → đặt điểm cắt theo khoảng lặng THẬT trên sóng âm (dài nhất, ≥ MINSIL) quanh biên
    if a0 == 0: s = 0.0; rs = None
    else:
        rs = silence(master, prev_end - WIN, fw['start'] + WIN)
        s = max(rs[0], rs[1] - PAD) if rs else max(fw['start'] - PAD, (prev_end + fw['start']) / 2)
    if b + 1 == len(W): e = dur; re_ = None
    else:
        re_ = silence(master, lw['end'] - WIN, next_start + WIN)
        e = min(re_[1], re_[0] + PAD) if re_ else min(lw['end'] + PAD, (lw['end'] + next_start) / 2)
    out = R + '/mp3/' + Q[n]['key'] + '.mp3'; tmp = out + '.part.mp3'
    fi, fo = 0.006, 0.012
    if DRY: out = '/tmp/claude-0/dry.mp3'; tmp = out + '.part.mp3'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{s:.3f}', '-t', f'{e - s:.3f}', '-i', master, '-af', f'afade=t=in:d={fi},afade=t=out:st={max(0, e - s - fo):.3f}:d={fo}', '-ar', '44100', '-b:a', '128k', '-codec:a', 'libmp3lame', tmp], check=True)
    os.replace(tmp, out)
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout)
    head = rms(master, s, s + 0.03) if a0 else -99.0; tail = rms(master, e - 0.03, e) if b + 1 < len(W) else -99.0
    spoken = lw['end'] - fw['start']
    # biên đầu/cuối: nếu có khoảng lặng thật thì điểm cắt nằm TRONG nó là đủ (mốc Scribe hay trễ/sớm ~0,1–0,15 s); không có thì dùng mốc Scribe như cũ
    lead_ok = a0 == 0 or (rs is not None and rs[0] <= s <= rs[1]) or (rs is None and fw['start'] - s >= 0.03 - 1e-9)
    trail_ok = b + 1 == len(W) or (re_ is not None and re_[0] <= e <= re_[1]) or (re_ is None and lw['end'] + 0.01 <= e)
    ok = abs(d - (e - s)) < 0.12 and lead_ok and trail_ok and head < -45 and tail < -45
    if a0 == 0 and re_ is None: ok = ok and d >= spoken
    rec = dict(ts=now(), event='result', n=n, key=Q[n]['key'], batch=bid, status='ok' if ok else 'check_fail', dur=round(d, 3), size=os.path.getsize(out), file='mp3/' + Q[n]['key'] + '.mp3', lead=round(fw['start'] - s, 3), trail=round(e - lw['end'], 3), head_rms=head, tail_rms=tail, words=b - a + 1)
    bad += not ok; res.append(rec)
    print(rec['status'], n, f"dur={d:.2f} lead={rec['lead']} trail={rec['trail']} head={head} tail={tail}", Q[n]['tts'][:50])
if DRY: sys.exit(1 if bad else 0)
with open(R + '/state/ledger.jsonl', 'a') as f:
    for r in res: f.write(json.dumps(r, ensure_ascii=False) + '\n')
    f.write(json.dumps(dict(ts=now(), event='batch_result', batch=bid, session=json.load(open(R + '/state/batches/' + bid + '.json'))['session'], status='ok' if not bad else 'check_fail', n_ok=len(res) - bad), ensure_ascii=False) + '\n')
sys.exit(1 if bad else 0)
