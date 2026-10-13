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
const tts = (t) => t.replace(/\s*·\s*/g, (m, o, s) => /[.!?]$/.test(s.slice(0, o)) ? ' ' : '. ').replace(/\s*(↔|→|⇒|=)\s*/g, ', ').replace(/\s+/g, ' ').trim();
q.forEach((e, i) => { e.n = i; e.tts = tts(e.speak); });
fs.writeFileSync(new URL('../state/queue.json', import.meta.url), JSON.stringify(q));
const s = {}; for (const e of q) { s[e.group] = s[e.group] || [0, 0]; s[e.group][0]++; s[e.group][1] += e.chars; }
console.log(q.length, 'câu Đức', JSON.stringify(s));
