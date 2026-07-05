# verified-intent-ir — v1 Deterministic Core (Design Spec)

**Date:** 2026-07-05
**Status:** Approved architecture; pending user review of this spec
**Scope of this document:** The first buildable slice — the deterministic core.
Live LLM generation, confidence-signal collection, and the full research
harness are deferred to later slices and named explicitly below.

> The artifact is built to answer one question at a time instead of assuming an
> answer up front.

This spec implements the mission from the project brief. It does **not** restate
the brief's philosophy (mission, non-goals, kill criteria, prior art) except
where a design decision depends on it. Those sections of the brief remain
authoritative and are referenced by name.

---

## 1. What this slice is (and isn't)

**Is:** an in-memory IR object model, its JSON serializer, a three-stage
validation pipeline (structural → semantic → contract), a hand-proven contract
table, a thin execution-plan layer, a dumb IR→Python compiler, a runner, a
per-IR statistics module, and a SQLite logger — all exercised end-to-end on
**human-authored** IR programs, with generation present only as a stubbed seam.

**Is not (deferred, on purpose):**

- Live LLM generation / grammar-constrained decoding (`gen` is a stub returning fixtures)
- Confidence-signal collection and calibration scoring
- Semantic edit distance
- The full 40-task adversarial set (a seed subset ships now)
- Any optimizer, algorithm selection, or plan rewrite (permanent v1 non-goal)
- YAML/binary serializers (seam exists; code does not)

**Deferred is not vague.** Each deferred item has a named seam in the
architecture so it plugs in without reshaping the core.

---

## 2. Guiding separations

These four separations are load-bearing. Every module boundary below traces to
one of them.

1. **Representation vs. serialization.** The IR is an object model. JSON is one
   serializer among future others. Nothing downstream of the model depends on
   JSON.
2. **Syntax vs. semantics.** Structural validity (shape) is checked separately
   from semantic validity (dataflow, field coherence). A structurally valid IR
   can still be semantically nonsense.
3. **Validation vs. verification.** Validation asks "is this a well-formed
   program?" Verification asks "are the *claims* it makes about itself true?"
   Different stages, different failure messages.
4. **Artifact vs. contribution.** This spec builds the artifact (Track A). It
   produces no contribution by itself. Finishing it is not the goal; it is the
   instrument that later measures something worth reporting.

---

## 3. Architecture

Every stage is replaceable behind an interface. Data flows one direction.

```
        Fixtures (human-authored IR)
              │
   generate_ir(prompt)  ← stubbed seam; fixture now, model later
              │
              ▼
        ┌─────────────────────┐
        │   IR Object Model   │   (dataclasses; the semantic object)
        └─────────────────────┘
              │        ▲
   JsonSerializer.parse│ JsonSerializer.emit   (serialization is a seam)
              ▼        │
        ┌─────────────────────┐
        │ Structural Validator│   stage 1 — JSON Schema, shape only
        └─────────────────────┘
              │
        ┌─────────────────────┐
        │  Semantic Validator │   stage 2 — dataflow + op-field coherence
        └─────────────────────┘
              │
        ┌─────────────────────┐
        │  Contract Verifier  │   stage 3 — claim discharge vs contract table
        └─────────────────────┘
              │
        ┌─────────────────────┐
        │  Execution Planner  │   thin; IR → typed plan nodes (no optimization)
        └─────────────────────┘
              │
        ┌─────────────────────┐
        │      Compiler       │   plan → Python source (dumb, 1:1)
        └─────────────────────┘
              │
        ┌─────────────────────┐
        │       Runner        │   execute source on input data → result/error
        └─────────────────────┘
              │
        ┌─────────────────────┐
        │       Logger        │   SQLite; one row per run
        └─────────────────────┘

   IR Statistics module observes the object model out-of-band and feeds the log.
```

**Logging order.** A row is opened at the moment an IR enters the pipeline
(before structural validation) and updated with the outcome. Never lose a
generation to a later crash.

---

## 4. The IR object model

Python dataclasses. A pipeline is a **flat list** of operation nodes plus
top-level `claims` and `hints`. Dataflow is expressed by named `input`/`output`
variables, allowing a DAG while keeping the JSON shape shallow.

### 4.0 Why these six primitives

> The six primitives (`map`, `filter`, `sort`, `reduce`, `groupby`, `take`) are
> selected as a minimal closed set sufficient to express common
> collection-processing pipelines. **They are a design hypothesis, not a claim of
> optimality.** The experiments are what test the hypothesis; the set is expected
> to move.

