// 2026-10-13 · Danh sách câu cần âm thanh (mọi nút 🔊) từ mã nguồn hiện tại của repo → gộp trùng toàn bộ 14 app,
// giữ ánh xạ từng câu với MỌI vị trí dùng; chia nhóm ưu tiên KHÔNG cộng trùng (mỗi câu tính một lần, ở nhóm ưu tiên cao nhất).
// usage: node audio/build_manifest.mjs [audio/manifest.json]
// Văn bản chuẩn hóa GIỐNG HỆT speakDe() của engine (bỏ *, (…), " / " → ", ") — đây cũng là khóa tra file khi phát.
import fs from 'fs'; import crypto from 'crypto'; import path from 'path'; import { deParts } from './vi_split.mjs';
const R = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const SRC = R + '/theme/src/', OUT = R + '/theme/out/';
function lit(s, name, open = '[', close = ']') { const st = s.indexOf('const ' + name + ' = '); if (st < 0) return null;
  let i = s.indexOf(open, st), d = 0, inStr = false, q = '', esc = false, tmpl = false; const start = i;
  for (; i < s.length; i++) { const c = s[i]; if (esc) { esc = false; continue; } if (inStr) { if (c === '\\') esc = true; else if (c === q) inStr = false; continue; }
    if (tmpl) { if (c === '\\') esc = true; else if (c === '`') tmpl = false; continue; } if (c === '"' || c === "'") { inStr = true; q = c; continue; } if (c === '`') { tmpl = true; continue; }
    if (c === open) d++; else if (c === close) { d--; if (d === 0) return s.slice(start, i + 1); } } }
export const plain = (t) => String(t || '').replace(/\*/g, '').replace(/\s\/\s/g, ', ').replace(/\([^)]*\)/g, ' ').replace(/\s+/g, ' ').replace(/\s+([.,!?;:])/g, '$1').trim();
const ENGINE = ['cluster-c-angaben-konnektoren', 'cluster-d-praep-kasus', 'cluster-e-satz-operationen', 'cluster-f-modalpartikeln', 'passiv-trainer', 'konjunktiv-trainer',
  'vermutung-futur-trainer', 'praeposition-trainer', 'praefix-kompass', 'genus-plural', 'unregelmaessige-verben', 'wortschatz'];
const all = new Map(); let pos = 0;
const add = (app, kind, ref, t) => { const p = plain(t); if (!p || !/[A-Za-zÄÖÜäöüß]/.test(p)) return; pos++;
  if (!all.has(p)) all.set(p, []); all.get(p).push({ app, kind, ref }); };
for (const app of ENGINE) {
  const f = app === 'cluster-f-modalpartikeln' ? R + '/theme/cluster-f-data.jsx' : SRC + app + '.jsx';
  const s = fs.readFileSync(f, 'utf8');
  let items = []; for (const n of ['ITEMS', 'PROFI', 'WRITE']) { const L = lit(s, n); if (L) items = items.concat(eval(L)); }
  const seen = new Set();
  for (const it of items) {
    if (seen.has(it.id)) continue; seen.add(it.id);
    if (it.type === 'form') add(app, 'form', it.id, it.answer);
    else if (it.type === 'transform') add(app, 'transform', it.id, it.answer);
    else if (it.type === 'error') add(app, 'error', it.id, it.correct);
    else if (it.type === 'write') add(app, 'write', it.id, it.model);
  }
  const TH = lit(s, 'THEORIE'); if (TH) for (const c of eval(TH)) (c.blocks || []).forEach((b, bi) => {
    if (b.k === 'ex') { const parts = String(b.de).split(' → '); add(app, 'lernen', c.id + '#' + bi, parts.length === 2 ? parts[0] : b.de); }
    if (b.k === 'treppe') (b.lanes || []).flatMap((l) => l.steps || []).concat(b.steps || []).forEach((ln, si) => add(app, 'treppe', c.id + '#' + bi + '.' + si, Array.isArray(ln) ? ln[0] : (ln.de || ln)));
  });
}
{ const s = fs.readFileSync(OUT + 'mix-review.jsx', 'utf8'); const D = eval(lit(s, 'DATA'));
  const vre = s.match(/const VI_RE\s*=\s*(\/[^\n]*\/[a-z]*);/); const VI_RE = vre ? eval(vre[1]) : /[ăâđêôơư]/i;
  const mcSrc = s.slice(s.indexOf('function mcSay('), s.indexOf('\n}', s.indexOf('function mcSay(')) + 2); const mcSay = eval('(' + mcSrc + ')');
  D.forEach((it, i) => { if (it.type === 'mc') { const t = mcSay(it); if (t) add('mix-review', 'waehlen', i, t); } else if (it.cr) add('mix-review', 'error', i, it.cr); }); }
{ const s = fs.readFileSync(OUT + 'fvg-trainer.jsx', 'utf8'); const D = eval('(' + lit(s, 'DATA', '{', '}') + ')');
  (D.items || []).forEach((it, i) => { if (it.bsp) add('fvg-trainer', 'beispiel', it.id || i, it.bsp); }); }
