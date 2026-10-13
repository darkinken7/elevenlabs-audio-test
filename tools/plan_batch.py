#!/usr/bin/env python3
# Chọn lô tiếp theo: các câu CHƯA có mp3 và chưa nằm trong lượt đang chờ, cùng nhóm ưu tiên, tối đa MAXC ký tự (tts). In JSON: ns + prompt (ngăn bằng dòng trống).
import json, sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAXC = int(sys.argv[1]) if len(sys.argv) > 1 else 1400
Q = json.load(open(R + '/state/queue.json')); have = set(); pend = set()
for l in open(R + '/state/ledger.jsonl'):
    r = json.loads(l)
    if r.get('event') == 'result' and r.get('status') == 'ok': have.add(r['n'])
    if r.get('event') == 'batch_submitted' and r.get('status') != 'cut_failed': pend.update(r['ns'])
    if r.get('event') == 'submitted' and r.get('status') == 'submitted': pend.add(r['n'])
todo = [e for e in Q if e['n'] not in have and e['n'] not in pend]
if not todo: print('{}'); sys.exit()
g = todo[0]['group']; ns = []; c = 0
for e in todo:
    if e['group'] != g: break
    L = len(e['tts']) + 2
    if ns and c + L > MAXC: break
    ns.append(e['n']); c += L
print(json.dumps({'group': g, 'ns': ns, 'chars': c, 'remaining_in_group': sum(1 for e in todo if e['group'] == g) - len(ns), 'prompt': '\n\n'.join(Q[n]['tts'] for n in ns)}, ensure_ascii=False))
