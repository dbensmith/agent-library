# APM Readiness Report — `dbensmith/agent-library`

**Plan ID:** `20260625-apm-readiness-review`
**Report Date:** 2026-06-25
**APM Version:** 0.16.1 (lockfile) / v0.16.1–v0.21.0 (spec reference)
**Repository:** `git@github.com:dbensmith/agent-library.git` (branch `humble-spider`)
**Reviewed by:** Automated audit (REVIEWER role)

---

## 1. Executive Summary & Verdict

### Verdict: **NO-GO** — Not ready for `apm install dbensmith/agent-library#v0.1.0`

The repository does **not** meet the minimum bar for a version-pinned APM consumer install. One critical blocker and three high-severity gaps prevent consumers from pinning to a version tag or reliably rebuilding the package from source.

**The core problem:** the repository has a structurally valid `apm.yml` and 4 correctly authored skills, but it lacks the three foundational artifacts that APM requires for a reliable consumer experience: (1) a published git tag for version pinning, (2) source instructions for `apm compile` to produce root context files for non-copilot targets, and (3) source agent definitions that match the published build output. All four HIGH+ gaps must be resolved before any release attempt.

### Quick Stats

| Metric | Value |
|---|---|
| Total gaps found | **13** |
| CRITICAL | **1** (zero git tags — blocks version-pinned install) |
| HIGH | **3** (missing source primitives, stale build) |
| MEDIUM | **5** (docs, CI, manifest completeness) |
| LOW | **4** (lockfile, frontmatter, config) |

---

## 2. Gap Summary

### GAP-01 — Zero Git Tags (CRITICAL)

- **Category:** Git Tags / Version Pinning
- **Description:** `git tag --list` returns no output. Zero tags exist on any branch, including `main`. The `apm.yml` declares `version: 0.1.0` but no tag `v0.1.0` (or `0.1.0`) exists in the remote.
- **Consumer impact:** `apm install dbensmith/agent-library#v0.1.0` **fails immediately** — APM resolves pinned versions by matching git tags against the `^v?\d+\.\d+\.\d+` pattern. No match = resolution failure. The only working install is the unqualified `dbensmith/agent-library` (resolves `latest` on `main`, pinning a floating commit SHA — non-reproducible across time).
- **Producer impact:** Blocks marketplace publishing. `apm marketplace check` exits non-zero. The `0.1.0` version in `apm.yml` is unverifiable.
- **Effort to fix:** Trivial — a single `git tag v0.1.0 && git push origin v0.1.0`.
- **Spec refs:** Research Digest §6.1, §6.2, §7.1; Manifest Schema §4.1.1.

### GAP-02 — Missing `.apm/instructions/` Source (HIGH)

- **Category:** Source Tree / Compile Blockage
- **Description:** No `.apm/instructions/` directory or `.instructions.md` file exists in the source tree. However, `AGENTS.md` line 9 declares source as `local .apm/instructions/library.instructions.md`, and `build/agent-library-0.1.0/instructions/library.instructions.md` contains functional content. The instructions primitive exists in the stale build output but has no source file to regenerate from.
- **Consumer impact:** Copilot target may function (compile is optional for copilot per APM spec §4.2). However, the `gemini` and `opencode` targets declared in `apm.yml` **require** compile output. A fresh `apm compile` will produce empty or broken GEMINI.md and AGENTS.md — consumers targeting gemini or opencode receive no library instructions.
- **Producer impact:** `apm compile` cannot produce root context files. `apm compile --validate` will report a missing primitive. `apm pack` cannot reproduce the current build.
- **Effort to fix:** Easy — create `.apm/instructions/library.instructions.md` with the content currently in the stale build, then re-run `apm compile`. Approx. 5 minutes.
- **Spec refs:** Research Digest §2.2, §4.1, §4.2; Package Anatomy; Compile your Package.

### GAP-03 — Missing `.apm/agents/` Source (HIGH)