Candidates deliberately **excluded from v1**, and why:

- `join`, `zip` — binary (two-input) ops; break the single-`input` node shape and
  complicate the dataflow model. Revisit once the unary set is proven.
- `distinct`, `partition` — expressible/adjacent to `filter`+`groupby` for now;
  excluded under YAGNI until a task needs them.
- `flatten`, `window` — introduce shape/arity changes (nesting, sliding state)
  that the flat closed-expression model doesn't yet cover.

Each is a candidate for a later slice, added only when a real task forces it —
and each addition is a `DECISIONS.md` entry, not a silent expansion.

```
Pipeline
  ir_version: int            # = 1
  contract_version: int      # = 1  (see §7)
  ops: list[Op]
  claims: Claims
  hints: Hints               # opaque to verification; never trusted

Op = Filter | Map | Sort | Reduce | GroupBy | Take
  each Op has: input: str, output: str    # variable names
```

A variable that is never any op's `output` is a **source** (supplied at runtime,
e.g. `"users"`). Semantic validation enforces define-before-use.

### 4.1 Closed expression grammar (shared)

To keep the vocabulary genuinely closed — the whole justification for provable
ground truth — `map` and `filter` share one tiny scalar-expression grammar. No
user lambdas, ever (that reintroduces Rice's-theorem undecidability).

```
Expr = Const(value)
     | Field(name)
     | BinOp(op ∈ {add, sub, mul, div}, left: Expr, right: Expr)

Condition = Compare(field: str, cmp ∈ {gt, lt, gte, lte, eq, neq}, value: Expr)
```

Boolean combinators (`and`/`or`) are **not** in v1 (YAGNI; single comparison per
filter). Extension point noted, not built.

### 4.2 Per-operation fields

| Op | Fields | Semantics |
|---|---|---|
| `filter` | `condition: Condition` | keep elements where condition holds |
| `map` | `assign: str`, `expr: Expr` | set one field per element from Expr |
| `sort` | `key: str`, `descending: bool=false` | order by key (always stable in v1 — see §7) |
| `reduce` | `reducer ∈ {sum,product,min,max,count}`, `field: str?`, `init?` | fold to scalar |
| `groupby` | `key: str` | hash-group into `{key → list}` |
| `take` | `count: int` | first `count` elements |

`groupby` output is a mapping; ops consuming grouped data are limited in v1 and
this limit is documented rather than papered over. `reduce`'s `field` is required
for `sum/product/min/max`, ignored for `count`.

### 4.3 Claims vs. hints (from the brief — restated because it is load-bearing)

- **Hints** (`suggested_algorithm`, access pattern): safe to be wrong; worst case
  is a missed optimization. **Never consulted by the verifier.**
- **Claims** (`complexity`, `stable`, plus inert `mutates`/`aliasing`): checked
  against the contract table before being trusted.

**v1 scoring caveat (from brief):** all six primitives are pure/non-mutating by
construction, so `mutates` and `aliasing` have zero variance and are **not
scored**. Only `complexity` and `stable` carry signal in v1.

---

## 5. Serialization layer

```
Serializer (interface)
  parse(text: str) -> Pipeline
  emit(pipeline: Pipeline) -> str

JsonSerializer implements Serializer     # the only implementation in v1
```

Round-trip property (tested): `parse(emit(p)) == p` for every fixture. The
generation seam speaks to the model in the serialized wire format; the rest of
the system speaks in `Pipeline` objects. **Nothing except the serializer imports
`json`.**

---

## 6. Three-stage validation

Three ordered stages, each a pure function returning a typed result. Later stages
assume earlier ones passed.

### Stage 1 — Structural (`validate/structural.py`)
JSON Schema (`schema/ir.schema.json`) checks **shape only**: known op names,
required fields present, field types, flat-array pipeline. Scoped deliberately
narrow — it is *not* asked to enforce semantics. Its known limitation (over-
permissiveness, e.g. a `sort` carrying a stray `count`) is the reason stage 2
exists.

### Stage 2 — Semantic (`validate/semantic.py`)
- **Dataflow:** every `input` is a source or an earlier `output`; no use-before-
  define; no dangling outputs referenced by nothing except as final result.
- **Op-field coherence:** each op carries exactly its allowed fields and no
  foreign ones (catches `{"op":"sort","count":10}` — wrong field, missing `key`).
- **Field references:** `Field(name)` / `key` / `assign` reference plausible
  fields (v1: non-empty strings; schema-of-data checking is deferred).

### Stage 3 — Contract (`verify/check_claims.py`)
Claim discharge against the contract table (§7). Emits a **structured
`Explanation`** (§6.1), not a string. Every stage does — see below.

### 6.1 Structured explanations (`explain/`)

Every rejection (and every accept) from all three stages is a structured object,
**generated first**; human text is *rendered* from it, never the other way round.
This exists for the experiments, not for users: it lets us aggregate "which rule
fires, how often, on what evidence" across thousands of runs — impossible with
free text.

```
Explanation
  stage:      "structural" | "semantic" | "contract"
  outcome:    "ok" | "rejected"
  rule:       str        # stable identifier, e.g. "SORT_IMPLIES_NLOGN"
  evidence:   list[str]  # e.g. ["sort"]  — the ops/fields that fired the rule
  declared:   str?       # what the IR claimed (e.g. "O(n)")
  derived:    str?       # what the contracts entail (e.g. "O(n log n)")
  suggestion: str?       # smallest fix
```

`explain/render.py` turns that into the brief's exact text format:

```
Claim rejected: complexity
Declared: O(n)
Derived:  O(n log n)   (pipeline contains SORT)
Smallest fix: update complexity claim, or remove SORT
```

The structured `Explanation` is what gets logged (§12); the rendered string is a
display convenience.

---

## 7. Primitive contracts (hand-proven once) + versioning

`verify/contracts.py` holds the table. It is tagged `contract_version` (starts at
`1`), logged with every run so experiments stay reproducible when a contract's
model later improves.

**Framing.** Because the vocabulary is closed, the verifier is not doing program
*analysis* — it is a **small theorem checker over a finite algebra**. Claim
discharge is pattern-matching against a fixed table plus the composition rule
below, not SMT solving and not inference. Complexity composition is literally an
algebra (a max-semilattice over three ordered elements), which is why it is
decidable and cheap. This is the property that makes ground truth knowable for
certain; it is also exactly what evaporates the moment the vocabulary opens up.

| Primitive | Time | Mutates | Notes |
|---|---|---|---|
| `filter` | O(n) | No | |
| `map` | O(n) | No | |
| `sort` | O(n log n) | No | stable (Python `sorted`) |
| `reduce` | O(n) | No | |
| `groupby` | O(n) | No | hash-based |
| `take` | O(k) | No | dominated by upstream |

**Complexity composition** = the maximum order among composed ops, under the
ordering `O(k) < O(n) < O(n log n)`. A single `sort` anywhere ⇒ whole pipeline
`O(n log n)`. `filter`+`take` ⇒ `O(n)` (filter dominates). `take` alone ⇒ `O(k)`.
This is trivial *only because* the vocabulary is closed — it is not a general
resource-analysis engine (contrast RaML, which fails on merge-sort variants;
that failure is exactly why contracts are hand-specified, not inferred).

**`stable` discharge:** `stable` is a **top-level claim only** in v1 (there is no
per-op stable flag, because Python `sorted` is unconditionally stable and the
dumb compiler cannot emit an unstable sort). A `stable: true` claim on a pipeline
containing a sort is honest; `stable: false` contradicts the compiler and is
rejected. The research value is whether a *model* declares `stable` correctly —
which the tied-sort adversarial tasks probe. A per-op stable flag becomes
meaningful only once an unstable/faster sort backend exists; deferred until then.

---

## 8. Execution plan layer (thin; on probation)

`plan/execution_plan.py` lowers a validated `Pipeline` into an ordered list of
typed plan nodes:

```
filter → sort → take    lowers to    Scan(src) → Predicate(...) → Sort(...) → Limit(...)
```

**Guardrails (explicit):**
- One plan node per primitive. **Zero optimization passes.** The no-optimizer
  non-goal is intact.
- Rationale for existing now: it is the seam for future multi-target backends
  (SQL/Pandas/Spark), visualization, and the "estimated execution stages" stat.
- **Probation clause:** if this layer never diverges from a 1:1 rename of the IR,
  it is a deletion candidate under kill-criterion #5 (growing the machinery
  without catching proportionally more). Revisit at the first backend or the
  first optimization — whichever comes first.

