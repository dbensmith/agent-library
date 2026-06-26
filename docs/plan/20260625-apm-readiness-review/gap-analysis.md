# APM Readiness Gap Analysis — `dbensmith/agent-library`

**Plan ID:** `20260625-apm-readiness-review`
**Review Date:** 2026-06-25
**Reviewer:** Automated audit agent (REVIEWER role)
**Repository:** `dbensmith/agent-library` on branch `humble-spider`
**APM Version:** 0.16.1 (lockfile generation) / v0.16.1–v0.21.0 (spec reference)

---

## 1. Introduction

### 1.1 Scope & Methodology

This audit performs a file-by-file and directory-by-directory comparison of the `.apm/` source tree against the `build/agent-library-0.1.0/` output, validated against the APM Packaging Specification documented in `research-digest.md`. The audit covers:

- **Manifest conformance** (`apm.yml`) against the APM manifest schema (§1 of the research digest)
- **Lockfile integrity** (`apm.lock.yaml`) — deployed files vs `.agents/` tree on disk
- **Plugin metadata** (`plugin.json`) — schema conformance
- **AGENTS.md traceability** — source references back to `.apm/`
- **README.md accuracy** — claimed vs actual directory/file existence
- **`.apm/` source inventory** — primitive completeness
- **`.agents/` runtime tree** — lockfile consistency
- **`build/agent-library-0.1.0/`** — diff against `.apm/` source; orphaned files
- **Git state** — tags, branches, remote configuration
- **Config files** — presence/absence of CI/CD, linting, and editor config

### 1.2 Assumptions About Unresolved Questions

The following are treated as known facts per the task definition and have **not** been re-verified:

| Assumption | Rationale |
|---|---|
| `build/agent-library-0.1.0/instructions/library.instructions.md` exists in build but `.apm/instructions/` source is absent | Treated as HIGH-severity — `apm compile` will fail on fresh run. Build directory assumed stale or manually constructed. |
| `build/agent-library-0.1.0/agents/marketplace-listings.agent.md` exists but no `.apm/agents/` source | Agent intended to ship but source location unknown. Treated as HIGH-severity. |
| Build output is from a prior, possibly manual, `apm pack` run | Build contains `review-and-refactor` gap (present in lockfile, absent from build). Timestamp mismatch with lockfile generation (2026-06-03). |

### 1.3 Severity Rubric

| Severity | Consumer Impact | Producer Impact |
|---|---|---|
| **CRITICAL** | Blocks `apm install` — consumer cannot install at all | N/A |
| **HIGH** | Degraded but installable | Blocks `apm compile` / `apm pack` — producer cannot build |
| **MEDIUM** | Spec violation with workaround — works but non-compliant | Warning or best-practice gap |
| **LOW** | Cosmetic / non-blocking | Docs, formatting, nice-to-haves |

---

## 2. Gap Overview

| ID | Severity | Category | Title |
|---|---|---|---|
| GAP-01 | **CRITICAL** | Git Tags | Zero git tags — blocks version-pinned install |
| GAP-02 | **HIGH** | Source Tree | Missing `.apm/instructions/` source — blocks `apm compile` |
| GAP-03 | **HIGH** | Source Tree | Missing `.apm/agents/` source — agent shipped without source |
| GAP-04 | **HIGH** | Build Integrity | Build output is stale — missing `review-and-refactor` skill, contains orphaned files |
| GAP-05 | **MEDIUM** | Documentation | README.md references non-existent directories |
| GAP-06 | **MEDIUM** | Manifest | `apm.yml` description is generic placeholder text |
| GAP-07 | **MEDIUM** | CI/CD | No `.github/workflows/` directory — no CI pipeline |
| GAP-08 | **MEDIUM** | Manifest | No `scripts` section in `apm.yml` |
| GAP-09 | **MEDIUM** | Manifest | `targets` list incomplete — omits codex, claude, cursor |
| GAP-10 | **LOW** | Lockfile | `local_deployed_file_hashes` absent from lockfile |
| GAP-11 | **LOW** | Build Output | `marketplace-listings.agent.md` missing YAML frontmatter block |
| GAP-12 | **LOW** | Docs | README "Directory Structure" section is misleading about `docs/` content |
| GAP-13 | **LOW** | Config | No `.gem-team.yaml` — team configuration absent |