- **Category:** Source Tree / Build Reproducibility
- **Description:** `build/agent-library-0.1.0/agents/marketplace-listings.agent.md` exists (64 lines, functional agent definition) but there is no `.apm/agents/` directory in the source tree. The source tree only contains `.apm/skills/`.
- **Consumer impact:** If the agent is intended to ship, consumers will not receive it from any future `apm pack` run. The agent file is orphaned in a stale build directory and will be lost when the build is regenerated.
- **Producer impact:** `apm pack` cannot reproduce the current build output. The `agents/marketplace-listings.agent.md` file in `build/` is a ghost — present now, gone after next rebuild.
- **Effort to fix:** Easy — create `.apm/agents/marketplace-listings.agent.md` with the agent definition. Requires YAML frontmatter (`---` delimiters) with `name` and `description` fields (per spec §2.3).
- **Spec refs:** Research Digest §2.2, §2.3, §2.4; Canonical layout for marketplace publishers.

### GAP-04 — Stale / Inconsistent Build Output (HIGH)

- **Category:** Build Integrity
- **Description:** The `build/agent-library-0.1.0/` directory is inconsistent with both the lockfile and the source tree:
  - Skills: lockfile lists 9 skills (4 local + 5 remote deps); build contains only 8 skills (`review-and-refactor` is missing from build)
  - Instructions: present in build but missing from source (GAP-02)
  - Agents: present in build but missing from source (GAP-03)
- **Consumer impact:** N/A (`build/` is a producer artifact, not consumed directly). But any bundle packaged from this stale build would fail integrity verification at install time (spec §5.3).
- **Producer impact:** `apm pack` on a fresh `apm install` will produce output different from the current `build/` contents. The current build cannot be trusted or shipped.
- **Effort to fix:** Easy (after GAP-02 and GAP-03 are resolved) — run `apm install && apm compile && apm pack` to regenerate from current state.
- **Spec refs:** Research Digest §5.3 (Bundle integrity), §5.4 (Empty bundle prevention).

### GAP-05 — README References Non-Existent Directories (MEDIUM)

- **Category:** Documentation Accuracy
- **Description:** README.md lines 95–98 claim the repository contains `.apm/instructions/`, `.apm/prompts/`, and `docs/` with "architecture patterns and general configuration guides." Ground truth:
  - `.apm/instructions/` — does not exist (GAP-02)
  - `.apm/prompts/` — does not exist
  - `docs/` — exists but only contains this audit's `plan/` directory; no architecture patterns
- **Consumer impact:** A consumer following the README will navigate to `.apm/instructions/` or `.apm/prompts/` and find nothing. Documentation is misleading and erodes trust.
- **Producer impact:** No direct blockage, but misrepresentation in public README hurts credibility for potential consumers browsing the GitHub repo.
- **Effort to fix:** Trivial — update README lines 95–98 to reflect actual directory structure. Alternatively, create the missing directories with content.
- **Spec refs:** Research Digest §13 item 13; general accuracy.

### GAP-06 — Generic Placeholder `apm.yml` Description (MEDIUM)

- **Category:** Manifest Completeness
- **Description:** `apm.yml` line 3: `description: APM project for agent-library` — the scaffold default. Not descriptive of the library's actual purpose (centralized library of AI agent instructions, skills, and tool definitions).
- **Consumer impact:** `apm view` and `apm search` display this description. It adds no information value for consumers evaluating the package.
- **Producer impact:** `apm pack` warns when description is scaffold-default. Reduces publish quality for marketplace listings.
- **Effort to fix:** Trivial — edit one line in `apm.yml` with a meaningful description.
- **Spec refs:** Research Digest §1.3; Manifest Schema §3.3.

### GAP-07 — No CI/CD Pipeline (MEDIUM)

