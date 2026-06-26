# Product Requirements Document — APM Readiness for `dbensmith/agent-library`

**PRD ID:** `20260625-apm-readiness-review`
**Version:** `1.0.0`
**Repository:** `dbensmith/agent-library`
**Status:** Draft — pending implementation
**Plan ID:** `20260625-apm-readiness-review`
**Generated:** 2026-06-25

---

## 1. User Story Overview

### Core User Story

> As a user I should be able to run `apm install dbensmith/agent-library` and have it work automatically with latest and release version and sha pinning

This is the single BDD story that all action items decompose. Every fix below answers: what must be true for this one user action to succeed?

### Three Installation Modes

| Mode | User Command | What APM Resolves | What's Required |
|------|-------------|-------------------|-----------------|
| **Latest** (unqualified) | `apm install dbensmith/agent-library` | HEAD of default branch (`main`); locks commit SHA | Valid `apm.yml` at repo root; `.apm/` directory exists; compile succeeds |
| **Release tag** | `apm install dbensmith/agent-library#v0.1.0` | Exact tag `v0.1.0` on remote (immutable) | A git tag matching `v?.d+.d+.d+` pushed to the remote |
| **SHA pinning** | `apm install dbensmith/agent-library#<commit-sha>` | Exact commit by 7–40 character hex SHA | The commit must contain a valid `apm.yml` and `.apm/` tree as of that revision |
| **Semver range** | `apm install dbensmith/agent-library` with `ref: "^0.1.0"` | Highest tag satisfying the range | At least one semver tag exists; `apm.yml version` must be parseable |

**Current state (2026-06-25):** The unqualified (latest) install via `main` branch *may* work but is untested. Release-tag and semver-range installs **fail** because no git tags exist. SHA pinning would work only if the pinned commit contains a valid `apm.yml` and `.apm/` tree — but `apm compile` would fail for non-copilot targets due to missing `.apm/instructions/` source. This PRD defines the minimum actions to make all four modes work reliably.

---

## 2. Action Items

---

### Action 1: Create and Push Git Version Tags

**As a user I should be able to run `apm install dbensmith/agent-library` and have it work automatically with latest and release version and sha pinning**

**Sub-requirement:** The repository must have at least one semver-formatted git tag pushed to the remote so that version-pinned installs (`#v0.1.0`) and semver ranges (`^0.1.0`) can resolve.

**Maps to gaps:** GAP-01 (Zero git tags — CRITICAL)

**Verification:** Run `git ls-remote --tags origin` and confirm at least one tag matching `v0.1.0` appears. Run `apm install dbensmith/agent-library#v0.1.0` in a clean consumer repo — it must succeed.

**Acceptance Criteria:**

- **Given** the repository has `version: 0.1.0` in `apm.yml` and a release commit on `main`,  
  **When** a maintainer runs `git tag v0.1.0` on the release commit and `git push origin v0.1.0`,  
  **Then** `git ls-remote --tags origin` lists `refs/tags/v0.1.0`.

- **Given** the `v0.1.0` tag exists on the remote,  
  **When** a consumer runs `apm install dbensmith/agent-library#v0.1.0`,  
  **Then** APM resolves the tag, locks the commit SHA in `apm.lock.yaml`, and deploys all primitives without error.

- **Given** the `v0.1.0` tag exists on the remote,  
  **When** a consumer uses a semver range like `ref: "^0.1.0"` in their `apm.yml` and runs `apm install`,  
  **Then** APM resolves to `v0.1.0` (the highest satisfying tag) and install succeeds.

**Tags to create (minimum):**

| Tag | Commit | Purpose |
|-----|--------|---------|
| `v0.1.0` | Current HEAD of `main` (or the commit with all fixes applied) | First release; enables `#v0.1.0` and range `^0.1.0` |

**Effort:** Trivial — two commands (`git tag && git push`)

---

### Action 2: Create `.apm/instructions/` Source Directory

**As a user I should be able to run `apm install dbensmith/agent-library` and have it work automatically with latest and release version and sha pinning**