**Total gaps:** 13 (1 CRITICAL, 3 HIGH, 5 MEDIUM, 4 LOW)

---

## 3. Detailed Gap Analysis

### GAP-01 — Zero Git Tags (CRITICAL)

- **Spec reference:** Research Digest §6.1, §6.2; Manifest Schema §4.1.1
- **Finding:** `git tag --list` returns **no output**. Zero tags exist on any branch.
- **Evidence:**
  ```
  $ git tag --list
  (no output)
  ```
- **Impact on consumer:** Consumers cannot pin to a version. `apm install dbensmith/agent-library#v0.1.0` will **fail** — no tag matching `v0.1.0` or `0.1.0` exists. The only working install is `dbensmith/agent-library` (resolves `latest` on `main`, pinning a floating commit SHA).
- **Impact on producer:** Blocks marketplace publishing. `apm marketplace check` will exit non-zero. The `version: 0.1.0` in `apm.yml` is effectively unverifiable.
- **Fix guidance:**
  ```bash
  git tag v0.1.0
  git push origin v0.1.0
  ```
  Tag must be on the release commit. For pre-release, use `v0.1.0-beta.1`.

---

### GAP-02 — Missing `.apm/instructions/` Source (HIGH)

- **Spec reference:** Research Digest §2.2, §4.1, §4.2; Package Anatomy; Compile your Package
- **Finding:** `.apm/` contains only `skills/`. There is no `.apm/instructions/` directory. However:
  - `AGENTS.md` line 9 declares: `<!-- Source: local .apm/instructions/library.instructions.md -->`
  - `build/agent-library-0.1.0/instructions/library.instructions.md` exists with content
  - `apm compile` reads instructions from `.apm/instructions/` — it **will fail or produce empty output** on a fresh run
- **Evidence (AGENTS.md line 9):**
  ```
  <!-- Source: local .apm/instructions/library.instructions.md -->
  ```
- **Evidence (directory listing):**
  ```
  $ find .apm -type f -o -type d | sort
  .apm
  .apm/skills
  .apm/skills/home-assistant-env/SKILL.md
  .apm/skills/marketplace-listings/SKILL.md
  .apm/skills/organize-tax-docs-canada/SKILL.md
  .apm/skills/uv/SKILL.md
  ```
  No `.apm/instructions/` directory or `.instructions.md` file exists.
- **Impact on consumer:** Copilot target may still function (compile is optional for copilot per §4.2) but gemini and opencode targets declared in `apm.yml` **require** compile output.
- **Impact on producer:** `apm compile` cannot produce root context files (GEMINI.md, AGENTS.md with embedded instructions). `apm compile --validate` will report missing primitive.
- **Fix guidance:** Create `.apm/instructions/library.instructions.md` with the content currently in `build/agent-library-0.1.0/instructions/library.instructions.md`. Then re-run `apm compile`.

---

### GAP-03 — Missing `.apm/agents/` Source (HIGH)

- **Spec reference:** Research Digest §2.2, §2.4; Canonical layout for marketplace publishers
- **Finding:** `build/agent-library-0.1.0/agents/marketplace-listings.agent.md` exists (64 lines, functional agent definition) but there is **no** `.apm/agents/` directory in the source tree.
- **Evidence (build directory):**
  ```
  $ find build -type f -o -type d | sort
  ...
  build/agent-library-0.1.0/agents/marketplace-listings.agent.md
  ```
- **Evidence (source tree):** `.apm/` contains only `skills/`.
- **Impact on producer:** `apm pack` cannot reproduce the current build output. The agent file is orphaned in `build/` — any future `apm pack` run will omit it.
- **Impact on consumer:** If the agent is intended to ship, consumers will not receive it after the next build.
- **Fix guidance:** Create `.apm/agents/marketplace-listings.agent.md` with the agent definition. Per spec §2.3, the file extension must be `.agent.md`. Must include YAML frontmatter (`---` delimiters) with at minimum a `name` and `description` field.

---

### GAP-04 — Build Output is Stale / Inconsistent (HIGH)