---

## 9. Compiler

`compiler/plan_to_python.py`: `ExecutionPlan → Python source string`. Dumb, 1:1,
stdlib only. Each plan node emits one statement:

- `Predicate` → list comprehension
- `Map` → list comprehension assigning a field
- `Sort` → `sorted(..., key=..., reverse=...)`
- `Reduce` → `functools.reduce` / `sum` / `min` / `max` / `len`
- `GroupBy` → dict accumulation
- `Limit` → slice `[:k]`

No fusion, no reordering, no algorithm choice. The generated source is meant to
be *boringly* readable — that readability is itself a Track-C measurement later.

---

## 10. Runner

`runner/run.py`: executes compiled source against supplied input data in a
constrained namespace, captures the final output variable or the exception →
`(passed: bool, result | error)`. v1 uses in-process `exec` with a restricted
globals dict; sandboxing hardening is deferred (fixtures are trusted, human-
authored).

---

## 11. IR statistics

`stats/ir_stats.py`: pure `(Pipeline) → dict`, computed on every IR, logged even
when never queried. Fields: `primitive_count`, `pipeline_depth`, `claim_count`,
`hint_count`, `derived_complexity`, `estimated_stages`, per-primitive counts.
The point is to already have the data when a question like "do all failed
generations have >6 primitives?" appears.

