# DECISIONS

An append-only log of significant decisions (ADR-style). The point is that six
months from now the reasoning is recoverable without re-deriving it — often more
valuable than code comments. This log records not just what the project **became**
but what it deliberately **refused to become** (see *Rejected Alternatives*).

Every entry carries:

- **Category** — `Architecture` | `Research` | `Build Process` (filterable)
- **Status** — `Accepted` | `Rejected` | `Superseded`
- **Revisit** — a condition that should trigger reconsideration, or `Permanent`.
  Distinguishes temporary decisions from load-bearing ones.
- **Maintenance Cost** — `Low` | `Medium` | `High`, meaning *long-term
  maintenance* cost, not implementation cost. Helps future-you decide what to
  delete.

Newest at the top within each section. See also:
`docs/superpowers/specs/2026-07-05-verified-intent-ir-design.md`.

---

# Decisions

## 2026-07-05 — Research questions must emerge from artifacts

**Category:** Research
**Status:** Accepted
**Revisit:** Permanent (governing principle)
**Maintenance Cost:** Low — it is a constraint, not machinery.

**Decision:** Do not introduce a research hypothesis that requires new
infrastructure before existing infrastructure has produced data.

**Reason:** The project optimizes for empirical discovery rather than speculative
novelty. It started as an attempt to invent a language; it became a system
designed to discover what is worth researching. This ADR is the one-sentence form
of that shift.

**Trade-offs:** Some ideas wait longer to be evaluated. In exchange, premature
scope expansion is structurally discouraged.

---

## 2026-07-05 — Corpus gate is a coverage matrix, not a count or an adjective

**Category:** Build Process
**Status:** Accepted
**Revisit:** Before wiring `generate_ir` to a model (evaluate the matrix then).
**Maintenance Cost:** Low — maintaining a coverage checklist.

**Decision:** The gate that freezes the IR language before generation is wired up
is a *checkable coverage matrix* (every primitive, every expression construct,
every adversarial category, honest + mis-declared claims), not "100 fixtures" and
not "a sufficiently diverse corpus."

**Alternatives:**
- Raw count ("100 human-authored programs").
- "A sufficiently diverse human-authored corpus."

**Reason:** A raw count is arbitrary; "sufficiently diverse" is unfalsifiable and
can be declared satisfied at any convenient moment — the exact failure mode the
project's explicit-gates discipline exists to prevent. A coverage matrix is
checkable and preserves the real intent (humans define the language first).

**Trade-offs:** Slightly more bookkeeping. Count is no longer a single memorable
number (expected ~100, derived from coverage).

---

## 2026-07-05 — `explain/` module: structured explanations, not text-first

**Category:** Architecture
**Status:** Accepted
**Revisit:** If aggregate analysis never queries `rule`/`evidence` in practice.
**Maintenance Cost:** Low — one small type plus a render step.

**Decision:** All three validation stages emit a structured `Explanation` (stage,
rule, evidence, declared, derived, suggestion). Human text is *rendered* from it.
The structured form is what gets logged.

**Alternatives:** Emit the human-readable rejection string directly.

**Reason:** The whole project is about studying rejections/claims at scale.
Structured explanations let us aggregate "which rule fired, how often, on what
evidence" across thousands of runs — impossible with free text.

**Trade-offs:** One more module and an indirection. Negligible; same information,
structured.

---

## 2026-07-05 — Six primitives stated as a hypothesis, not optimality

**Category:** Research
**Status:** Accepted
**Revisit:** When a real task forces a new primitive (each addition = new ADR).
**Maintenance Cost:** Low — documentation framing.

**Decision:** `map, filter, sort, reduce, groupby, take` are documented as a
minimal-closed-set *design hypothesis*, with excluded candidates named (`join`,
`distinct`, `flatten`, `zip`, `window`, `partition`) and reasons.

**Alternatives:** Present the six as simply "the primitives" with no justification.

**Reason:** Unjustified, the set invites "why exactly these six?" and hides the
fact that it is expected to move. Framing it as a testable hypothesis is honest
and pre-empts the obvious reviewer question.

**Trade-offs:** None material.

---

## 2026-07-05 — Three-stage validation (structural / semantic / contract)

**Category:** Architecture
**Status:** Accepted
**Revisit:** Permanent (the separation is foundational).
**Maintenance Cost:** Low — three focused modules, each independently testable.

**Decision:** Split validation into Structural (JSON Schema, shape only) →
Semantic (dataflow + op-field coherence) → Contract (claim discharge).

**Alternatives:** Use JSON Schema as "the grammar" and let it carry semantics too.

**Reason:** JSON Schema validates structure, not semantics; a too-permissive
schema passes nonsense like `{"op":"sort","count":10}`. Separating stages makes
each cheap to reason about and gives precise, stage-specific failures.

