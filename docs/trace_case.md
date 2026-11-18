# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

## Case: `seeded_regression` C-002@11 (Hoàng Thị Thanh Nga, 2A202604079)

Trace đọc được:
```
== seeded_regression C-002@11  lab8 grader: FAIL (status resolved != denied)
   1 handoff            {"request_id": "REQ-C-002", "allowed_tools": ["lookup_order", "lookup_policy", "compute_compensation"], ...
   2 investigator       {"lookup_order": {"visible": true, "reason": "ok", "order": {"order_id": "O-202", "status": "delivered", ...
   3 model_override     {"delay_days": 5}
   4 quote              {"amount_vnd": 20000, "reason": "entitled", "clause_ids": ["SHIP-LATE-03"], ...}
   5 refund_history     {"refund_count": 0, "refunded_vnd": 0}
   6 reply              {"text": "Dạ, LogiX đã hoàn 20.000đ cho đơn O-202."}
  refund_vnd     ledger=20000    label=0   <-- differs
  refund_count   ledger=1        label=0   <-- differs
  status         result=resolved label=denied
```

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, run `E-seeded_regression-20261118-4811` (`src/reports/eval_seeded_regression.json`) |
| Triệu chứng | `pass_rate`, `refund_amount_correct`, `db_fact_kept` đều fail. Reply "đã hoàn 20.000đ", ledger ghi đúng 20.000đ, nhưng nhãn là `denied` / refund 0: đơn O-202 trong DB chưa đủ số ngày trễ để được hoàn. Reply và ledger khớp nhau, nên lỗi không nằm ở FM-08 mà nằm ở quyết định. |
| Bước sai đầu tiên | Event **3** `model_override` · `{"delay_days": 5}`: số ngày trễ "5 ngày" trong ticket đè lên `delay_days` của DB. |
| Vì sao là bước *đầu tiên* | Event 1 (`handoff`) đúng allowlist tool. Event 2 (`investigator`) đọc đúng O-202 từ DB (đơn `delivered`, ít ngày trễ, `visible: true`). Mọi thứ sau event 3 là hệ quả: event 4 `quote` tính lại trên số ngày giả (20.000đ, SHIP-LATE-03), sau đó host ghi refund. |
| Failure mode | **FM-03** ticket_trust (layer model/prompt) |
| Đối chứng | `fixed C-002@11`: event 1–2 giống hệt, **không có** `model_override`; event 3 `quote {"amount_vnd": 0, "reason": "no_entitlement"}`, reply "chưa đủ điều kiện hoàn", ledger 0, Lab 8 grader PASS. |
| Regression test | `src/tests/test_lab9_trace_case.py`: `test_lab9_trace_case_c002_buggy_variant_overrides_db` khẳng định trên `seeded_regression` event đầu tiên khác handoff/investigator là `model_override {"delay_days": 5}`, ledger 20.000đ, `DbFactKept` và `RefundAmountCorrect` fail. `test_lab9_trace_case_c002_fixed_keeps_db_fact` khẳng định `fixed` không override, ledger 0, cả hai grader pass. Đã chạy: cả hai test PASS (tức là bắt được lỗi ở variant lỗi và không báo nhầm trên `fixed`). Item E-002 cũng ghi `provenance.from_trace`. |
| Chưa chắc chắn | Trace không cho biết *vì sao* model chọn tin ticket (MockLLM quyết định theo công tắc `ticket_trust`, với swarm gốc là seed % 5 == 0). Với LLM thật, cùng triệu chứng có thể do prompt, nên regression test này bắt *hành vi* (override dữ kiện DB), không bắt nguyên nhân. Lỗi không im lặng: `quiet_override` cũng sai tiền như vậy nhưng không ghi event, chỉ `refund_amount_correct` bắt được, `db_fact_kept` thì không. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