- **Spec reference:** Research Digest §5.3 (Bundle integrity); §5.4 (Empty bundle prevention)
- **Finding:** The `build/agent-library-0.1.0/` output is inconsistent with the lockfile and source tree:

  | Artifact | Lockfile | Build Output | Mismatch |
  |---|---|---|---|
  | Skills deployed | 9 skills | 8 skills | `review-and-refactor` missing from build |
  | Instructions | N/A (compile output) | `instructions/library.instructions.md` present | Present in build, no source |
  | Agents | N/A | `agents/marketplace-listings.agent.md` present | Present in build, no source |

- **Evidence (lockfile skills):** `local_deployed_files` lists 4 local + 5 dependency skills = 9 total
- **Evidence (build skills):** 8 subdirectories under `build/agent-library-0.1.0/skills/`
- **Impact on producer:** `apm pack` on a fresh `apm install` will produce different output than what currently exists in `build/`. Bundle integrity verification at install time would reject the stale build.
- **Impact on consumer:** N/A (build/ is producer artifact).
- **Fix guidance:** Resolve GAP-02 and GAP-03 first. Then run `apm install` to refresh `.agents/`, followed by `apm compile` and `apm pack` to regenerate `build/` from current state.

---

### GAP-05 — README.md References Non-Existent Directories (MEDIUM)

- **Spec reference:** Research Digest §13 item 13 (README.md at repo root recommended); General accuracy
- **Finding:** README.md lines 95–98 claim:
  ```
  - `.apm/instructions/`: High-level system instructions and personas.
  - `.apm/skills/`: Tool definitions and specialized agent capabilities...
  - `.apm/prompts/`: Reusable prompt templates.
  - `docs/`: Architecture patterns and general configuration guides.
  ```
  **Ground truth:**
  - `.apm/instructions/` → does **not** exist
  - `.apm/skills/` → exists ✓
  - `.apm/prompts/` → does **not** exist
  - `docs/` → exists but contains only `plan/20260625-apm-readiness-review/` — no "architecture patterns and general configuration guides"
- **Impact on consumer:** Misleading. A consumer following the README will try to copy from `.apm/instructions/` or `.apm/prompts/` and find nothing.
- **Fix guidance:** Either create the missing directories with content, or update README to reflect current state. Remove references to `.apm/prompts/` if no prompts are planned.

---

### GAP-06 — `apm.yml` Description is Generic Placeholder (MEDIUM)

- **Spec reference:** Research Digest §1.3; Manifest Schema §3.3
- **Finding:** `apm.yml` line 3 reads:
  ```yaml
  description: APM project for agent-library
  ```
  This is the scaffold default — not descriptive of the library's actual purpose.
- **Evidence (apm.yml line 3):** `description: APM project for agent-library`
- **Impact on consumer:** `apm view` and `apm search` display this description. It adds no value.
- **Impact on producer:** `apm pack` warns when description is generic/missing.
- **Fix guidance:** Replace with a meaningful description, e.g.:
  ```yaml
  description: Centralized library of AI agent instructions, skills, and tool definitions for copilot, gemini, and opencode targets.
  ```

---

### GAP-07 — No CI/CD Pipeline (MEDIUM)

- **Spec reference:** Research Digest §10 (CI/CD Expectations); §10.2, §10.3
- **Finding:** No `.github/workflows/` directory exists. No CI pipeline configured.
- **Evidence:**
  ```
  $ find .github -type f 2>/dev/null
  (no output — directory does not exist)
  ```
- **Impact on consumer:** No automated drift check (`apm audit --ci`). Consumers may encounter stale deployed files.
- **Impact on producer:** No automated `apm pack --check-clean` or `apm marketplace check` in CI. Manual gates required before each release.
- **Fix guidance:** Add a GitHub Actions workflow using `microsoft/apm-action` (spec §10.3). Minimum: run `apm compile --validate`, `apm audit --ci`, `apm pack --check-clean`.

---

### GAP-08 — No `scripts` Section in `apm.yml` (MEDIUM)

- **Spec reference:** Research Digest §1.9; Manifest Schema §3.8
- **Finding:** `apm.yml` line 16 reads:
  ```yaml
  scripts: {}
  ```
  No `start` or other entry point scripts defined.
