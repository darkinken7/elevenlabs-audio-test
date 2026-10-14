#!/usr/bin/env python3
# Chọn lô tiếp theo: các câu CHƯA có mp3 và chưa nằm trong lượt đang chờ, cùng nhóm ưu tiên, tối đa MAXC ký tự (tts). In JSON: ns + prompt (ngăn bằng dòng trống).
import json, sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAXC = int(sys.argv[1]) if len(sys.argv) > 1 else 1400
Q = json.load(open(R + '/state/queue.json')); have = set(); pend = set(); subm = {}; closed = set(); fails = {}
for l in open(R + '/state/ledger.jsonl'):
    r = json.loads(l)
    if r.get('event') == 'result' and r.get('status') == 'ok': have.add(r['n'])
    if r.get('event') == 'result' and r.get('status') != 'ok': fails[r['n']] = fails.get(r['n'], 0) + 1
    if r.get('event') == 'batch_submitted': subm[r['batch']] = r['ns']
    if r.get('event') == 'batch_result': closed.add(r['batch'])
    if r.get('event') == 'submitted' and r.get('status') == 'submitted': pend.add(r['n'])
for b, ns_ in subm.items():
    if b not in closed: pend.update(ns_)
GI = ['lernen+treppe', 'passiv', 'konjunktiv', 'cluster-c', 'schreiben', 'fehler-korrekt', 'rest']
todo = sorted([e for e in Q if e['n'] not in have and e['n'] not in pend and not e.get('skip') and fails.get(e['n'], 0) < 3], key=lambda e: (GI.index(e['group']), e['n']))
if not todo: print('{}'); sys.exit()
g = todo[0]['group']; ns = []; c = 0
for e in todo:
    pass
    L = len(e['tts']) + 2
    if ns and c + L > MAXC: break
    ns.append(e['n']); c += L
# Đơn vị ngắn/liệt kê hoặc từng hỏng: xen giữa các câu dài để có khoảng nghỉ rõ khi cắt
def short(n): t = Q[n]['tts']; return n in fails or len(t) < 40 or t.count('. ') >= 1 and len(t) < 70
S_ = [n for n in ns if short(n)]; Lg = [n for n in ns if not short(n)]; ord_ = []
while S_ or Lg:
    if Lg: ord_.append(Lg.pop(0))
    if S_: ord_.append(S_.pop(0))
ns = ord_
if len(sys.argv) > 2: open(R + '/state/batches/' + sys.argv[2] + '.prompt.txt', 'w').write('\n\n'.join(Q[n]['tts'] for n in ns))
print(json.dumps({'group': g, 'ns': ns, 'chars': c, 'remaining_in_group': sum(1 for e in todo if e['group'] == g) - len(ns), 'prompt': '\n\n'.join(Q[n]['tts'] for n in ns)}, ensure_ascii=False))
