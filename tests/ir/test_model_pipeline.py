from ir.model import Claims, Hints, Pipeline, Take


def test_pipeline_holds_versions_ops_claims_and_hints():
    take = Take(input="users", output="top10", count=10)
    claims = Claims(complexity="O(k)", stable=False)
    hints = Hints()

    pipeline = Pipeline(
        ir_version=1,
        contract_version=1,
        ops=[take],
        claims=claims,
        hints=hints,
    )

    assert pipeline.ir_version == 1
    assert pipeline.contract_version == 1
    assert pipeline.ops == [take]
    assert pipeline.claims == claims
    assert pipeline.hints == hints