**Sub-requirement:** The `.apm/instructions/` directory must exist and contain a valid `.instructions.md` file so that `apm compile` succeeds for all declared non-copilot targets (gemini, opencode). The current build output contains `instructions/library.instructions.md` but the source file in `.apm/instructions/` is missing — compile will fail on a fresh run.

**Maps to gaps:** GAP-02 (Missing `.apm/instructions/` source — HIGH), GAP-05 (README references non-existent directories — MEDIUM)

**Verification:** Run `apm compile --validate` — must exit zero with no errors about missing instruction primitives. Run `apm compile -t gemini` — must produce `GEMINI.md` at repo root with embedded instructions content. Run `apm compile -t opencode` — must produce `AGENTS.md` at repo root with embedded instructions content.

**Acceptance Criteria:**

- **Given** the `build/agent-library-0.1.0/instructions/library.instructions.md` exists and contains the current agent library instructions,  
  **When** a maintainer creates `.apm/instructions/library.instructions.md` with the same content,  
  **Then** `.apm/instructions/` is a non-empty directory containing exactly one `.instructions.md` file.

- **Given** `.apm/instructions/library.instructions.md` exists,  
  **When** a maintainer runs `apm compile --validate`,  
  **Then** APM parses the instruction primitive, reports no structural errors, and exits zero.

- **Given** `.apm/instructions/library.instructions.md` exists,  
  **When** a maintainer runs `apm compile -t gemini && apm compile -t opencode`,  
  **Then** `GEMINI.md` and `AGENTS.md` are generated at repo root with the instructions embedded and a valid `<!-- Source: local .apm/instructions/library.instructions.md -->` comment.

**Source file to create:**

```
.apm/
├── instructions/
│   └── library.instructions.md   ← NEW (copy content from build/agent-library-0.1.0/instructions/library.instructions.md)
└── skills/                        ← Existing
```

**Effort:** Trivial — copy existing build artifact content into correct source location.

---

### Action 3: Create `.apm/agents/` Source Directory with Frontmatter

**As a user I should be able to run `apm install dbensmith/agent-library` and have it work automatically with latest and release version and sha pinning**

**Sub-requirement:** The `.apm/agents/` directory must exist and contain `marketplace-listings.agent.md` with valid YAML frontmatter so that the agent primitive is reproducible from source. The current build output ships this agent but no source exists — any future `apm pack` will omit it.

**Maps to gaps:** GAP-03 (Missing `.apm/agents/` source — HIGH), GAP-11 (Build agent file missing YAML frontmatter — LOW)

**Verification:** Run `apm compile --validate` — must not report missing agent primitives. Run `apm pack` — the resulting `build/<name>/agents/` directory must contain `marketplace-listings.agent.md` with YAML frontmatter.

**Acceptance Criteria:**

- **Given** the `build/agent-library-0.1.0/agents/marketplace-listings.agent.md` exists and contains the agent definition (minus frontmatter),  
  **When** a maintainer creates `.apm/agents/marketplace-listings.agent.md` with YAML frontmatter (`---`, `name`, `description`, `---`) followed by the agent Markdown body,  
  **Then** `.apm/agents/` is a non-empty directory containing exactly one `.agent.md` file.

- **Given** `.apm/agents/marketplace-listings.agent.md` exists with valid frontmatter,  
  **When** a maintainer runs `apm pack`,  
  **Then** the `build/agent-library-<version>/agents/` output includes `marketplace-listings.agent.md` with its frontmatter block intact.

- **Given** the agent file has YAML frontmatter with `name: marketplace-listings` and `description`,  
  **When** a consumer installs the package,  
  **Then** the target tool UI displays the agent with the correct name and description.

**Required frontmatter template:**

```yaml
---
name: marketplace-listings
description: Drafts Facebook Marketplace listings (with price/firm/OBO checks,
  OneDrive photo subfolders, and custom style guidelines) and automates
  posting via browser injection.
---
```

**Effort:** Trivial — copy existing build content, add frontmatter block.

---

### Action 4: Regenerate Build Output from Clean State