**Trade-offs:** Three modules instead of one. `jsonschema` scoped narrowly to
stage 1 (kept because the schema doubles as the future grammar-constrained-
decoding grammar).

---

## 2026-07-05 — Execution-plan layer added (thin, no optimizer, on probation)

**Category:** Architecture
**Status:** Accepted
**Revisit:** At the first backend (SQL/Pandas/Spark) or first optimization —
whichever comes first. Deletion candidate under kill-criterion #5 if it never
diverges from a 1:1 rename of the IR.
**Maintenance Cost:** Medium — an additional abstraction requiring synchronization
with the IR.

**Decision:** Compile `IR → ExecutionPlan → Python` rather than `IR → Python`.
One plan node per primitive, zero optimization passes.

**Alternatives:**
- Compile directly from IR (simpler, no extra layer).
- Planner with optimization passes (violates the v1 no-optimizer non-goal).

**Reason:** Logical/physical separation is the seam for future multi-target
backends, visualization, and the "estimated stages" stat — the same reason
databases separate logical and physical plans.

**Trade-offs:** Extra abstraction; the highest-maintenance decision in the core,
which is why it is explicitly on probation.

---

## 2026-07-05 — IR is an object model; JSON is one serializer

**Category:** Architecture
**Status:** Accepted
**Revisit:** When a second serializer (YAML/binary/dataclass) is actually needed.
**Maintenance Cost:** Low — a thin interface with one implementation.

**Decision:** The IR is an in-memory object model (dataclasses). Serialization is
a `Serializer` interface with `JsonSerializer` as the only v1 implementation.

**Alternatives:** Treat JSON as the IR itself (LLM → JSON → verifier → compiler).

**Reason:** JSON is a transport format, not the semantic object. Decoupling means
a future YAML/MessagePack/binary/dataclass serializer changes nothing downstream.

**Trade-offs:** A thin serialization layer now. Other serializers are seams, not
built (YAGNI).

---

## 2026-07-05 — Build order: deterministic core first, generation as a stub

**Category:** Build Process
**Status:** Accepted
**Revisit:** Once the core is proven and the corpus coverage matrix is satisfied.
**Maintenance Cost:** Low — a stub honoring the real seam signature.

**Decision:** First slice is the deterministic core (schema, validators, verifier,
plan, compiler, runner, stats, logger) exercised on hand-authored IR. `generate_ir`
is a stubbed fixture loader with the signature the real model will use.

**Alternatives:**
- Build the full loop including live grammar-constrained generation first.
- Build schema + verifier only.

**Reason:** The core is fully deterministic with zero external dependencies and is
what everything else plugs into. Building live generation first front-loads
API/model/decoding infra before the thing it feeds is proven. Matches the brief's
"don't add a feature until the first surprising result appears."

**Trade-offs:** No calibration data point on day one; that waits for the
generation slice.

---

# Rejected Alternatives

Ideas seriously considered and intentionally abandoned. Recording *why* something
was rejected — not just what was chosen — is what makes architectural drift hard:
a future contributor who proposes one of these can read exactly why it was ruled
out, and whether the conditions that ruled it out still hold.

## 2026-07-05 — Rejected: General-purpose AI-native programming language

**Category:** Architecture (scope)
**Status:** Rejected
**Revisit:** Not planned. Would require abandoning the closed-vocabulary premise
that makes ground truth knowable — i.e. a different project.

**Reason:** The project originally aimed to build an AI-native programming
language. Rejected because:
- it dramatically expands scope;
- existing research already explores AI-oriented languages (Anka, AIDL, …);
- the research questions become impossible to isolate — you can no longer know
  the ground truth of a claim once general recursion is allowed (Rice's theorem).

**Replacement:** A closed, six-primitive intermediate representation.

## 2026-07-05 — Rejected: Automatic complexity inference

**Category:** Research
**Status:** Rejected
**Revisit:** If a closed-vocabulary inference method is shown decidable and cheap
for exactly the six primitives — unlikely to beat a hand table.

**Reason:** General inference quickly reaches undecidability and duplicates
existing resource-analysis research (RaML, which notably fails on merge-sort
variants). Inferring contracts would import that fragility.

**Replacement:** Hand-authored primitive contracts plus compositional checking
(a small theorem checker over a finite algebra).

## 2026-07-05 — Rejected: Trust LLM semantic claims

**Category:** Architecture
**Status:** Rejected
**Revisit:** Permanent. An unverified claim that licenses an unsafe optimization
is worse than no claim, because it fails silently (the C `restrict` failure mode).

**Reason:** Trusting model-declared semantics is unsafe. The entire premise is
that machine-generated semantic information must be checked before it is trusted.

**Replacement:** The Hints-vs-Claims split — hints are safe to be wrong, claims
are discharged against the contract table by the verifier.
