# Output Review — APM Readiness for `dbensmith/agent-library`

**Plan ID:** `20260625-apm-readiness-review`
**Review Date:** 2026-06-25
**Reviewer:** REVIEWER role (Wave 4 quality gate)
**Documents Reviewed:**
- `readiness-report.md` (305 lines)
- `PRD.md` (454 lines)
- Source-of-truth: `research-digest.md`, `gap-analysis.md`

---

## Verdict: APPROVED — outputs are correct, consistent, and ready for stakeholder consumption

The readiness report and PRD are well-constructed, internally consistent, and faithfully cross-referenced against the gap analysis and APM spec research digest. The NO-GO verdict is justified by one CRITICAL gap (zero git tags) and three HIGH gaps (missing source primitives, stale build). All 13 gaps map to concrete action items. No factual errors, no missing gap coverage, no blocking issues.

**4 suggestions** below are minor improvements — none require re-review.

---

## Cross-Validation Summary

### Gap Coverage: 13/13 gaps represented in both outputs ✅

| Gap | Readiness Report | PRD Action |
|-----|------------------|------------|
| GAP-01 (CRITICAL) | §2, table row | Action 1 |
| GAP-02 (HIGH) | §2, table row | Action 2 |
| GAP-03 (HIGH) | §2, table row | Action 3 |
| GAP-04 (HIGH) | §2, table row | Action 4 |
| GAP-05 (MEDIUM) | §2, table row | Actions 2, 6 |
| GAP-06 (MEDIUM) | §2, table row | Action 5 |
| GAP-07 (MEDIUM) | §2, table row | Action 7 |
| GAP-08 (MEDIUM) | §2, table row | Action 5 |
| GAP-09 (MEDIUM) | §2, table row | Action 5 |
| GAP-10 (LOW) | §2, table row | Action 4 |
| GAP-11 (LOW) | §2, table row | Action 3 |
| GAP-12 (LOW) | §2, table row | Action 6 |
| GAP-13 (LOW) | §2, table row | Action 6 (optional) |

### Verdict Justification: NO-GO matches gap analysis conclusion ✅

Gap analysis conclusion (lines 480-487): "not release-ready due to 1 CRITICAL and 3 HIGH gaps."
Readiness report verdict (line 13): "NO-GO — Not ready for `apm install dbensmith/agent-library#v0.1.0`"

### BDD Action Items: All 7 use the required prefix ✅

Every action item opens with the exact user story prefix:
> "As a user I should be able to run `apm install dbensmith/agent-library` and have it work automatically with latest and release version and sha pinning"

Each maps to ≥1 documented gap (verified in Appendix A of PRD). Verification criteria are specific and testable.

### Pre-Flight Checklists: ≥5 items, binary verifiable ✅

Readiness report: 8 items. PRD definition-of-done: 12 items. All are yes/no gates.

### Compliance Matrix: Non-marketplace requirements fully covered ✅

The readiness report's 14-item compliance matrix covers all MUST/SHOULD requirements from the research digest that apply to direct GitHub install (marketplace-only items 15-18, 20 correctly excluded since PRD Appendix B declares marketplace publishing a non-goal).

---

## Findings

### WARNING-1: GAP-02 severity classification is aggressive but defensible

**Location:** `readiness-report.md` lines 42-49; `gap-analysis.md` lines 93-118

**Issue:** GAP-02 (missing `.apm/instructions/`) is classified HIGH with the claim that "`apm compile` cannot produce root context files." Per the research digest §2.2, ALL subdirectories under `.apm/` are **optional** — a package with zero instruction primitives is perfectly valid. `apm compile` on a package with no instructions would produce empty (but not errored) root context files; the install itself would still succeed.

The HIGH classification is justified by the declared `gemini` and `opencode` targets in `apm.yml` (which "require" compile output per §4.2). However, "require" in the spec means "recommended for best experience," not "will hard-fail." A consumer on gemini without instructions would get an empty `GEMINI.md` — suboptimal but not blocked.

**Why it still holds:** The existing `AGENTS.md` line 9 declares `<!-- Source: local .apm/instructions/library.instructions.md -->`, meaning the current deployed output references a source that doesn't exist. This is worse than a fresh package that never had instructions — the existing artifact is orphaned from its source. This specific circumstance elevates the severity.

**Recommendation:** Add a one-sentence note in the readiness report clarifying that instructions are optional in general, but the gap is HIGH here because (a) existing `AGENTS.md` references the missing source and (b) declared non-copilot targets benefit from compile output.

---

### SUGGESTION-1: License absent from `apm.yml` — not promoted to a gap