**As a user I should be able to run `apm install dbensmith/agent-library` and have it work automatically with latest and release version and sha pinning**

**Sub-requirement:** After fixing the source tree (Actions 2, 3), run a full `apm install → apm compile → apm pack` pipeline to regenerate `build/` and `plugin.json` from current state. The existing `build/` directory is stale — it is missing the `review-and-refactor` skill and contains orphaned files with no source. The lockfile also lacks `local_deployed_file_hashes`.

**Maps to gaps:** GAP-04 (Build output is stale/inconsistent — HIGH), GAP-10 (`local_deployed_file_hashes` absent from lockfile — LOW)

**Verification:** Run `apm install` to refresh `.agents/`. Confirm `.agents/skills/review-and-refactor/` is present. Run `apm compile` for all targets — all must exit zero. Run `apm pack` — the resulting `build/` must contain: 9 skills (including `review-and-refactor`), `instructions/library.instructions.md`, `agents/marketplace-listings.agent.md`, and `plugin.json`. Run `apm audit` — must report no drift.

**Acceptance Criteria:**

- **Given** Actions 2 and 3 are complete (`.apm/instructions/` and `.apm/agents/` exist),  
  **When** a maintainer runs `apm install`,  
  **Then** `.agents/skills/` contains 9 skill directories (4 local + 5 remote dependencies), including `review-and-refactor` which was missing from the previous stale build.

- **Given** `.apm/` source is complete and `.agents/` is current,  
  **When** a maintainer runs `apm compile -t copilot && apm compile -t gemini && apm compile -t opencode`,  
  **Then** all three compiles exit zero and produce their respective root context files.

- **Given** compile succeeded for all targets,  
  **When** a maintainer runs `apm pack`,  
  **Then** `build/agent-library-0.1.0/` is regenerated, contains all 9 skills, instructions, agents, and `plugin.json`, and `apm audit` reports zero drift when comparing deployed files to source.

- **Given** a fresh `apm install` was run,  
  **When** the lockfile is inspected,  
  **Then** `apm.lock.yaml` includes `local_deployed_file_hashes` with SHA-256 hashes for each locally-deployed file.

**Command sequence:**

```bash
apm install                   # Refresh .agents/ from lockfile
apm compile --validate        # Validation dry-run
apm compile                   # Compile all targets (default)
apm compile -t gemini         # Gemini-specific output
apm audit                     # Check for drift and hidden Unicode
apm pack                      # Generate build/<name>-<version>/
```

**Effort:** Medium — requires all source gaps to be resolved first; the pipeline itself is automated.

---

### Action 5: Update Manifest for Accuracy and Completeness

**As a user I should be able to run `apm install dbensmith/agent-library` and have it work automatically with latest and release version and sha pinning**

**Sub-requirement:** The `apm.yml` manifest must have a meaningful description, a `start` script for consumer entry point, and complete target declarations. These improve discoverability (`apm view` / `apm search`) and enable cross-tool compatibility.

**Maps to gaps:** GAP-06 (`apm.yml` description is generic placeholder — MEDIUM), GAP-08 (No `scripts` section — MEDIUM), GAP-09 (`targets` list incomplete — MEDIUM)

**Verification:** Run `apm view .` — description must be meaningful and non-generic. Run `apm pack` — must not warn about missing description or empty scripts. Run `apm compile -t all` — must generate output for all declared targets without errors.

**Acceptance Criteria:**

- **Given** the current `apm.yml` description is `"APM project for agent-library"`,  
  **When** a maintainer replaces it with a descriptive string (e.g., `"Centralized library of AI agent instructions, skills, and tool definitions for copilot, gemini, opencode, and compatible targets."`),  
  **Then** `apm view .` displays the new description and `apm pack` emits no description-related warning.

- **Given** the current `scripts:` block is empty (`{}`),  
  **When** a maintainer adds a `start` script entry,  
  **Then** consumers can run `apm start` (per APM script conventions) or `apm run start` to get a one-command entry point.

