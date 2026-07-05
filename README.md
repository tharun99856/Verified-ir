# verified-intent-ir

An AI-native intermediate representation that lets language models express
intent explicitly, compiles reliably to Python, and is instrumented from day
one to study the reliability of machine-generated semantic information.

This is **not** a new programming language, and it is not trying to beat
Python. It is a small, closed, JSON-serializable IR plus a verifier and
logging harness.

## Why

LLMs are good at producing plausible-looking code and bad at knowing whether
their own claims about that code (its complexity, whether it mutates input,
whether a sort is stable) are actually true. This project asks: if you force
the model to express *intent* in a small, closed, provable vocabulary instead
of arbitrary Python, can those claims be checked cheaply — and are they any
good?

The **artifact** (IR, compiler, verifier, logger) and the **contribution**
(what running experiments on that artifact reveals) are kept deliberately
separate. Finishing the artifact does not by itself produce a result.

## The IR: six primitives, closed vocabulary

```
map, filter, sort, reduce, groupby, take
```

Nothing else in v1. A pipeline is a flat array of operations connected by
named `input`/`output` variables — not deeply nested JSON, since depth
tracking is a known source of structural errors in LLM generation.

```json
{
  "ir_version": 1,
  "contract_version": 1,
  "ops": [
    {"op": "filter", "input": "users", "condition": {"field": "age", "cmp": "gt", "value": 18}, "output": "adults"},
    {"op": "sort",   "input": "adults", "key": "score", "descending": true, "output": "sorted"},
    {"op": "take",   "input": "sorted", "count": 10, "output": "top10"}
  ],
  "claims": {"complexity": "O(n log n)", "stable": true},
  "hints": {"suggested_algorithm": "partial_sort"}
}
```

Each primitive has a hand-proven contract (time complexity, mutation
behavior) — see the design spec for the full table and the composition rule.

**Hints vs. claims** — never conflated: hints (suggested algorithm, access
pattern) are safe to be wrong; claims (complexity, stability) are checked
against the contract table before being trusted for anything.

## Architecture

```
Fixtures (human-authored IR)
        │
generate_ir(prompt)   ← stubbed seam; fixture now, model later
        │
        ▼
   IR Object Model
        │
 Structural Validator   (shape only)
        │
  Semantic Validator     (dataflow + op-field coherence)
        │
  Contract Verifier      (claim discharge vs. hand-proven contracts)
        │
  Execution Planner      (thin; one node per primitive, no optimization)
        │
      Compiler           (plan → Python, dumb, 1:1)
        │
       Runner            (execute, capture result/error)
        │
       Logger            (SQLite; one row per run, before anything else)
```

Every stage is a pure function with a single responsibility, replaceable
without touching its neighbors. Full rationale for each separation is in the
design spec.

## Status

Pre-implementation. The deterministic core (everything above the generation
seam) is being built now, phase by phase, against hand-authored fixtures.
Live LLM generation is deferred until the fixture corpus satisfies a coverage
matrix (every primitive, every expression construct, every adversarial
category) — see `DECISIONS.md`.

## Documentation

- [`docs/superpowers/specs/2026-07-05-verified-intent-ir-design.md`](docs/superpowers/specs/2026-07-05-verified-intent-ir-design.md) —
  full design spec for the v1 deterministic core.
- [`DECISIONS.md`](DECISIONS.md) — ADR-style log of accepted decisions and
  rejected alternatives, with revisit conditions and maintenance-cost tags.

## Non-goals (v1)

No LLVM/native codegen, no new type system, no borrow checker, no optimizer
(no algorithm selection, no fusion — direct 1:1 translation only), no
primitives beyond the six above. See `DECISIONS.md` for what was
specifically considered and rejected, and why.

## License

MIT — see [`LICENSE`](LICENSE).
