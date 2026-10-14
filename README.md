# elevenlabs-audio-test — MP3 cho nút 🔊 của grammatik-trainer

Nguồn nội dung: darkinken7/grammatik-trainer @ 1ab76e1 (main, 14 app); luật tách Đức/Việt + manifest @ 92322b6 (work/c67-68). Chi tiết: state/source.json.
Giọng Lea Brandt – Explainer (pMrwpTuGOma7Nubxs5jo), eleven_multilingual_v2, 1 bản/câu.

- source/manifest.full.json: 6.600 câu, mọi vị trí dùng (uses). cls: de / mixed / vi.
- state/queue.json: 6.178 câu Đức thuần, gộp trùng theo key, xếp theo ưu tiên (Lernen+Treppe → Passiv → Konjunktiv → Cluster C → Schreiben → Fehler Korrekt → còn lại). `tts` = chữ gửi đi (chỉ đổi · ↔ → = thành dấu ngắt).
- Câu mixed (257) và vi (165) KHÔNG tạo: mixed giữ cách phát hiện tại vì phần Đức do luật tách, chưa chắc chắn; vi đã ẩn 🔊.
- state/ledger.jsonl: mỗi lượt ghi 'submitted' (flow, session) ngay khi tạo, rồi 'result' (gen id, credits, thời lượng, trạng thái). Tải lỗi → tải lại URL cũ, không tạo lại.
- state/prior_spend.json: credits đã chi trước phiên này.
- audio-map.json: câu → file (dùng cho window.__GT_AUDIO). patches/gt-audio-speakDe.patch: bản vá app (chưa áp vào grammatik-trainer).
- Lệnh: node tools/build_queue.mjs · python3 tools/rec.py submit|done|sum · python3 tools/build_map.py

## Khóa tra cho app (2026-10-14)
- `audio-map.json` / `audio-map.usable.json` khóa theo văn bản gửi TTS (`tts`, có thể thêm dấu chấm) — chỉ dùng nội bộ, KHÔNG dùng để tra trong app.
- App dùng `audio-index.json` (tools/export_index.py): mỗi mục `{file, texts, apps}`, `texts` = chuỗi app truyền vào speakDe() đã chuẩn hóa bằng đúng quy tắc `gtNorm` (theme/audio/norm.mjs bên grammatik-trainer). Chỉ gồm câu cắt đạt và không nằm trong CONTENT_FLAGS.md.