- **Given** the current `targets` list has only 3 entries (`copilot`, `gemini`, `opencode`),  
  **When** a maintainer adds all compatible targets or uses `targets: [all]`,  
  **Then** `apm compile` generates output for every supported tool harness, and consumers using non-declared targets receive tool-specific context files.

**Recommended `apm.yml` changes:**

```yaml
# Before → After
description: APM project for agent-library
# →
description: >-
  Centralized library of AI agent instructions, skills, and tool
  definitions for copilot, gemini, opencode, and compatible targets.

scripts: {}
# →
scripts:
  start: apm compile && echo 'agent-library ready. Skills in .agents/skills/'

targets:
  - copilot
  - gemini
  - opencode
# →
targets:
  - all
```

**Effort:** Trivial — three field updates in `apm.yml`.

---

### Action 6: Fix README and Documentation Accuracy

**As a user I should be able to run `apm install dbensmith/agent-library` and have it work automatically with latest and release version and sha pinning**

**Sub-requirement:** The `README.md` currently claims that `.apm/instructions/`, `.apm/prompts/`, and `docs/` (with architecture guides) exist. Two of these directories do not exist. The README must accurately reflect the repository's actual directory structure so consumers can follow it without hitting dead ends.

**Maps to gaps:** GAP-05 (README references non-existent directories — MEDIUM), GAP-12 (README `docs/` description misleading — LOW), GAP-13 (No `.gem-team.yaml` — LOW; optional)

**Verification:** After Actions 2 and 3 complete, verify every directory referenced in the "Directory Structure" section of `README.md` exists on disk and contains the described content. If `.apm/prompts/` is not planned, remove its reference from the README. Verify `docs/` description matches actual content.

**Acceptance Criteria:**

- **Given** Actions 2 and 3 have created `.apm/instructions/` and `.apm/agents/`,  
  **When** a maintainer reviews the README "Directory Structure" section,  
  **Then** every listed directory exists on disk and contains the described artifacts.

- **Given** `.apm/prompts/` does not exist and no prompts are planned for this release,  
  **When** a maintainer updates the README,  
  **Then** the reference to `.apm/prompts/` is removed from the directory structure listing.

- **Given** `docs/` currently contains only the plan audit directory (`plan/20260625-apm-readiness-review/`),  
  **When** a maintainer updates the README's `docs/` description,  
  **Then** it accurately states what `docs/` contains (e.g., "APM readiness review artifacts and remediation plans") rather than claiming "architecture patterns and general configuration guides."

- **Given** all README fixes are applied,  
  **When** a new consumer clones the repository and follows the README's directory references,  
  **Then** every referenced path is navigable and contains the described content.

**Effort:** Trivial — text edits to `README.md` lines 95–98.

---

### Action 7: Set Up CI/CD Pipeline with APM Validation Gates

**As a user I should be able to run `apm install dbensmith/agent-library` and have it work automatically with latest and release version and sha pinning**

**Sub-requirement:** A GitHub Actions CI pipeline must run automated APM validation gates on every push and pull request to prevent regressions. The pipeline must at minimum execute `apm compile --validate`, `apm audit --ci`, and `apm pack --check-clean`. This ensures that the package remains installable across all three modes as the repository evolves.

**Maps to gaps:** GAP-07 (No CI/CD pipeline — MEDIUM)

**Verification:** Push a commit to `main` or open a PR — the CI workflow must trigger and complete with all gates passing (exit zero). Intentionally break a primitive (e.g., remove frontmatter from a skill) — CI must fail with a non-zero exit.

**Acceptance Criteria:**

- **Given** no `.github/workflows/` directory exists,  
  **When** a maintainer creates `.github/workflows/apm-ci.yml`,  
  **Then** the directory exists and contains a valid GitHub Actions workflow definition.

- **Given** the CI workflow is configured,  
  **When** a commit is pushed to any branch,  
  **Then** the workflow runs `apm compile --validate` and fails if any primitive has structural errors.

- **Given** the CI workflow is configured,  
  **When** a commit is pushed,  
  **Then** the workflow runs `apm audit --ci` and fails if hidden Unicode characters are found or if deployed files have drifted from source.

