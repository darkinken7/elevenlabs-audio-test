// Hiệu chỉnh manifest v1: bước Treppe thật là steps:[{tag,a:[de,vi],b:[de,vi]}] (ui.jsx: <Snd text={ln[0]}/> cho a và b); build_manifest.mjs v1 đọc sai cấu trúc
// → bỏ sót câu Treppe và sinh mục "[object Object]". usage: node tools/extra_treppe.mjs <thư mục grammatik-trainer (đọc, không sửa)>
import fs from 'fs'; import crypto from 'crypto';
const SRC = process.argv[2] + '/theme/src/';
function lit(s, name, open = '[', close = ']') { const st = s.indexOf('const ' + name + ' = '); if (st < 0) return null;
  let i = s.indexOf(open, st), d = 0, inStr = false, q = '', esc = false, tmpl = false; const start = i;
  for (; i < s.length; i++) { const c = s[i]; if (esc) { esc = false; continue; } if (inStr) { if (c === '\\') esc = true; else if (c === q) inStr = false; continue; }
    if (tmpl) { if (c === '\\') esc = true; else if (c === '`') tmpl = false; continue; } if (c === '"' || c === "'") { inStr = true; q = c; continue; } if (c === '`') { tmpl = true; continue; }
    if (c === open) d++; else if (c === close) { d--; if (d === 0) return s.slice(start, i + 1); } } }
const plain = (t) => String(t || '').replace(/\*/g, '').replace(/\s\/\s/g, ', ').replace(/\([^)]*\)/g, ' ').replace(/\s+/g, ' ').replace(/\s+([.,!?;:])/g, '$1').trim();
const rows = new Map();
for (const app of fs.readdirSync(SRC).filter((f) => f.endsWith('.jsx')).map((f) => f.slice(0, -4))) {
  const f = app === 'cluster-f-modalpartikeln' ? process.argv[2] + '/theme/cluster-f-data.jsx' : SRC + app + '.jsx';
  const s = fs.readFileSync(f, 'utf8'); const TH = lit(s, 'THEORIE'); if (!TH) continue;
  for (const c of eval(TH)) (c.blocks || []).forEach((b, bi) => { if (b.k !== 'treppe') return;
    (b.steps || []).forEach((st, si) => [st.a, st.b].forEach((ln, li) => { const p = plain(Array.isArray(ln) ? ln[0] : ''); if (!p) return;
      if (!rows.has(p)) rows.set(p, []); rows.get(p).push({ app, kind: 'treppe', ref: `${c.id}#${bi}.${si}.${'ab'[li]}` }); })); });
}
const out = [...rows.entries()].map(([t, uses]) => ({ key: crypto.createHash('sha1').update(t).digest('hex').slice(0, 12), text: t, speak: t, cls: 'de', chars: t.length, group: 'lernen+treppe', uses }));
const remove_keys = [crypto.createHash('sha1').update('[object Object].').digest('hex').slice(0, 12), crypto.createHash('sha1').update('[object Object]').digest('hex').slice(0, 12)];
fs.writeFileSync(new URL('../source/manifest.corrections.json', import.meta.url), JSON.stringify({ why: 'v1 đọc sai cấu trúc Treppe', remove_keys, add_rows: out }, null, 1));
console.log(out.length, 'câu Treppe,', out.reduce((a, r) => a + r.chars, 0), 'ký tự');
