# 38 — Redundancy and Circularity Audit

Triggered by `/r-redundancy [scope]`. Build a paragraph-level reverse outline,
find repeated propositions and circular argument chains, and propose a
preservation-first consolidation plan. The audit is read-only; similarity is a
candidate signal, never an editorial verdict.

## Boundary

- `/r-global` reports redundancy as one whole-manuscript lens.
- `/r-structure` maps all content units and their order.
- `/r-redundancy` examines what each paragraph contributes, including distant
  paraphrases, repeated framing, necessary reprises, and stalled argument
  progression.
- `scrittura` drafts accepted consolidations; `tone-of-voice` polishes prose
  only after meaning and structure are settled.
- Judge recurrence with the ordered decision model in `tone-of-voice`,
  "Repetition" (structural -> terminological -> rhetorical -> flag -> merge ->
  delete); the classification table in section 4 is its manuscript-specific
  instantiation.

Do not use this command for lexical repetition alone. Repeating the canonical
name of a technical construct is often necessary and is not evidence that the
underlying proposition is duplicated.

## 1. Establish the read-only scope

1. Resolve and state the exact manuscript file, version, and inclusive line or
   heading range. If the command omits the scope, show the resolved active file
   and its section outline, then ask for one scope before continuing.
2. Run `workflow/10-setup.md` read-only and load the existing freeze ledger
   without creating revision state. Mark frozen paragraphs in the audit.
3. Record the source checksum and its current Git status. The same bytes and
   status must remain after the audit; pre-existing changes are not an error.
4. State the scope's communicative purpose, intended reader, governing claim,
   and expected argumentative destination. Use `wayfinder`; mark a missing or
   uncertain destination instead of inventing one.

Do not create a version, task, ledger entry, report file, export, commit, or
push. Save the audit only if the user separately asks for a sidecar and approves
its exact path.

## 2. Build the reverse outline

Reuse the paragraph inventory and locator mechanics from the read-only phase of
`workflow/13-content-structure.md`. For every prose paragraph in scope, record:

- stable working ID, full locator, section path, and frozen state;
- primary function: governing claim, supporting claim, definition, evidence,
  example, bridge, implication, limitation, preview, or recap;
- one central proposition stated independently of the paragraph's wording;
- support actually added: premise, source, datum, example, condition,
  qualification, implication, or none;
- relation to the preceding paragraph and to the section's destination.

Use this table:

```text
| ID | Locator | Function | Central proposition | New support or delta | Relation forward | Citations | Frozen |
```

A paragraph with several competing central propositions is `overloaded`; a
paragraph whose proposition does not advance the section destination is
`detour`. Neither label by itself authorizes a cut.

## 3. Generate candidate pairs

The deterministic helper removes citation syntax from comparison text while
retaining citation keys as metadata. Run it through the project's configured
Python environment, resolving the script relative to this skill:

```bash
<project-python> <article-revision-root>/scripts/redundancy_candidates.py \
  <article-path> --lines <start>:<end> --backend auto
```

`auto` uses the local Ollama `/api/embed` endpoint with
`qwen3-embedding:8b` when available and reports an explicit lexical fallback
otherwise. It resolves `ARTICLE_REVISION_OLLAMA_URL`, `OLLAMA_BASE_URL`, or
`OLLAMA_HOST` from the closest project `.env` before the process environment
and localhost; this supports a Windows Ollama host called from WSL. A CLI
`--ollama-url` overrides discovery. Use `--backend lexical` for a deterministic
offline run or `--backend ollama` when semantic coverage is required and
failure should stop the audit. Do not install a model, start a service, or
change configuration as part of the audit.

The default semantic threshold is deliberately uncalibrated (`0.0`): the
helper returns the highest-ranked queue capped by `--max-pairs` instead of
silently excluding pairs with a model-specific score. Use a nonzero threshold
only when it was calibrated for the selected model on an annotated corpus from
the manuscript, and record the model, threshold, and calibration source in the
audit.

Treat the output as a ranked reading queue:

- lexical similarity catches close rewrites;
- embedding similarity can surface distant paraphrases;
- citation deltas and `review_flags` expose evidence, negation, modality,
  causality, or qualification that requires close reading;
- low similarity does not prove that two propositions are distinct;
- high similarity does not prove redundancy.

Review the full reverse outline as well as the ranked pairs. The sensor may miss
long-distance repetition expressed through different terminology.

### Optional local semantic pre-review

When the candidate queue is large enough that a preliminary pass reduces review
cost, invoke `scrittura` and follow the Local microtasks reference linked from
that skill's entrypoint, using local `qwen3.8:latest`. Give Qwen only bounded
candidate pairs, their locators, section functions, citation metadata, and
`review_flags`.
Request structured provisional output containing:

```text
pair_id, provisional_classification, shared_proposition,
distinct_information, safeguard_flags, short_rationale
```

For a direct Ollama call, use JSON output with `think: false`; the local model
can otherwise complete a reasoning turn while leaving the final `response`
field empty.

Allow only the classifications in section 4. Qwen's output is working material:
check every retained field against the exact paragraphs and their full section
context. The primary agent assigns the final classification, confidence,
canonical home, and proposed action. Continue without this pass when the local
model is unavailable or verification would cost as much as direct review.

## 4. Classify propositions and clusters

Cluster paragraphs only after reading them in their section context. Assign one
classification to every reviewed candidate:

| Classification | Criterion |
|---|---|
| `true duplicate` | Same proposition and function, with no material new evidence, condition, qualification, or implication |
| `same claim with new evidence` | Same proposition, but a distinct source, datum, example, or warranted development is added |
| `necessary reprise` | A preview, bridge, recap, introduction, or conclusion deliberately re-anchors the argument in its new location |
| `recurring technical term` | The same canonical label appears, but the paragraphs make different propositions |
| `contradiction` | Polarity, causality, modality, scope, conditions, or conclusions are incompatible or unresolved |
| `false positive` | Surface or vector similarity does not reflect the same argumentative content |

For every cluster, identify:

1. the shared core proposition;
2. the distinct contribution of each paragraph, including citation metadata;
3. the canonical home in which the full idea belongs;
4. what would be lost by merging or cutting;
5. whether the repeated content serves a real structural function.

Preserve definitions, evidence, citations, examples, conditions, negations,
epistemic qualifiers, causal strength, and limitations. Introduction and
conclusion may legitimately share the governing thesis when their functions
differ. A new citation is evidence metadata, not automatic proof of a new
argumentative contribution.

## 5. Detect circularity and tortuous progression

Trace each section as `claim -> support -> inference -> destination`. Flag:

- a premise that merely restates the conclusion;
- a cross-reference that points back to an assertion but adds no support;
- consecutive or distant paragraphs that repeat the governing claim without a
  new premise, evidence, distinction, consequence, or limitation;
- repeated previews or recaps that postpone the paragraph doing the actual
  argumentative work;
- detours that require the reader to leave and re-enter the main claim;
- qualifications distributed so far from their claim that the argument becomes
  difficult to reconstruct.

Do not diagnose sentence length or ornament here unless it hides one of these
argumentative relations. Route sentence-level clarity and rhythm to
`scrittura`, then `tone-of-voice`.

## 6. Required audit output

Present the reverse outline first, followed by:

```text
| Cluster | Paragraphs | Shared proposition | Distinct information | Type | Canonical home | Proposed action | Confidence |
```

`Proposed action` is one of:

- `KEEP` — both propositions or structural functions are necessary;
- `MERGE` — combine the shared core and all warranted deltas in the canonical
  home;
- `MOVE` — relocate a contribution to the section where it performs its real
  function;
- `CUT` — remove a true duplicate only when a named canonical survivor retains
  the complete warranted content;
- `DEEPEN` — replace a stalled repetition with the missing premise, evidence,
  distinction, implication, or limit;
- `CROSS-REFERENCE` — keep a short functional reminder while locating the full
  treatment in one canonical home.

Then add:

```text
## Circularity and progression
| Chain | Repeated conclusion | Missing advancement | Proposed repair | Risk |

## Decision packets
### Cluster <ID> — <action>
- Canonical survivor/home: <ID and locator>
- Shared core: <proposition>
- Unique information to preserve: <item by paragraph, including citations>
- Structural function to preserve: <preview/bridge/recap/etc. or none>
- Risk: <low|medium|high and reason>
- Decision: Accetta / Modifica / Mantieni / Tieni in considerazione
```

Confidence describes the quality of the evidence for the diagnosis, not the
similarity score alone. Every `CUT` and `MERGE` packet must name a canonical
survivor/home and account for all unique information. Present independent
clusters as separate decisions. For a packet that touches a frozen paragraph,
use the advisory warning in `workflow/15-freeze-ledger.md`; keep the ledger
unchanged during diagnosis. Then wait. Do not draft replacement prose unless
the user asks to see it.

## 7. Apply only approved decisions

An accepted redundancy action starts a `tracked-round`; it never uses
`direct-apply` or `/r-auto`.

1. Revalidate the source checksum, paragraph map, exact accepted cluster, and
   freeze state. Surface drift before editing.
2. Create the new working version and task through the first-edit lifecycle in
   `SKILL.md`, using `COMMAND=/r-redundancy`.
3. Use the move and preservation manifest from
   `workflow/13-content-structure.md`. Account for every affected paragraph and
   every unique contribution.
4. If the accepted action requires new or consolidated wording, use
   `wayfinder` to confirm the intended proposition, `scrittura` to draft one
   complete replacement at the least invasive sufficient depth, and
   `tone-of-voice` to polish it and run the formula and implication audit. Show
   wording that was not already approved and obtain a separate decision before
   applying it.
5. Apply only the accepted cluster. Recompute locators and rerun this audit on
   the affected scope; a former duplicate should either disappear or remain
   with an explicit distinct function.
6. Run citation or numeric verification when their content changed. Check that
   negation, modality, causal strength, conditions, limitations, and bridge
   citations survived.
7. Use `thesis-text-graph` to inspect the affected cross-section connections.
   Regenerate graph artifacts only when the user requested them or the project
   lifecycle already requires them, and include generated paths in the session
   manifest.

Close or hand off the tracked round through the standard article-revision
lifecycle. Git publication remains separately authorized.

## 8. Verification

At the end of a diagnostic-only run, verify the recorded checksum and scoped
Git status are unchanged. At the end of an applied run, report:

- accepted cluster and resulting paragraph locators;
- preservation manifest result;
- citations and semantic safeguards retained;
- residual repeated propositions or circular chains;
- graph/coherence check status;
- tracked files changed and any unrelated pre-existing work left untouched.

Maintainers run:

```bash
<project-python> tests/test_redundancy_candidates.py
```

The behavioural cases in `tests/redundancy-cases.json` cover distant
paraphrase, technical-term false positives, legitimate reprise, semantic
safeguards, new evidence, read-only execution, and preservation accounting.