- **Given** the CI workflow is configured,  
  **When** a commit is pushed to `main`,  
  **Then** the workflow runs `apm pack --check-clean` to verify the working tree is clean and version alignment is correct.

**Minimum CI workflow template:**

```yaml
name: APM CI
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: microsoft/apm-action@v1
      - run: apm install
      - run: apm compile --validate
      - run: apm audit --ci
      - run: apm pack --check-clean
        if: github.ref == 'refs/heads/main'
```

**Effort:** Easy — create one YAML file. Depends on Actions 1–5 being complete so the CI gates can actually pass.

---

## 3. Dependency Graph

### 3.1 Execution Order

```
Phase 1 — Independent (parallel)        Phase 2 — Sequential        Phase 3 — Gated
─────────────────────────────────       ──────────────────────      ───────────────
Action 1: Git Tags                       Action 4: Rebuild       ┌─ Action 7: CI/CD
Action 2: .apm/instructions/             (depends on 2, 3)       │  (depends on 1–5)
Action 3: .apm/agents/                         │                  │
Action 5: Manifest updates                     ▼                  │
Action 6: README/docs fixes         ┌────────────────┐           │
                                    │ apm install     │           │
                                    │ apm compile     │───────────┘
                                    │ apm audit       │
                                    │ apm pack        │
                                    └────────────────┘
```

### 3.2 Dependency Matrix

