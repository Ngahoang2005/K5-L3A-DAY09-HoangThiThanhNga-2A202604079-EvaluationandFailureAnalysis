"""Regression test for docs/trace_case.md: seeded_regression C-002@11.

First wrong step = event 3 `model_override {"delay_days": 5}`: the ticket's "5 ngày" overrides
the DB delay, so a claim the policy denies gets a 20.000đ refund (FM-03 ticket_trust).
The test must FAIL the buggy variant and PASS `fixed` on the same claim@seed.
"""
import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.student


def _trial(shape: str, tmp_path: Path, claim_id: str = "C-002", seed: int = 11) -> dict:
    from lab9 import eval as ev
    from lab9 import variants

    variants.register()
    spec = ev.load_spec(ev.SPEC)
    labels = json.loads(Path(spec["labels"]).read_text(encoding="utf-8"))
    world, claims = ev.load_world(spec)
    return ev.make_task(shape, world, claims, labels, tmp_path)({"claim_id": claim_id, "seed": seed})


def _graded(trial: dict) -> dict[str, bool]:
    from pydantic_evals.evaluators import EvaluatorContext

    from lab9.graders import DbFactKept, RefundAmountCorrect

    label = json.loads(Path("data/eval/labels_v1.json").read_text(encoding="utf-8"))["C-002"]
    ctx = EvaluatorContext(name="C-002@11", inputs={}, metadata=None, expected_output=label, output=trial,
                           duration=0.0, _span_tree=None, attributes={}, metrics={})
    return {"db_fact_kept": DbFactKept().evaluate(ctx).value,
            "refund_amount_correct": RefundAmountCorrect().evaluate(ctx).value}


def test_lab9_trace_case_c002_buggy_variant_overrides_db(tmp_path):
    trial = _trial("seeded_regression", tmp_path)
    kinds = [e["kind"] for e in trial["events"]]
    first_override = kinds.index("model_override")
    assert kinds[:first_override] == ["handoff", "investigator"]      # steps before it are clean
    assert trial["events"][first_override]["payload"] == {"delay_days": 5}
    assert trial["snapshot"]["refund_vnd"] == 20000
    assert _graded(trial) == {"db_fact_kept": False, "refund_amount_correct": False}


def test_lab9_trace_case_c002_fixed_keeps_db_fact(tmp_path):
    trial = _trial("fixed", tmp_path)
    assert "model_override" not in [e["kind"] for e in trial["events"]]
    assert trial["snapshot"]["refund_vnd"] == 0
    assert _graded(trial) == {"db_fact_kept": True, "refund_amount_correct": True}
