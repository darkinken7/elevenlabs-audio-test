# elevenlabs-audio-test — bàn giao (2026-10-14)

Bản đầy đủ nằm ở repo `darkinken7/grammatik-trainer`, nhánh `claude/audio-integration`, file **`docs/AUDIO_HANDOFF.md`** (đọc file đó trước). Dưới đây chỉ là phần riêng của repo audio.

## Trạng thái một dòng
4.625 MP3 trong `mp3/` (4.341 mục dùng được trong `audio-index.json`, 284 file đã có nhưng bị loại theo `CONTENT_FLAGS.md`). Quy tắc tạm dừng; mẫu pa1 chưa duyệt. Số dư do James cung cấp 10.857 (14/10) → suy ra từ ledger ≈ 2.579 sau đợt 4 app.

## Nhánh và nơi đặt dữ liệu
- Nhánh làm việc: `claude/grammatik-audio-workflow-b5injh` (chưa merge main, không merge khi James chưa bảo).
- `mp3/<key>.mp3` — một file/câu, tên theo băm câu gửi TTS (`state/queue.json` → `key`).
- `audio-index.json` — khóa tra cho app (`texts` = chuỗi app đã qua `gtNorm`). Chỉ mục này mới đưa vào app; `audio-map*.json` là bản nội bộ theo văn bản gửi TTS.
- `state/ledger.jsonl` — sổ chi tiêu append-only. `state/balance.json` — số dư James cung cấp (mốc). `python3 tools/rec.py sum` — tổng đã chi + số dư SUY RA.
- `state/queue.json` — 6.209 câu Đức thuần; `state/content_flags.json` (đã có file nhưng không dùng) và `state/pending_flags.json` (chưa tạo vì sẽ bị đánh dấu) do `tools/flags.py` ghi.
- `state/batches/<id>.*` — mỗi lô: `plan.json`, `prompt.txt`, `master.mp3`, `words.json` (Scribe); `cut.log` chỉ có từ sm-003.
- `rules/` — lời đọc quy tắc: `pa1.mp3` (ghép), `src/pa1.<khối>.<ngôn ngữ>.mp3` (4 đoạn giữ riêng), `index.json` (prompt, model, giọng, sha, credits từng đoạn). **Mẫu chưa duyệt, không nhân rộng.**

## Quy trình tạo tiếp
Xem mục „Quy trình tạo tiếp (cập nhật 2026-10-14 chiều)“ trong `README.md`. Ba điều dễ quên nhất:
1. Giá = 0,9999 × ký tự gửi đi (kể cả „\n\n“ ngăn câu); Scribe = 165 credits mỗi lần gọi và `estimate_only` của Scribe luôn báo 0.
2. `tools/cut.py` chạy đúng một lần mỗi lô.
3. Kiểm kê bằng `theme/audio/inventory.mjs` (repo grammatik-trainer) trước mỗi đợt, không dùng số ước tính cũ.
