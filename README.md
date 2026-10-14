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

## Ngân sách (James, 2026-10-14 chiều)
Bỏ dự phòng 10.000 và trần cũ 151.000 credits. Khi tạo tiếp câu còn thiếu: dùng trong số credits THỰC TẾ còn trong tài khoản, không tạo trùng (kiểm queue/ledger trước mỗi đợt), không mua thêm, không bật phí vượt hạn mức. Chưa tạo thêm cho đến khi James bảo tiếp tục.

## Quy trình tạo tiếp (cập nhật 2026-10-14 chiều — đọc trước khi tạo gì)
Bài học đắt giá của phiên này nằm ở mục „Lỗi/đính chính“ bên dưới; đừng bỏ qua.
1. **Số dư**: connector ElevenLabs KHÔNG có lệnh đọc số dư. `state/balance.json` = số James cung cấp (mốc). `python3 tools/rec.py sum` in số dư SUY RA từ ledger (chưa xác minh). Đầu mỗi đợt: hỏi James xem lại trên elevenlabs.io.
2. **Kiểm kê** (câu thật sự còn thiếu, theo từng app): `node <grammatik-trainer>/theme/audio/inventory.mjs <thư mục repo này> --apps a,b,c --emit missing.json`. Công cụ đọc mã nguồn app HIỆN TẠI, loại câu đã có MP3, câu thuộc diện đánh dấu (CONTENT_FLAGS + `state/pending_flags.json` do `tools/flags.py` ghi), câu Việt/mixed.
3. **Giá**: 0,9999 credit × ký tự gửi đi. Tính cả „\n\n“ ngăn câu (2 ký tự/câu) và mỗi thẻ `<break time="…"/>` (11 ký tự). Multilingual v2 và Turbo v2.5 giá như nhau. (Ghi 0,94/0,91 trước đây là SAI.)
4. **Lập lô**: `PLAN_ONLY=missing.json python3 tools/plan_batch.py <số ký tự tối đa> <id lô> > state/batches/<id>.plan.json` (ghi luôn `<id>.prompt.txt`). Cỡ đã kiểm chứng: 2.700–2.800 ký tự/lô (≈ 200 s).
5. **Tạo**: MCP `creative_generate_speech`, model `eleven_multilingual_v2`, giọng Lea Brandt `pMrwpTuGOma7Nubxs5jo`, `generations_count=1`, flow `CreFyryjdIL7L0dtSziW`. KHÔNG gọi lại để thử lại. Ngay khi có session/gen: `bash tools/sub.sh <id> <flow> <session> <gen> <credits>`.
6. **Scribe** (`creative_transcribe_audio`) lấy mốc từ để cắt: **165 credits MỖI LẦN GỌI** (giá cố định, kể cả file 50 s hay 200 s; file ≤ 13 s sáng 14/10 từng 0). `estimate_only` của Scribe LUÔN báo 0 → không dự toán được. Vì giá cố định nên mỗi lô nên đủ lớn (≈ 2.700 ký tự) để phí Scribe chỉ ≈ 6%. Đã thử cắt cục bộ theo khoảng lặng (quy hoạch động + dấu ngắt): chỉ đúng ≈ 77% ranh giới so với Scribe trên 58 lô → KHÔNG dùng (gắn nhầm âm thanh nguy hiểm hơn tốn 165 credits). Không có ASR cục bộ vì mạng chặn huggingface.co.
7. **Cắt/kiểm**: `python3 tools/cut.py <id> <master.mp3> <words.json> <ns>` chạy ĐÚNG MỘT LẦN (chạy lại ghi trùng ledger; muốn chỉ xem: `DRY=1`). Câu `check_fail` được lập lại ở lô sau (plan_batch tự rải xa nhau).
8. **Sau cùng**: `python3 tools/flags.py && python3 tools/export_index.py && python3 tools/build_map.py`, rồi commit + push.
9. Đừng dùng `pkill -f <tên>` trong cùng lệnh có chứa tên đó (tự giết shell).

## Lỗi/đính chính (phiên 2026-10-14)
- Giá ký tự ghi trước đây (0,94 / 0,91) sai; đúng 0,9999. Ước tính „53.455 ký tự ≈ 50.000 credits; 8.200 cho 5 app“ sai theo cùng nguyên nhân và còn bỏ sót ký tự ngăn câu.
- `tools/rec.py sum` hỏng khi ledger có dòng không có `status` (đã sửa) và không còn in „cap 151000“.
- Ledger có các dòng trùng của sm-002 (cut.py chạy 2 lần) — giống hệt nhau, vô hại.
- 18 + 8 câu của 4 app bị loại khỏi lần tạo vì sẽ bị đánh dấu ngay (có „…“, „/“, „+“) hoặc chỉ là âm tiết/hậu tố („ä“, „ie“, „-en“, „- n“) — xem `state/pending_flags.json`.
