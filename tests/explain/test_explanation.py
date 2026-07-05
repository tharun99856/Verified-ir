from explain.explanation import Explanation


def test_explanation_ok_has_no_declared_derived_or_suggestion():
    exp = Explanation(stage="structural", outcome="ok", rule="OK")

    assert exp.stage == "structural"
    assert exp.outcome == "ok"
    assert exp.rule == "OK"
    assert exp.evidence == []
    assert exp.declared is None
    assert exp.derived is None
    assert exp.suggestion is None


def test_explanation_rejection_carries_evidence_and_suggestion():
    exp = Explanation(
        stage="contract",
        outcome="rejected",
        rule="SORT_IMPLIES_NLOGN",
        evidence=["sort"],
        declared="O(n)",
        derived="O(n log n)",
        suggestion="update complexity claim, or remove SORT",
    )

    assert exp.outcome == "rejected"
    assert exp.evidence == ["sort"]
    assert exp.declared == "O(n)"
    assert exp.derived == "O(n log n)"
    assert exp.suggestion == "update complexity claim, or remove SORT"