- **Evidence (apm.yml line 16):** `scripts: {}`
- **Impact on consumer:** No one-command entry point. Consumer must know which primitives to load and how.
- **Impact on producer:** `apm pack` warns. Reduces publish quality score.
- **Fix guidance:** Add a `start` script that activates the primary instructions, e.g.:
  ```yaml
  scripts:
    start: "apm compile && echo 'Library ready. Skills available in .agents/skills/'"
  ```

---

### GAP-09 — `targets` List Incomplete (MEDIUM)

- **Spec reference:** Research Digest §1.6; Manifest Schema §3.6; Targets Matrix §11.1
- **Finding:** `apm.yml` lines 17–20 declare only three targets:
  ```yaml
  targets:
    - copilot
    - gemini
    - opencode
  ```
  Missing: `codex`, `claude`, `cursor`, `antigravity`, `windsurf`, `kiro`. The library is a general-purpose agent library; omitting targets limits discoverability.
- **Impact on consumer:** Install on non-declared targets may still work if primitives are compatible, but tool-specific optimizations (e.g. `.cursor/` rules) will not be generated.
- **Impact on producer:** `apm compile` generates output only for declared targets.
- **Fix guidance:** Add all compatible targets. If all targets are supported, use:
  ```yaml
  targets:
    - all
  ```

---

### GAP-10 — `local_deployed_file_hashes` Absent from Lockfile (LOW)

- **Spec reference:** Research Digest §8.1; Lockfile Spec
- **Finding:** `apm.lock.yaml` includes `local_deployed_files` (lines 50–54) but does **not** include `local_deployed_file_hashes`.
- **Evidence:** Full lockfile (54 lines) — no `local_deployed_file_hashes` key present.
- **Impact:** Minor. Integrity verification relies on dependency hashes (present for all 5 deps) but not for local files. `apm audit` drift detection still works.
- **Fix guidance:** Re-run `apm install` to regenerate lockfile with hashes, or manually add SHA-256 hashes for each local deployed file.

---

### GAP-11 — Build Agent File Missing Frontmatter (LOW)

- **Spec reference:** Research Digest §2.3; Primitive file naming conventions (`.agent.md` format)
- **Finding:** `build/agent-library-0.1.0/agents/marketplace-listings.agent.md` starts directly with Markdown content:
  ```
  1: # Facebook Marketplace Listing Agent
  ```
  No YAML frontmatter block (`---` delimiters) is present.
- **Evidence (build/agent-library-0.1.0/agents/marketplace-listings.agent.md line 1):** `# Facebook Marketplace Listing Agent`
- **Impact on consumer:** APM may fail to parse metadata (name, description) from the agent file, causing it to appear nameless in target tool UIs.
- **Fix guidance:** Add frontmatter block at the top:
  ```yaml
  ---
  name: marketplace-listings
  description: Drafts Facebook Marketplace listings and automates posting via browser injection.
  ---
  ```

---

### GAP-12 — README `docs/` Description Misleading (LOW)

- **Spec reference:** General accuracy
- **Finding:** README line 98 claims `docs/` contains "Architecture patterns and general configuration guides." In reality, `docs/` contains only `plan/20260625-apm-readiness-review/` (this audit).
- **Impact:** Minor. Consumer looking for architecture docs will find nothing.
- **Fix guidance:** Either add actual documentation content to `docs/`, or update the README to accurately describe what `docs/` contains.

---

### GAP-13 — No `.gem-team.yaml` Team Config (LOW)

- **Spec reference:** APM producer best practices; team configuration
- **Finding:** No `.gem-team.yaml` file at repository root. All config defaults apply.
- **Impact:** Minor. Team metadata (team name, members, ownership) not declared. Not blocking for any APM operation.
- **Fix guidance:** Add `.gem-team.yaml` if team-level configuration is desired. Optional.

---

## 4. Source vs Build Comparison

### 4.1 Files in Build But NOT in `.apm/` Source