**Location:** `gap-analysis.md` §6.1 (line 360); `readiness-report.md` §5.2

**Issue:** The gap analysis §6.1 explicitly notes: "⚠ License declared in plugin.json but not apm.yml." Research Digest §1.5 classifies `license` as SHOULD. The plugin.json currently carries `MIT`, but the README and PRD never mention adding `license: MIT` to `apm.yml`. When the stale build is regenerated (Action 4), APM may not propagate the license from the old plugin.json into the new one — it synthesizes from `apm.yml`.

**Impact:** Minor. Consumers installing via `apm install` from GitHub repo will still get the MIT license from the repo's LICENSE file. But the lockfile's `declared_license` field may be empty, affecting SBOM accuracy.

**Recommendation:** Add `license: MIT` to the `apm.yml` edits in PRD Action 5. This is a single-line addition.

---

### SUGGESTION-2: Compile behavior is inferred, not tested — make this explicit

**Location:** `readiness-report.md` lines 43-48; checklist item 4 (line 237)

**Issue:** Multiple statements assert that `apm compile` "will fail" or "cannot produce" output due to missing `.apm/instructions/`. The readiness report correctly marks checklist item 4 as UNVERIFIED. However, the certainty of language elsewhere ("apm compile cannot produce," "apm pack cannot reproduce") could mislead a reader into thinking this was empirically tested. It wasn't — it's a reasoned inference from the spec.

**Recommendation:** Add a footnote or parenthetical to GAP-02 and GAP-04 stating: "Inferred from spec — not empirically tested. Recommend running `apm compile` as first verification step after fixes."

---

### SUGGESTION-3: PRD user story prefix covers 3 modes; PRD body targets 4

**Location:** `PRD.md` Section 1 (lines 16, 22-29) vs action item prefixes

**Issue:** The common prefix across all actions says "latest and release version and sha pinning" — explicitly naming 3 modes. But PRD §1 defines **four** modes: Latest, Release tag, SHA pinning, and Semver range (line 27). The Definition of Done (§4.1, lines 372-384) includes all four.

**Impact:** None. SHA pinning and semver ranges both resolve to a commit SHA, so "sha pinning" arguably covers both. But a reader comparing the prefix against the four-mode table may notice the omission.

**Recommendation:** Either (a) add "and semver ranges" to the prefix, or (b) add a note in §1 explaining that "sha pinning" encompasses semver range resolution since both ultimately pin a commit SHA.

---

## What Works Well

1. **Comprehensive gap-to-action mapping.** PRD Appendix A provides a one-glance cross-reference of all 13 gaps to 7 actions. No gap is orphaned.

2. **Honest about unknowns.** The readiness report uses UNVERIFIED and PARTIAL statuses instead of fabricating results. The PRD correctly states the unqualified install "may work but is untested" (line 29).

3. **Correct sequencing.** The dependency graph respects real constraints — git tags are independent, source primitives must exist before rebuild, CI depends on everything else passing.

4. **Spec-anchored.** Every gap in the readiness report cites specific research digest sections and APM documentation URLs. Cross-reference table (§5.1) is thorough.

5. **Actionable remediation.** Each action item has concrete commands, expected output, and BDD-style acceptance criteria. A maintainer could follow the PRD without additional research.

6. **Minimal scope discipline.** PRD Appendix B explicitly lists non-goals (marketplace publishing, new primitives, APM version upgrades), preventing scope creep.

---

## Repository Ground-Truth Confirmation

Verified on-disk state matches gap analysis claims:
- `git tag --list`: **no output** (confirms GAP-01) ✅
- `.apm/`: contains only `skills/` subdirectory (confirms GAP-02, GAP-03) ✅
- `.gem-team.yaml`: absent (confirms GAP-13) ✅

No discrepancies between documented findings and actual repository state.

---

## Final Assessment

| Criterion | Result |
|-----------|--------|
| Cross-validation against source documents | **PASS** — 13/13 gaps represented, verdict consistent with gap analysis |
| BDD action item quality | **PASS** — correct prefix, gap mapping, testable criteria |
| GO/NO-GO verdict justification | **PASS** — clearly reasoned from CRITICAL+HIGH gaps |
| Pre-flight checklist completeness | **PASS** — 8 items (report), 12 items (PRD), all binary |
| Logic and consistency | **PASS** — no internal contradictions, dependency graph valid |
| Edge cases and assumptions | **PASS with notes** — 3 minor suggestions for improvement |

**Outputs are ready for stakeholder consumption.** The NO-GO verdict is correct and well-supported. The 7 action items in the PRD, if executed in the specified order, will resolve all blocking and advisory gaps.
