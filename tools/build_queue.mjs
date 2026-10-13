// Hàng đợi tạo audio từ manifest đầy đủ của grammatik-trainer (nguồn: xem state/source.json).
// Chỉ câu cls='de' (tiếng Đức thuần). 'vi' → ẩn 🔊; 'mixed' → giữ cách phát hiện tại (phần Đức tách bằng luật, chưa chắc chắn).
// Gộp theo key (băm phần đọc) — một file cho mọi vị trí dùng. Thứ tự: nhóm ưu tiên → thứ tự trong manifest.
import fs from 'fs';
const M = JSON.parse(fs.readFileSync(new URL('../source/manifest.full.json', import.meta.url)));
const G = ['lernen+treppe', 'passiv', 'konjunktiv', 'cluster-c', 'schreiben', 'fehler-korrekt', 'rest'];
const by = new Map();
for (const r of M.rows) {
  if (r.cls !== 'de') continue;
  const e = by.get(r.key) || { key: r.key, speak: r.speak, chars: r.chars, group: r.group, texts: [], uses: [] };
  if (G.indexOf(r.group) < G.indexOf(e.group)) e.group = r.group;
  e.texts.push(r.text); e.uses.push(...r.uses); by.set(r.key, e);
}
const q = [...by.values()].sort((a, b) => G.indexOf(a.group) - G.indexOf(b.group));
// Văn bản gửi TTS: chỉ đổi ký hiệu không đọc được (· ↔ → =) thành dấu ngắt; nội dung chữ giữ nguyên
const tts = (t) => t.replace(/\s*·\s*/g, (m, o, s) => /[.!?]$/.test(s.slice(0, o)) ? ' ' : '. ').replace(/\s*(↔|→|⇒|=)\s*/g, ', ').replace(/…\./g, '…').replace(/[✓✔✗✘]/g, '').replace(/\.,/g, '.').replace(/\s+/g, ' ').trim();
q.forEach((e, i) => { e.n = i; e.tts = tts(e.speak); if (!/[.!?…]$/.test(e.tts) && i > 14 && ![15,16,17,44,45,46].includes(i)) e.tts += '.'; });  // cụm không dấu câu: thêm '.' để model ngắt rõ (n≤52 giữ nguyên chữ đã gửi)
// Hiệu chỉnh (xem tools/extra_treppe.mjs): đánh dấu skip mục rác (giữ nguyên n); câu Treppe bổ sung nối thêm cuối (n mới), câu đã có thì gộp thêm vị trí dùng
const C = JSON.parse(fs.readFileSync(new URL('../source/manifest.corrections.json', import.meta.url)));
for (const e of q) if (C.remove_keys.includes(e.key)) e.skip = true;
const byKey = new Map(q.map((e) => [e.key, e]));
for (const r of C.add_rows) { const ex = byKey.get(r.key);
  if (ex) { ex.uses.push(...r.uses); ex.texts.push(r.text); if (G.indexOf('lernen+treppe') < G.indexOf(ex.group)) ex.group = 'lernen+treppe'; }
  else { const e = { key: r.key, speak: r.speak, chars: r.chars, group: r.group, texts: [r.text], uses: r.uses.slice(), n: q.length, tts: tts(r.speak) }; if (!/[.!?…]$/.test(e.tts)) e.tts += '.'; q.push(e); byKey.set(e.key, e); } }
fs.writeFileSync(new URL('../state/queue.json', import.meta.url), JSON.stringify(q));
const s = {}; for (const e of q.filter((e) => !e.skip)) { s[e.group] = s[e.group] || [0, 0]; s[e.group][0]++; s[e.group][1] += e.chars; }
console.log(q.length, 'câu Đức', JSON.stringify(s));