| File in `build/agent-library-0.1.0/` | Expected Source Location | Status |
|---|---|---|
| `instructions/library.instructions.md` | `.apm/instructions/library.instructions.md` | Source file **missing** (GAP-02) |
| `agents/marketplace-listings.agent.md` | `.apm/agents/marketplace-listings.agent.md` | Source directory **missing** (GAP-03) |
| `plugin.json` | Root `plugin.json` (synthesized by `apm pack`) | Normal — expected in build |
| `skills/find-docs/SKILL.md` | N/A (dependency) | Normal — from lockfile dep |
| `skills/gh-cli/SKILL.md` | N/A (dependency) | Normal — from lockfile dep |
| `skills/git-commit/SKILL.md` | N/A (dependency) | Normal — from lockfile dep |
| `skills/make-repo-contribution/SKILL.md` | N/A (dependency) | Normal — from lockfile dep |
| `skills/make-repo-contribution/assets/*` | N/A (dependency) | Normal — from lockfile dep |
| `skills/home-assistant-env/SKILL.md` | `.apm/skills/home-assistant-env/SKILL.md` | Normal — source exists ✓ |
| `skills/marketplace-listings/SKILL.md` | `.apm/skills/marketplace-listings/SKILL.md` | Normal — source exists ✓ |
| `skills/organize-tax-docs-canada/SKILL.md` | `.apm/skills/organize-tax-docs-canada/SKILL.md` | Normal — source exists ✓ |
| `skills/uv/SKILL.md` | `.apm/skills/uv/SKILL.md` | Normal — source exists ✓ |

### 4.2 Files in Source But NOT in Build

| Source File | Expected in Build? | Status |
|---|---|---|
| `.apm/skills/home-assistant-env/SKILL.md` | Yes — `skills/home-assistant-env/SKILL.md` | Present ✓ |
| `.apm/skills/marketplace-listings/SKILL.md` | Yes — `skills/marketplace-listings/SKILL.md` | Present ✓ |
| `.apm/skills/organize-tax-docs-canada/SKILL.md` | Yes — `skills/organize-tax-docs-canada/SKILL.md` | Present ✓ |
| `.apm/skills/uv/SKILL.md` | Yes — `skills/uv/SKILL.md` | Present ✓ |

### 4.3 Skills in Lockfile But NOT in Build

| Skill | Lockfile Status | Build Status |
|---|---|---|
| `review-and-refactor` | Deployed (dependency, in `.agents/skills/`) | **Missing** from `build/agent-library-0.1.0/skills/` |

This confirms the build is stale and predates the lockfile or was manually constructed.

---

## 5. Git State Summary

| Property | Value |
|---|---|
| Current branch | `humble-spider` (feature branch) |
| Default branch | `main` |
| Remote URL | `git@github.com:dbensmith/agent-library.git` |
| Tags | **None** (0 tags) |
| Behind `main` | 0 commits (feature branch is at or ahead of `main`) |
| Latest commit | `35f6f0c` — `docs: refactor README for Antigravity 2.0 CLI and IDE transition` |
| Lockfile commit | `ee8384e` — `chore: migrate skills to remote APM dependencies (#1)` |
| Working tree | Clean (only `docs/` untracked — this audit output) |

---

## 6. Manifest Conformance Check

### 6.1 `apm.yml` — Schema Compliance

| Field | Required | Present | Value | Status |
|---|---|---|---|---|
| `name` | MUST | Yes | `agent-library` | ✓ Conforms (alphanumeric, dots, hyphens) |
| `version` | MUST | Yes | `0.1.0` | ✓ Matches `^\d+\.\d+\.\d+` |
| `description` | SHOULD | Yes | `APM project for agent-library` | ⚠ Generic placeholder (GAP-06) |
| `author` | SHOULD | Yes | `dbensmith` | ⚠ Plain string; prefers structured `{name}` |
| `license` | SHOULD | **Not in apm.yml** | (present in `plugin.json` as MIT) | ⚠ License declared in plugin.json but not apm.yml |
| `targets` | SHOULD | Yes | `[copilot, gemini, opencode]` | ⚠ Incomplete — only 3 of 9 targets (GAP-09) |
| `includes` | SHOULD (MUST for governance) | Yes | `auto` | ✓ Conforms |
| `type` | Advisory | **Not present** | N/A | ✓ Optional |
| `scripts` | SHOULD | Yes | `{}` (empty) | ⚠ Empty — no `start` script (GAP-08) |
| `dependencies` | N/A (conditional) | Yes | 5 remote skill deps | ✓ All resolve |
| `devDependencies` | N/A (conditional) | Yes | `apm: []` (empty) | ✓ Conforms |

