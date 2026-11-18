# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5` (judge replay từ CSV, FAIL = lớp dương).

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | **Đạt** (tp 24, fp 4, fn 6, tn 66) | **dùng**, chỉ cho giọng văn, không chặn release một mình |
| helpful | 100 | 0.375 | 1.000 | 0.300 | **Không đạt** (κ và R dưới sàn; tp 9, fp 0, fn 21, tn 70) | **loại**, không được làm gate |

Tỉ lệ lỗi hiệu chỉnh Rogan-Gladen: tone quan sát 0.28 → 0.30; helpful quan sát 0.09 → 0.30. Judge helpful báo tỉ lệ lỗi chỉ bằng **1/3** thực tế.

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 1 | H-008 "Em đã hoàn tiền cho anh rồi nha…" | PASS | FAIL | Người | Xưng "em" + "nha" quá suồng sã. Rubric: thêm luật xưng hô cứng (LogiX ↔ anh/chị), "nha/nhé" ⇒ FAIL. |
| 2 | H-017 "Dạ, bạn ơi LogiX đã hoàn 25.000đ…" | PASS | FAIL | Người | Gọi khách là "bạn". Rubric: liệt kê đại từ được phép; judge đang coi "thân thiện" = lịch sự. |
| 3 | H-029 "Dạ, vui lòng chờ… không cần nhắn thêm." | PASS | FAIL | Người | Giọng ra lệnh nằm sau từ lịch sự. Rubric: đánh giá cả câu, có ví dụ âm về mệnh lệnh ("không cần…", "phải…"). |
| 4 | H-042 "Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ." | FAIL | PASS | Người | Judge phạt vì "thiếu xin lỗi". Rubric: xin lỗi **không bắt buộc** khi đã giải quyết xong; ngắn nhưng đủ ý = PASS. |
| 5 | H-051 "Dạ, LogiX đã refund 90.000đ…" | FAIL | PASS | Người | CS LogiX cho phép "refund". Rubric: thêm whitelist thuật ngữ tiếng Anh được phép. |
| 6 | HL-015 "đã hoàn 55.000đ cho đơn O-112" (ledger 40.000đ) | PASS | FAIL | Người | Judge helpful không thấy ledger nên không thể biết sai tiền. **Không sửa được bằng rubric**: chuyển sang grader code `reply_matches_ledger` (FM-08). |
| 7 | HL-016 xin lỗi dài + "đã hoàn 55.000đ" (ledger 35.000đ) | PASS | FAIL | Người | Văn bản dài, nhiều câu xin lỗi được judge thưởng điểm, che mất số sai (thiên lệch độ dài). |
| 8 | HL-020 "đã hoàn 90.000đ cho đơn O-303" (ledger 120.000đ) | PASS | FAIL | Người | Như #6. |

## Kết luận
- **tone_ok dùng được**: qua cả 3 sàn; 10 bất đồng chủ yếu là luật xưng hô/từ vựng mà rubric chưa nói rõ, sửa rubric như trên rồi đo lại trên tập nhãn mới.
- **helpful bị loại**: R = 0.30, tức là judge bỏ sót 21/30 reply người chấm FAIL. Cả **18/18** reply "sai tiền" đều bị judge cho PASS (3 lỗi bỏ sót còn lại là "sai xưng hô"). P = 1.0 không cứu được judge này: nó chỉ chắc chắn khi lỗi quá rõ (lạc đề, giọng cụt). Dùng nó làm gate thì một bản agent báo sai tiền vẫn có thể merge. Đúng nguyên tắc của bài: **tiền chấm bằng code**. Phần "sai tiền" thuộc FM-08, đã có metric `reply_matches_ledger` đọc ledger. Cũng không lấy κ hay P đơn lẻ để kết luận, phải nhìn cả ma trận nhầm lẫn.
- Rủi ro còn lại: judge chỉ được kiểm trên dữ liệu replay đã công khai, và rubric sửa xong chưa được đo lại; cần nhãn người mới để có held-out thật.