---

## 12. Logging

`log/store.py`: SQLite, one row per run, opened before stage 1 and updated with
the outcome. Columns:

```
id, ts,
prompt,               -- null for hand-authored fixtures
raw_ir,               -- serialized wire form as received
claims, hints,        -- serialized
confidence_signal,    -- null in v1 (seam for later)
ir_version, contract_version,
stats,                -- serialized §11 output
compiled_python,      -- null if failed before compile
stage_reached,        -- structural | semantic | contract | plan | compile | run
explanation,          -- serialized structured Explanation (§6.1); rule/evidence queryable
passed                -- bool
```

The `explanation` column stores the **structured** object, not rendered text, so
runs are queryable by `rule` and `evidence` (e.g. "count runs where
`rule = SORT_IMPLIES_NLOGN`"). Text is rendered on read when a human looks.

Never re-run a model to answer a question you didn't think to ask: the log is the
permanent record; models and prompts drift, rows don't.

---

## 13. Generation seam (stubbed)

`gen/generate.py` exposes `generate_ir(prompt: str) -> str` (returns wire-format
IR). v1 implementation: a fixture loader keyed by prompt/id. Later slice swaps in
grammar-constrained decoding against a real model — same signature, same
downstream. **Hard gate:** the language must be frozen by the human corpus (§14)
before this seam is connected to any model.

---

## 14. Fixture corpus

`fixtures/` holds **human-authored** IR programs. This is deliberate: an IR that
evolves only from generated examples becomes Python-shaped, because the model is
biased toward Python. Humans define the language first.

- **Now (core build):** a seed set (~15–20) covering all six primitives, the
  shared expression grammar, and the three adversarial categories, sufficient to
  drive TDD of every module.
- **Gate on the generation slice — a *coverage matrix*, not a raw count.** The
  language is frozen (and only then is `generate_ir` wired to a model) when the
  human-authored corpus satisfies a checkable matrix:
  - every primitive appears in ≥ K distinct programs,
  - every expression-grammar construct (each `BinOp`, each comparator) appears,
  - every adversarial category (ties, complexity-traps, edge cases) appears,
  - each claim type that carries v1 signal (`complexity`, `stable`) appears both
    honestly-declared and mis-declared.

  The count is whatever satisfies that matrix (expected to land near ~100, but the
  matrix is the gate, not the number). Rationale for making this a matrix: a bare
  count is arbitrary and "a sufficiently diverse corpus" is unfalsifiable — either
  would let the gate be declared passed at a convenient moment, which is precisely
  the failure mode the project's explicit-gates discipline exists to prevent. A
  coverage matrix is *checkable* and preserves the real intent (diversity, humans
  define the language first). **Not a gate on writing core code.**

`tasks/adversarial/` seeds now with at least: one tied-sort (probes `stable`
honesty), one complexity-trap (looks like it needs a sort but doesn't, and the
reverse), one empty-pipeline / trivial-reduce edge case. Grows toward the
brief's ~40.

`failed_ideas/` is created now and used continuously — archived, never deleted.

---

## 15. Testing strategy

TDD throughout; the verifier, compiler, validators, planner, and stats modules
are pure functions and highly testable.

- **Golden tests:** fixture IR → expected plan → expected Python → expected
  output on sample data.
- **Round-trip:** `parse(emit(p)) == p` for every fixture.
- **Adversarial / rejection:** malformed and mis-claimed IR produce the exact
  stage and message expected (e.g. sort + `O(n)` → the §6 rejection block;
  `{"op":"sort","count":10}` → stage-2 op-field-coherence failure, not a stage-1
  pass).
- **Composition:** complexity derivation across multi-op pipelines matches §7.

---

## 16. Dependencies

- `jsonschema` — stage 1 only (structural). Justified: the schema doubles as the
  future grammar-constrained-decoding grammar, so it is a first-class validated
  artifact, not hand-rolled string checks.
- Everything else: Python 3 stdlib (`dataclasses`, `functools`, `itertools`,
  `sqlite3`, `json`).

---

## 17. Module layout

```
schema/ir.schema.json          — structural grammar (stage 1)
ir/model.py                    — dataclasses: Pipeline, ops, Expr, Condition, Claims, Hints
ir/serialize.py                — Serializer interface + JsonSerializer
validate/structural.py         — stage 1
validate/semantic.py           — stage 2 (dataflow + op-field coherence)
verify/contracts.py            — contract table + contract_version + composition rule
verify/check_claims.py         — stage 3 (claim discharge → structured Explanation)
explain/explanation.py         — structured Explanation type (stage/rule/evidence/…)
explain/render.py              — Explanation → human text (brief's exact format)
plan/execution_plan.py         — IR → thin typed plan
compiler/plan_to_python.py     — plan → Python
runner/run.py                  — execute compiled source
stats/ir_stats.py              — per-IR statistics
log/store.py                   — SQLite logging
gen/generate.py                — generation seam (stub → fixture loader)
fixtures/                      — human-authored IR corpus (coverage-matrix gate, §14)
tasks/adversarial/             — adversarial task set (seed subset)
failed_ideas/                  — archived, not deleted
tests/                         — TDD suite
```

---

## 18. Non-goals & kill criteria

Carried verbatim in force from the project brief. Two that this spec touches
directly:

- **Kill criterion #5** (no growth without proportional catch) governs the
  execution-plan layer's probation (§8) and the "keep the verifier simple" line.
- **Non-goal: no optimizer** is enforced by §8's zero-pass guardrail and §9's
  dumb compiler.

The generation-dependent kill criteria (#1 claim reliability vs. Python, #3
calibration vs. the naive `sort`-heuristic) cannot be evaluated in this slice —
they require the generation slice and are not smuggled forward.

---

## 19. Decisions resolved in this spec

1. `map` assigns one field via the closed expression grammar (§4.1); no lambdas.
2. `reduce` uses a closed reducer set `{sum,product,min,max,count}`.
3. Dataflow via named `input`/`output` vars in a flat list; define-before-use.
4. `jsonschema` kept, scoped to structural validation only.
5. IR is an object model; JSON is one serializer (§5).
6. Validation split into three named stages (§6).
7. Execution-plan layer added, thin, no optimizer, on probation vs. kill-crit #5.
8. IR statistics computed and logged on every run (§11).
9. `contract_version` logged alongside `ir_version` (§7, §12).
10. Corpus gate on the *generation* slice is a checkable coverage matrix, not a
    raw count and not "sufficiently diverse" (§14). Not a gate on the core build.
11. The six primitives are stated as a design hypothesis, with excluded
    candidates named (§4.0).
12. `explain/` module: all stages emit structured `Explanation` objects; text is
    rendered from them, and the structured form is what's logged (§6.1, §12).

Every entry here is also recorded in `DECISIONS.md` (ADR-style) so the reasoning
survives when the code no longer makes it obvious.

---

## 20. Future directions (explicitly NOT v1)

Recorded so they are not forgotten and not smuggled into v1:

- **Bidirectional compilation** (`Python → IR → Python`). Enables comparing human
  Python, generated IR, and regenerated Python — a genuinely interesting
  experiment on round-trip semantic fidelity. Requires a Python→IR frontend that
  does not exist and is out of scope until the forward path is proven.
- Additional primitives (`join`, `distinct`, `flatten`, `zip`, `window`,
  `partition`) — added only when a real task forces one, each as a `DECISIONS.md`
  entry (§4.0).
- Live grammar-constrained generation, confidence-signal collection, calibration
  scoring, semantic edit distance — the research harness that consumes this
  artifact (§1).