### 6.2 `apm.lock.yaml` — Schema Compliance

| Field | Required | Present | Value | Status |
|---|---|---|---|---|
| `lockfile_version` | Yes | Yes | `'1'` | ✓ Git-only (no registry deps) |
| `generated_at` | Yes | Yes | `2026-06-03T02:17:03.772381+00:00` | ✓ ISO 8601 UTC |
| `apm_version` | No | Yes | `0.16.1` | ✓ Diagnostic |
| `dependencies` | Yes | Yes | 5 entries | ✓ All with `repo_url`, `resolved_commit`, `deployed_files` |
| `mcp_servers` | No | **Not present** | N/A | ✓ Optional |
| `lsp_servers` | No | **Not present** | N/A | ✓ Optional |
| `local_deployed_files` | No | Yes | 4 entries | ✓ Matches `.agents/skills/` local files |
| `local_deployed_file_hashes` | No | **Not present** | N/A | ⚠ Absent (GAP-10) |
| `pack` | No | **Not present** | N/A | ✓ Only in bundled lockfiles |

### 6.3 `plugin.json` — Schema Compliance

| Field | Required | Present | Value | Status |
|---|---|---|---|---|
| `name` | Yes (for plugin format) | Yes | `agent-library` | ✓ Matches `apm.yml` |
| `version` | APM synthesizes | Yes | `0.1.0` | ✓ Matches `apm.yml` |
| `description` | Recommended | Yes | `APM project for agent-library` | ⚠ Same generic text as apm.yml |
| `author` | Recommended | Yes | `{"name": "Benjamin Smith"}` | ✓ Structured object |
| `license` | Recommended | Yes | `MIT` | ✓ SPDX expression |

---

## 7. `.apm/` Source Tree vs Spec Completeness

### 7.1 Primitive Inventory

| Primitive Type | Spec Directory | Source Exists? | Files | Status |
|---|---|---|---|---|
| Instructions | `.apm/instructions/` | **No** | N/A | ❌ GAP-02 |
| Skills | `.apm/skills/<name>/SKILL.md` | **Yes** | 4 skills | ✓ All have valid frontmatter (name matches dir) |
| Prompts | `.apm/prompts/` | **No** | N/A | ⚠ README claims it exists (GAP-05) |
| Agents | `.apm/agents/` | **No** | N/A | ❌ GAP-03 |
| Chatmodes | `.apm/chatmodes/` | **No** | N/A | ✓ Optional |
| Context | `.apm/context/` | **No** | N/A | ✓ Optional |
| Hooks | `.apm/hooks/` | **No** | N/A | ✓ Optional |

### 7.2 Skill Frontmatter Validation (Spec §3.3)

| Skill | `name` field | Matches dir? | `description` present? | ASCII-only? |
|---|---|---|---|---|
| `home-assistant-env` | `home-assistant-env` | ✓ | ✓ | ✓ |
| `marketplace-listings` | `marketplace-listings` | ✓ | ✓ | ✓ |
| `organize-tax-docs-canada` | `organize-tax-docs-canada` | ✓ | ✓ | ✓ |
| `uv` | `uv` | ✓ | ✓ | ✓ |

All 4 source skills pass frontmatter validation. ✓

---

## 8. `.agents/` Runtime Tree vs Lockfile Consistency