- **Category:** CI/CD Automation
- **Description:** No `.github/workflows/` directory exists. No CI pipeline configured for automated `apm audit --ci`, `apm compile --validate`, or `apm pack --check-clean`.
- **Consumer impact:** No automated drift check — consumers may encounter stale deployed files if the producer forgets to re-compile after changes.
- **Producer impact:** All validation gates must be run manually before each release. No CI guard against regressions. Higher risk of shipping a broken package.
- **Effort to fix:** Medium — add a GitHub Actions workflow using `microsoft/apm-action` (spec §10.3). Minimum: run `apm compile --validate`, `apm audit --ci`, `apm pack --check-clean`. Requires workflow authoring and testing.
- **Spec refs:** Research Digest §10 (CI/CD Expectations), §10.2, §10.3.

### GAP-08 — Empty `scripts` Section (MEDIUM)

- **Category:** Manifest Completeness
- **Description:** `apm.yml` line 16: `scripts: {}`. No `start` or other entry-point scripts defined.
- **Consumer impact:** No one-command entry point after install. Consumer must know which primitives to load and how to invoke them.
- **Producer impact:** `apm pack` warns. Reduces publish quality score.
- **Effort to fix:** Trivial — add a `start` script entry to `apm.yml`.
- **Spec refs:** Research Digest §1.9; Manifest Schema §3.8.

### GAP-09 — Incomplete `targets` List (MEDIUM)

- **Category:** Manifest Completeness
- **Description:** `apm.yml` declares only 3 targets: `copilot`, `gemini`, `opencode`. Missing: `codex`, `claude`, `cursor`, `antigravity`, `windsurf`, `kiro`. The library is general-purpose; omitting targets limits cross-tool installability.
- **Consumer impact:** Install on non-declared targets may still work if primitives are compatible, but tool-specific optimizations (e.g., `.cursor/` rules, `.claude/` context files) will not be generated. Consumers on omitted targets get a degraded experience.
- **Producer impact:** `apm compile` generates output only for declared targets.
- **Effort to fix:** Trivial — add `all` to the targets list, or enumerate all compatible targets.
- **Spec refs:** Research Digest §1.6, §11.1; Manifest Schema §3.6; Targets Matrix.

### GAP-10 — `local_deployed_file_hashes` Absent from Lockfile (LOW)

- **Category:** Lockfile Completeness
- **Description:** `apm.lock.yaml` includes `local_deployed_files` (lines 50–54) but does **not** include `local_deployed_file_hashes`. The lockfile has SHA-256 content hashes for all 5 remote dependencies but not for the 4 local skills.
- **Consumer impact:** Minor. Integrity verification relies on dependency hashes (present for all 5 deps). Local file hash absence slightly weakens drift detection for local skills.
- **Producer impact:** `apm audit` drift detection still works via file comparison. Hashes would strengthen integrity checks.
- **Effort to fix:** Trivial — re-run `apm install` to regenerate lockfile with hashes.
- **Spec refs:** Research Digest §8.1; Lockfile Spec.

### GAP-11 — Build Agent File Missing Frontmatter (LOW)

- **Category:** Primitive Formatting
- **Description:** `build/agent-library-0.1.0/agents/marketplace-listings.agent.md` starts directly with Markdown content (`# Facebook Marketplace Listing Agent`). No YAML frontmatter block (`---` delimiters) is present.
- **Consumer impact:** APM may fail to parse metadata (name, description) from the agent file, causing it to appear nameless in target tool UIs.
- **Producer impact:** Minor. Addressed when GAP-03 is resolved (create the source file with proper frontmatter).
- **Effort to fix:** Trivial — add `---\nname: marketplace-listings\ndescription: ...\n---` at the top of the agent source file.
- **Spec refs:** Research Digest §2.3; Primitive file naming conventions.

### GAP-12 — README `docs/` Description Misleading (LOW)

