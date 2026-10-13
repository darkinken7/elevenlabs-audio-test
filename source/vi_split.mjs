// 2026-10-13 · Tách phần tiếng Đức khỏi câu có chữ Việt (cho nút 🔊).
// Luật: cắt theo dấu nối mạnh (— – · = → ; : , và ngoặc „…“ có chữ Việt); đoạn KHÔNG có chữ Việt và có ít nhất 1 từ Đức thật
// (không tính chữ cái lẻ / viết tắt in hoa ≤ 3 chữ như NS, QK, số) là phần tiếng Đức.
// Kết quả: cls 'de' (không có chữ Việt) · 'mixed' (đọc phần Đức) · 'vi' (thuần Việt hoặc giải thích Việt có thuật ngữ Đức → ẩn 🔊).
export const VI_CH = /[ăâêôđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹàèìòùýĐ]/i;
// từ Việt không dấu hay gặp trong giải thích (không trùng từ Đức thông dụng)
export const VI_PLAIN = /(^|[^A-Za-zÄÖÜäöüß])(thay|cho|hay|khi|nay|xin|anh|em|va|la|ma|ra|sau|con|tin|nhanh|xa|theo|chia|né|tránh)(?=$|[^A-Za-zÄÖÜäöüß])/i;
export function deParts(text) {
  const t = String(text || '').trim();
  if (!VI_CH.test(t)) return { cls: 'de', de: t };
  const segs = t.split(/\s*(?:[—–·=→;:,]|\s\/\s)\s*/).map((x) => x.trim()).filter(Boolean);
  const isDe = (s) => !VI_CH.test(s) && !VI_PLAIN.test(s) && s.split(/[^A-Za-zÄÖÜäöüß]+/).some((w) => w.length >= 2 && !(w.length <= 3 && w === w.toUpperCase()));
  const de = segs.filter(isDe);
  return de.length ? { cls: 'mixed', de: de.join(', ') } : { cls: 'vi', de: '' };
}
