# Độ phủ audio ElevenLabs (cập nhật 2026-10-14, sau đối chiếu)

Đối chiếu: ledger ok (kết quả mới nhất) = 4232 · audio-map.json = 4232 mục · file mp3/ = 4232 · khớp 1:1. Ghi chú: „der reparierte Motor.“ được tạo 2 lần (2 mục nguồn khác nhau chỉ ở ký hiệu ✓) → 4232 file nhưng 4231 câu khác nhau; map dùng 1 file, file kia thừa.
Câu duy nhất có MP3 DÙNG ĐƯỢC (audio-map.usable.json) = 3947; 285 câu có MP3 nhưng bị loại do nội dung nguồn (xem CONTENT_FLAGS.md).
Câu trùng giữa các app dùng chung 1 file (1 câu duy nhất → nhiều lượt dùng). 11 MP3 gốc giữ nguyên, không tính ở đây.

Nhóm | có MP3 | dùng được | cần | bỏ (mixed/VI)
---|---|---|---|---
lernen+treppe | 131 | 124 | 131 | 1
passiv | 446 | 430 | 446 | 0
konjunktiv | 229 | 225 | 229 | 0
cluster-c | 934 | 887 | 934 | 3
schreiben | 586 | 567 | 586 | 0
fehler-korrekt | 1906 | 1715 | 2391 | 0
rest | 0 | 0 | 1483 | 5

App (lượt dùng) | dùng được / tổng | %
---|---|---
cluster-c-angaben-konnektoren | 951/998 | 95%
cluster-d-praep-kasus | 545/894 | 60%
cluster-e-satz-operationen | 428/687 | 62%
cluster-f-modalpartikeln | 638/975 | 65%
fvg-trainer | 0/97 | 0%
genus-plural | 322/472 | 68%
konjunktiv-trainer | 280/285 | 98%
mix-review | 619/1106 | 55%
passiv-trainer | 503/521 | 96%
praefix-kompass | 130/236 | 55%
praeposition-trainer | 133/217 | 61%
unregelmaessige-verben | 393/625 | 62%
vermutung-futur-trainer | 121/228 | 53%
wortschatz | 243/450 | 54%

Câu không có MP3 dùng được → speechSynthesis (fallback).