| Skill | In `.agents/skills/`? | In lockfile `local_deployed_files`? | In lockfile `dependencies`? | Status |
|---|---|---|---|---|
| `home-assistant-env` | ✓ | ✓ (line 51) | — | ✓ Local, consistent |
| `marketplace-listings` | ✓ | ✓ (line 52) | — | ✓ Local, consistent |
| `organize-tax-docs-canada` | ✓ | ✓ (line 53) | — | ✓ Local, consistent |
| `uv` | ✓ | ✓ (line 54) | — | ✓ Local, consistent |
| `git-commit` | ✓ | — | ✓ (line 7) | ✓ Dependency, consistent |
| `make-repo-contribution` | ✓ | — | ✓ (line 15) | ✓ Dependency, consistent |
| `review-and-refactor` | ✓ | — | ✓ (line 23) | ✓ Dependency, consistent |
| `find-docs` | ✓ | — | ✓ (line 32) | ✓ Dependency, consistent |
| `gh-cli` | ✓ | — | ✓ (line 41) | ✓ Dependency, consistent |

✓ All 9 skills in `.agents/skills/` are accounted for in the lockfile. Lockfile ↔ `.agents/` tree is consistent.

---

## 9. Config File Inventory

| File | Present | Purpose | Notes |
|---|---|---|---|
| `.editorconfig` | ✓ | Editor settings | 17 lines, UTF-8, LF, 2-space indent |
| `.prettierrc` | ✓ | Code formatting | 20 lines, 120-char print width, md override |
| `.commitlintrc.json` | ✓ | Commit message linting | Conventional commits, 100-char header max |
| `.markdownlint.jsonc` | ✓ | Markdown linting | 400-char line length, fenced code style |
| `.markdownlintignore` | ✓ | Lint exclusions | Ignores `node_modules` |
| `.gitignore` | ✓ | Git exclusions | Excludes `node_modules/`, `.env`, `apm_modules/` |
| `.gem-team.yaml` | ✗ | Team metadata | Not present (GAP-13) |
| `.github/workflows/` | ✗ | CI/CD pipelines | Not present (GAP-07) |
| `marketplace.yml` | ✗ | Marketplace registry | Not present (no coexistence conflict with apm.yml) ✓ |
| `.claude-plugin/` | ✗ | Marketplace artifacts | Not present (not a marketplace publisher) |
| `docs/` | ✓ | Documentation | Only contains `plan/20260625-apm-readiness-review/` |

---

## 10. Prioritized Remediation Plan

| Order | Gap ID | Action | Blocks |
|---|---|---|---|
| **1** | GAP-01 | `git tag v0.1.0 && git push origin v0.1.0` | Consumers pinning to version |
| **2** | GAP-02 | Create `.apm/instructions/library.instructions.md` | `apm compile` for non-copilot targets |
| **3** | GAP-03 | Create `.apm/agents/marketplace-listings.agent.md` with frontmatter | Agent shipping in build |
| **4** | GAP-04 | Re-run `apm install && apm compile && apm pack` | Build output integrity |
| **5** | GAP-06 | Update `apm.yml` description | Marketplace listing quality |
| **6** | GAP-08 | Add `scripts.start` to `apm.yml` | Consumer entry point |
| **7** | GAP-09 | Expand `targets` list | Cross-tool compatibility |
| **8** | GAP-05 | Update README.md to remove non-existent directories | Documentation accuracy |
| **9** | GAP-11 | Add frontmatter to `marketplace-listings.agent.md` | Agent metadata parsing |
| **10** | GAP-10 | Re-run `apm install` to generate `local_deployed_file_hashes` | Lockfile completeness |
| **11** | GAP-07 | Add `.github/workflows/apm-ci.yml` | Automated CI gating |
| **12** | GAP-12 | Update or populate `docs/` | Documentation accuracy |
| **13** | GAP-13 | Add `.gem-team.yaml` (optional) | Team metadata |

---

## 11. Conclusion

The repository has a **working foundation**: `apm.yml` is structurally valid, 4 skills are correctly authored with valid frontmatter, the lockfile is internally consistent with the deployed `.agents/` tree, and `apm install` succeeds for consumers using the unqualified `dbensmith/agent-library` reference.

However, the repository is **not release-ready** due to:

1. **CRITICAL — zero git tags** preventing version-pinned installs (GAP-01).
2. **3 HIGH-severity gaps** that will cause `apm compile` / `apm pack` to fail or produce incomplete output (GAP-02, GAP-03, GAP-04).

The build directory appears to be a stale or manually-constructed artifact that does not reflect the current lockfile state. The top 4 remediation actions (tags, instructions source, agents source, rebuild) should be completed before any release attempt.