// nhóm ưu tiên (James 13/10): Lernen + Treppe → Passiv → Konjunktiv → Cluster C → Schreiben-Musterlösung → câu sửa lỗi (Korrekt) → còn lại
const GROUPS = [['lernen+treppe', (u) => u.kind === 'lernen' || u.kind === 'treppe'], ['passiv', (u) => u.app === 'passiv-trainer'], ['konjunktiv', (u) => u.app === 'konjunktiv-trainer'],
  ['cluster-c', (u) => u.app === 'cluster-c-angaben-konnektoren'], ['schreiben', (u) => u.kind === 'write'], ['fehler-korrekt', (u) => u.kind === 'error'], ['rest', () => true]];
const rows = [...all.entries()].map(([t, uses]) => {
  const g = GROUPS.find(([, f]) => uses.some(f))[0];
  // câu có chữ tiếng Việt (vd đáp án Funktion „sau câu phủ định“, „→ rất tốt“): KHÔNG tạo bằng giọng Đức → giữ giọng trình duyệt
  // 2026-10-13 (James): thuần Việt → ẩn 🔊 (hide-vi); có cả Đức và Việt → giữ 🔊, chỉ đọc phần Đức (speak = phần Đức, tính ký tự theo speak)
  const p = deParts(t); const speak = p.cls === 'vi' ? '' : p.de;
  return { key: crypto.createHash('sha1').update(speak || t).digest('hex').slice(0, 12), text: t, speak, cls: p.cls, chars: speak.length, group: g, uses, file: null, voice_id: null, model: null, status: p.cls === 'vi' ? 'hide-vi' : 'pending' };
});
const sum = {}; let cum = 0; const order = GROUPS.map((g) => g[0]);
const seenKey = new Set();   // nhiều câu có chung phần Đức (vd „Überraschung“) → 1 file, chỉ tính tiền 1 lần
for (const r of rows) { if (r.status === 'hide-vi' || seenKey.has(r.key)) continue; seenKey.add(r.key); sum[r.group] = sum[r.group] || { sentences: 0, chars: 0 }; sum[r.group].sentences++; sum[r.group].chars += r.chars; }
const sk = rows.filter((r) => r.status === 'hide-vi'); const mx = rows.filter((r) => r.cls === 'mixed');
console.log('vị trí có 🔊 (đếm từng chỗ):', pos, '· câu sau gộp trùng:', rows.length, '· ký tự:', rows.reduce((a, r) => a + r.chars, 0));
console.log('ẩn 🔊 (thuần Việt):', sk.length, 'câu · có cả Đức + Việt (chỉ đọc phần Đức):', mx.length, 'câu,', mx.reduce((a, r) => a + r.chars, 0), 'ký tự Đức');
console.log('nhóm (không cộng trùng, chỉ câu tiếng Đức)  câu    ký tự   lũy kế');
for (const g of order) if (sum[g]) { cum += sum[g].chars; console.log(' ', g.padEnd(30), String(sum[g].sentences).padStart(6), String(sum[g].chars).padStart(8), String(cum).padStart(8)); }
const byApp = {}; for (const r of rows) for (const a of new Set(r.uses.map((u) => u.app))) byApp[a] = (byApp[a] || 0) + 1;
console.log('câu theo app (một câu có thể thuộc nhiều app):', JSON.stringify(byApp));
if (process.argv[2]) { fs.writeFileSync(process.argv[2], JSON.stringify({ built: new Date().toISOString(), normalize: 'speakDe: bỏ *, (…), " / " → ", "', rows }, null, 0)); console.log('→', process.argv[2]); }