| Action | Blocks | Blocked By | Can Parallelize With |
|--------|--------|-----------|---------------------|
| Action 1 (Git Tags) | CI verification (Action 7) | — | Actions 2, 3, 5, 6 |
| Action 2 (.apm/instructions/) | Build regeneration (Action 4) | — | Actions 1, 3, 5, 6 |
| Action 3 (.apm/agents/) | Build regeneration (Action 4) | — | Actions 1, 2, 5, 6 |
| Action 4 (Rebuild) | CI gates (Action 7) | Actions 2, 3 | — |
| Action 5 (Manifest) | CI gates (Action 7) | — | Actions 1, 2, 3, 6 |
| Action 6 (README/docs) | — | Soft: Actions 2, 3 (README should not reference dirs that still don't exist) | Actions 1, 5 |
| Action 7 (CI/CD) | — (final gate) | Actions 1, 2, 3, 4, 5 | — |

### 3.3 Critical Path

```
Action 2 (.apm/instructions/) → Action 4 (Rebuild) → Action 7 (CI/CD)
Action 3 (.apm/agents/)       ↗
```

**Estimated total serial time:** Actions 2+3 in parallel (~10 min), Action 4 (~5 min), Action 7 (~15 min) = **~30 minutes** of serial work. With Actions 1, 5, 6 done in parallel during Phase 1, the wall-clock time is dominated by the critical path.

---

## 4. Definition of Done

### 4.1 What "APM Install Works Automatically" Means

The package `dbensmith/agent-library` is **done** when a consumer on any supported platform can run **all** of the following commands and each succeeds without error:

```bash
# Mode 1: Latest (unqualified) — must resolve HEAD of main
apm install dbensmith/agent-library

# Mode 2: Release tag pinning — must resolve v0.1.0 tag
apm install dbensmith/agent-library#v0.1.0

# Mode 3: SHA pinning — must resolve exact commit
apm install dbensmith/agent-library#<commit-sha>

# Mode 4: Semver range — must resolve highest satisfying tag
# (by adding to consumer's apm.yml: dependencies.apm: [{ ref: "^0.1.0", repo: dbensmith/agent-library }])
apm install
```

And the resulting deployed files must include:

- `.agents/skills/` with all 9 skills (4 local + 5 remote dependencies)
- Target-specific root context files (e.g., `AGENTS.md` for opencode, `GEMINI.md` for gemini)
- `.agents/skills/review-and-refactor/` (the skill that was missing from the stale build)
- `.agents/agents/marketplace-listings.agent.md` with valid frontmatter

### 4.2 Pre-Flight Checklist (All Must Be True)

Before a consumer can run the above commands successfully, every item on this checklist must pass:

| # | Gate | How to Verify | Maps to Action |
|---|------|--------------|----------------|
| 1 | Git tag `v0.1.0` exists on remote | `git ls-remote --tags origin | grep v0.1.0` | Action 1 |
| 2 | `.apm/instructions/library.instructions.md` exists | `ls .apm/instructions/library.instructions.md` | Action 2 |
| 3 | `.apm/agents/marketplace-listings.agent.md` exists with YAML frontmatter | `head -5 .apm/agents/marketplace-listings.agent.md` shows `---\nname:` | Action 3 |
| 4 | `apm compile --validate` exits zero | Run command; check exit code | Actions 2, 3 |
| 5 | `apm compile` for all targets exits zero | `apm compile -t copilot && apm compile -t gemini && apm compile -t opencode` | Actions 2, 3 |
| 6 | `.agents/skills/review-and-refactor/` exists after `apm install` | `ls .agents/skills/review-and-refactor/SKILL.md` | Action 4 |
| 7 | `apm audit` reports zero drift | `apm audit` exits zero with no findings | Action 4 |
| 8 | `apm pack` produces `build/<name>/plugin.json` | `ls build/agent-library-0.1.0/plugin.json` | Action 4 |
| 9 | `apm.yml` description is non-generic | `grep description apm.yml` shows descriptive text (not `"APM project for..."`) | Action 5 |
| 10 | `apm.yml` targets includes all supported tools | `grep -A 10 targets apm.yml` shows `all` or ≥6 targets | Action 5 |
| 11 | README.md does not reference non-existent directories | `grep -c prompts README.md` returns 0 (unless `.apm/prompts/` was created) | Action 6 |
| 12 | CI workflow runs and passes on push | Check GitHub Actions tab — latest run on `main` is green | Action 7 |

### 4.3 One-Shot Verification Command

After all actions are complete, this single command chain should exit zero:

```bash
apm install && \
  apm compile --validate && \
  apm compile -t copilot && apm compile -t gemini && apm compile -t opencode && \
  apm audit --ci && \
  apm pack --check-clean && \
  echo "ALL GATES PASSED — dbensmith/agent-library is APM-installable"
```

---

## Appendix A: Gap Coverage Map

| Gap ID | Severity | Title | Addressed By |
|--------|----------|-------|-------------|
| GAP-01 | CRITICAL | Zero git tags | Action 1 |
| GAP-02 | HIGH | Missing `.apm/instructions/` source | Action 2 |
| GAP-03 | HIGH | Missing `.apm/agents/` source | Action 3 |
| GAP-04 | HIGH | Build output stale/inconsistent | Action 4 |
| GAP-05 | MEDIUM | README references non-existent dirs | Actions 2, 6 |
| GAP-06 | MEDIUM | `apm.yml` description generic | Action 5 |
| GAP-07 | MEDIUM | No CI/CD pipeline | Action 7 |
| GAP-08 | MEDIUM | No `scripts` section | Action 5 |
| GAP-09 | MEDIUM | `targets` list incomplete | Action 5 |
| GAP-10 | LOW | `local_deployed_file_hashes` absent | Action 4 |
| GAP-11 | LOW | Build agent missing frontmatter | Action 3 |
| GAP-12 | LOW | README `docs/` description misleading | Action 6 |
| GAP-13 | LOW | No `.gem-team.yaml` | Action 6 (optional; mentioned as nice-to-have) |

---

## Appendix B: Non-Goals (Out of Scope for This PRD)

- Marketplace publishing (`apm marketplace publish`) — this PRD targets direct GitHub install only
- `apm-policy.yml` governance configuration — no enterprise governance requirements for this repo
- Adding new prompts, chatmodes, or context primitives — out of scope; only fixing existing gaps
- Migrating to `lockfile_version: 2` (registry deps) — current git-only deps are sufficient
- Upgrading APM CLI version beyond 0.16.1 (the version recorded in `apm.lock.yaml`)
