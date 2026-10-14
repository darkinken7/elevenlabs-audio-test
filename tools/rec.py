#!/usr/bin/env python3
# Sổ chi tiêu + trạng thái từng lượt tạo (append-only: state/ledger.jsonl).
#  submit: stdin JSON [{n, flow, session, chars}]  → ghi 'submitted' NGAY khi tạo (trước khi poll)
#  done:   stdin JSON [{session, gen, credits, dur, url}] → tải MP3 (thử lại tối đa 4 lần, KHÔNG tạo lại), kiểm, ghi 'ok'/'dl_fail'
#  sum:    in tổng credits + trạng thái
import json, sys, os, time, subprocess, urllib.request, datetime
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = R + '/state/ledger.jsonl'; Q = json.load(open(R + '/state/queue.json'))
now = lambda: datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
def log(o): open(L, 'a').write(json.dumps(o, ensure_ascii=False) + '\n')
def rows(): return [json.loads(l) for l in open(L)] if os.path.exists(L) else []
def latest():
    s = {}
    for r in rows():
        if 'session' in r: s.setdefault(r['session'], {}).update(r)
    return s
def probe(p):
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,format_name:stream=codec_name,sample_rate,channels', '-of', 'json', p], capture_output=True, text=True)
    j = json.loads(o.stdout or '{}'); f = j.get('format', {}); st = (j.get('streams') or [{}])[0]
    return float(f.get('duration', 0)), f.get('format_name'), st.get('codec_name'), st.get('sample_rate')
cmd = sys.argv[1]
if cmd == 'submit':
    for x in json.load(sys.stdin):
        e = Q[x['n']]; log({'ts': now(), 'event': 'submitted', 'n': x['n'], 'key': e['key'], 'speak': e['speak'], 'chars': e['chars'], 'flow': x['flow'], 'session': x['session'], 'model': 'eleven_multilingual_v2', 'voice_id': 'pMrwpTuGOma7Nubxs5jo', 'status': 'submitted'})
elif cmd == 'done':
    st = latest(); bad = 0
    for x in json.load(sys.stdin):
        s = st[x['session']]; e = Q[s['n']]; p = R + '/mp3/' + e['key'] + '.mp3'; err = None
        for a in range(4):
            try:
                urllib.request.urlretrieve(x['url'], p + '.part'); os.replace(p + '.part', p); err = None; break
            except Exception as ex: err = str(ex)[:200]; time.sleep(2 ** (a + 1))
        rec = {'ts': now(), 'event': 'result', 'n': s['n'], 'key': e['key'], 'session': x['session'], 'gen': x['gen'], 'credits': x['credits'], 'api_dur': x['dur']}
        if err: rec.update(status='dl_fail', error=err); bad += 1
        else:
            d, fmt, codec, sr = probe(p); size = os.path.getsize(p)
            okk = fmt == 'mp3' and codec == 'mp3' and size > 2000 and abs(d - x['dur']) < 0.2 and 0.25 < d / max(1, e['chars']) * 15 < 4
            rec.update(status='ok' if okk else 'check_fail', dur=round(d, 3), size=size, codec=codec, sr=sr, file='mp3/' + e['key'] + '.mp3')
            if not okk: bad += 1
        log(rec); print(rec['status'], s['n'], e['key'], rec.get('dur'), e['speak'][:60])
    sys.exit(1 if bad else 0)
elif cmd == 'bsubmit':   # bsubmit <id> <flow> <session> <gen> <credits> <n_from> <n_to>  (ns liên tục)
    bid, flow, ses, gen, cr, nl = sys.argv[2:8]; ns = [int(x) for x in nl.split(',')]
    log({'ts': now(), 'event': 'batch_submitted', 'batch': bid, 'ns': ns, 'flow': flow, 'session': ses, 'gen': gen, 'credits': float(cr), 'chars_sent': sum(len(Q[n]['tts']) + 2 for n in ns) - 2, 'model': 'eleven_multilingual_v2', 'voice_id': 'pMrwpTuGOma7Nubxs5jo', 'status': 'submitted'})
    json.dump({'session': ses, 'ns': ns}, open(R + '/state/batches/' + bid + '.json', 'w'))
elif cmd == 'sum':
    st = latest(); c = sum(float(v.get('credits', 0)) for v in st.values()); by = {}
    for v in st.values(): by[v.get('status', '?')] = by.get(v.get('status', '?'), 0) + 1
    prior = json.load(open(R + '/state/prior_spend.json'))['total']; tot = c + prior
    print('ledger: job %.1f + prior %.1f = %.1f credits đã chi; trạng thái %s' % (c, prior, tot, by))
    bf = R + '/state/balance.json'
    if os.path.exists(bf):   # số dư James cung cấp (mốc) → số dư SUY RA từ ledger; chỉ là suy ra, không phải số dư đã xác minh
        b = json.load(open(bf)); a0 = b.get('ledger_total_at_anchor')
        if a0 is not None: print('mốc James %s: %s credits · đã chi từ mốc theo ledger %.1f → số dư SUY RA ≈ %.1f (chưa xác minh trên elevenlabs.io)' % (b['as_of'], b['balance'], tot - a0, b['balance'] - (tot - a0)))
    pend = [v['session'] for v in st.values() if v.get('status') == 'submitted']
    if pend: print('PENDING', json.dumps(pend))