- **Category:** Documentation Accuracy
- **Description:** README line 98 claims `docs/` contains "Architecture patterns and general configuration guides." In reality, `docs/` contains only `plan/20260625-apm-readiness-review/` (this audit's working directory).
- **Consumer impact:** Minor. Consumer looking for architecture documentation will find nothing.
- **Effort to fix:** Trivial — update README line 98 to accurately describe `docs/` contents, or add actual documentation.
- **Spec refs:** General accuracy.

### GAP-13 — No `.gem-team.yaml` Team Config (LOW)

- **Category:** Configuration
- **Description:** No `.gem-team.yaml` file at repository root. Team metadata (team name, members, ownership) not declared.
- **Consumer impact:** None. Not blocking for any APM operation.
- **Producer impact:** None. Optional configuration file for team-level settings.
- **Effort to fix:** Trivial — add `.gem-team.yaml` if team configuration is desired. Entirely optional.
- **Spec refs:** APM producer best practices.

---

## 3. Remediation Roadmap

### Phase 1: Unblock the Build Pipeline (CRITICAL + HIGH)

These gaps must be resolved before any consumer can install the package with version pinning or non-copilot targets.

**Ordered by dependency chain:**

1. **GAP-01** — Tag the release commit
   - `git tag v0.1.0 && git push origin v0.1.0`
   - Blocks: nothing. Unblocks: version-pinned install, marketplace check.
   - **Do this first.** It has no dependencies and unblocks consumer install.

2. **GAP-02** — Create `.apm/instructions/library.instructions.md`
   - Populate with content from `build/agent-library-0.1.0/instructions/library.instructions.md` (or author fresh).
   - Blocks: `apm compile` for gemini + opencode targets.
   - **Dependency:** None. Can be done in parallel with GAP-03.

3. **GAP-03** — Create `.apm/agents/marketplace-listings.agent.md`
   - Must include YAML frontmatter with `name: marketplace-listings` and `description`.
   - Blocks: agent shipping in build output.
   - **Dependency:** None. Can be done in parallel with GAP-02.

4. **GAP-04** — Regenerate build from source
   - `apm install && apm compile && apm pack`
   - **Dependency:** GAP-02 and GAP-03 must be resolved first (source primitives must exist before rebuilding).
   - After this step, `build/` output is consistent with source and lockfile.

### Phase 2: Improve Manifest Quality (MEDIUM)

Sequential or parallel (all independent of each other):

5. **GAP-06** — Update `apm.yml` description
6. **GAP-08** — Add `scripts.start` to `apm.yml`
7. **GAP-09** — Expand `targets` list to include `all` or enumerate all 9 targets

### Phase 3: Fix Documentation (MEDIUM + LOW)

8. **GAP-05** — Update README directory structure to reflect reality
9. **GAP-12** — Fix README `docs/` description

### Phase 4: Add Automation + Polish (MEDIUM + LOW)

10. **GAP-11** — Add frontmatter to `marketplace-listings.agent.md` (resolved automatically when GAP-03 is done correctly)
11. **GAP-10** — Re-run `apm install` to generate `local_deployed_file_hashes` in lockfile
12. **GAP-07** — Add `.github/workflows/apm-ci.yml` with `apm audit --ci`, `apm compile --validate`, `apm pack --check-clean`
13. **GAP-13** — Optionally add `.gem-team.yaml`

### Suggested Sequencing Diagram

```
Phase 1 (sequential):
  GAP-01 ─────────────────────────────────────────► (unblocks consumer install)
  GAP-02 ──┐
           ├──► GAP-04 (rebuild)
  GAP-03 ──┘

Phase 2 (parallel):
  GAP-06 ──┬──► GAP-08 ──┬──► (manifest quality)
           └──► GAP-09 ──┘

Phase 3 (parallel):
  GAP-05 ──┬──► (docs accuracy)
  GAP-12 ──┘

Phase 4 (parallel):
  GAP-11 (auto-resolved by GAP-03)
  GAP-10 ──┬──► GAP-07 (CI) ──► GAP-13 (optional)
```

---

## 4. Pre-Flight Checklist

Every condition below must be **YES** for a consumer to successfully run `apm install dbensmith/agent-library#v0.1.0` and receive a complete, functional package.

| # | Condition | Current | What to Verify |
|---|---|---|---|
| 1 | Git tag `v0.1.0` exists on the remote | **NO** | `git ls-remote --tags origin | grep v0.1.0` — must return a matching tag. If absent, `apm install dbensmith/agent-library#v0.1.0` will fail. |
| 2 | `.apm/instructions/` directory exists with at least one `.instructions.md` file | **NO** | `ls .apm/instructions/*.instructions.md` — must list at least `library.instructions.md`. Without it, `apm compile` produces empty output for gemini and opencode targets. |
| 3 | `.apm/agents/` directory contains all agent `.agent.md` files shipped in build output | **NO** | `diff <(ls .apm/agents/) <(ls build/*/agents/)` — must match. Any agent in build without a source file will be lost on next rebuild. |
| 4 | `apm compile` runs without errors for all declared targets | **UNVERIFIED** | `apm compile --validate` exits 0. Verify GEMINI.md and AGENTS.md are regenerated with correct content. |
| 5 | `apm.lock.yaml` is committed and lists all deployed files with hashes | **PARTIAL** | `grep local_deployed_file_hashes apm.lock.yaml` — should return a non-empty block. Local file hashes are currently absent (GAP-10). |
| 6 | `apm audit --ci` passes with no findings | **UNVERIFIED** | Run `apm audit --ci` — must exit 0. Detects hidden Unicode, stale deployed files, and drift between deployed tree and lockfile. |
| 7 | `apm pack` produces a `build/` directory with no missing skills, agents, or instructions vs the lockfile and source tree | **NO** | Build currently has 8 skills (lockfile has 9), orphaned agents, and instructions without source. After GAP-02/GAP-03/GAP-04 are resolved, verify build skill count == lockfile skill count (9). |
| 8 | `README.md` directory structure section accurately reflects the repository layout | **NO** | README claims `.apm/instructions/`, `.apm/prompts/`, and populated `docs/` exist. None are true. Consumer following README will be misled. |

---

## 5. Appendix — Supporting Evidence

### 5.1 Gap-to-Spec Cross-Reference

| Gap ID | Research Digest Requirement Violated | APM Spec Section |
|---|---|---|
| GAP-01 | §6.1 — Tag format `^v?\d+\.\d+\.\d+`; §6.2 — Tag publishing workflow; §7.1 — Version specifier `#v0.1.0` resolution | [Manifest Schema §4.1.1](https://microsoft.github.io/apm/reference/manifest-schema/#411-string-form); [Versioning strategies](https://microsoft.github.io/apm/producer/versioning-strategies/) |
| GAP-02 | §2.2 — `.apm/instructions/` subdirectory; §4.1 — `apm compile` scope; §4.2 — Compile required for non-copilot targets | [Compile your package](https://microsoft.github.io/apm/producer/compile/); [Package anatomy](https://microsoft.github.io/apm/concepts/package-anatomy/#the-apm-directory) |
| GAP-03 | §2.2 — `.apm/agents/` subdirectory; §2.3 — `.agent.md` extension; §2.4 — Canonical layout for marketplace | [Pack a bundle — Source layout](https://microsoft.github.io/apm/producer/pack-a-bundle/#source-layout-and-install-time-discovery) |
| GAP-04 | §5.3 — Bundle integrity at install time; §5.4 — Empty bundle prevention | [Pack a bundle — Integrity](https://microsoft.github.io/apm/producer/pack-a-bundle/#integrity-how-install-verifies-the-bundle) |
| GAP-05 | §13 item 13 — README.md at repo root | General accuracy |
| GAP-06 | §1.3 — `description` field quality | [Manifest Schema §3.3](https://microsoft.github.io/apm/reference/manifest-schema/#33-description) |
| GAP-07 | §10.2 — CI drift check; §10.3 — GitHub Action | [CI/CD pipelines](https://microsoft.github.io/apm/integrations/ci-cd/) |
| GAP-08 | §1.9 — `scripts` section | [Manifest Schema §3.8](https://microsoft.github.io/apm/reference/manifest-schema/#38-scripts) |
| GAP-09 | §1.6 — `targets` declaration; §11.1 — Targets matrix | [Manifest Schema §3.6](https://microsoft.github.io/apm/reference/manifest-schema/#36-target); [Targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/) |
| GAP-10 | §8.1 — `local_deployed_file_hashes` | [Lockfile spec](https://microsoft.github.io/apm/reference/lockfile-spec/) |
| GAP-11 | §2.3 — `.agent.md` format with YAML frontmatter | [Pack a bundle — Source layout](https://microsoft.github.io/apm/producer/pack-a-bundle/#source-layout-and-install-time-discovery) |
| GAP-12 | General accuracy | N/A (documentation quality) |
| GAP-13 | APM producer best practices | N/A (optional) |

### 5.2 Compliance Summary Matrix (Current State)

| # | Requirement | Class | Status |
|---|---|---|---|
| 1 | `apm.yml` exists with `name` and `version` | MUST | ✅ `name: agent-library`, `version: 0.1.0` |
| 2 | `version` matches `^\d+\.\d+\.\d+` | MUST | ✅ `0.1.0` |
| 3 | `.apm/` directory exists (`.apm/` package layout) | MUST | ✅ `.apm/skills/` exists |
| 4 | Primitive files use correct extensions | MUST | ✅ 4 skills use `SKILL.md`; ⚠️ instructions/agents source missing |
| 5 | `apm compile` succeeds (for non-copilot targets) | MUST | ❌ Blocked by GAP-02 |
| 6 | `apm.lock.yaml` committed to repo | MUST | ✅ Present at repo root |
| 7 | Deployed files committed to repo | MUST | ✅ `.agents/` tree present |
| 8 | Git tags follow semver `v?\d+\.\d+\.\d+` | MUST | ❌ Zero tags (GAP-01) |
| 9 | `apm audit` passes | SHOULD | ⚠️ Not run — no CI (GAP-07) |
| 10 | `includes` field declared | SHOULD | ✅ `includes: auto` |
| 11 | `description` populated | SHOULD | ⚠️ Placeholder text (GAP-06) |
| 12 | `targets:` declared | SHOULD | ⚠️ Only 3 of 9 (GAP-09) |
| 13 | `README.md` at repo root | SHOULD | ⚠️ Present but inaccurate (GAP-05, GAP-12) |
| 14 | `apm pack` produces valid `plugin.json` bundle | MUST | ⚠️ Stale build (GAP-04); will work after rebuild |

### 5.3 Key Documentation URLs

| Resource | URL |
|---|---|
| APM Homepage | https://microsoft.github.io/apm/ |
| Quickstart | https://microsoft.github.io/apm/quickstart/ |
| Producer Ramp | https://microsoft.github.io/apm/producer/ |
| Compile your Package | https://microsoft.github.io/apm/producer/compile/ |
| Preview and Validate | https://microsoft.github.io/apm/producer/preview-and-validate/ |
| Pack a Bundle | https://microsoft.github.io/apm/producer/pack-a-bundle/ |
| Versioning Strategies | https://microsoft.github.io/apm/producer/versioning-strategies/ |
| Manifest Schema | https://microsoft.github.io/apm/reference/manifest-schema/ |
| Lockfile Spec | https://microsoft.github.io/apm/reference/lockfile-spec/ |
| Package Types | https://microsoft.github.io/apm/reference/package-types/ |
| Targets Matrix | https://microsoft.github.io/apm/reference/targets-matrix/ |
| Package Anatomy | https://microsoft.github.io/apm/concepts/package-anatomy/ |
| CI/CD Integrations | https://microsoft.github.io/apm/integrations/ci-cd/ |

---

*Generated from `research-digest.md` (vetted APM spec requirements) and `gap-analysis.md` (file-by-file audit). All factual claims cross-referenced against live repository state as of 2026-06-25.*
