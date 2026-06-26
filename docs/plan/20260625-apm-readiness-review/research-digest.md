# APM Packaging Specification — Requirement Checklist

> **Research digest for Plan ID: 20260625-apm-readiness-review**
> Generated from APM documentation at microsoft.github.io/apm/ (v0.16.1–v0.21.0 era).
> All citations reference specific APM documentation URLs as required.

---

## Legend

| Label | Meaning |
|-------|---------|
| **MUST** | Blocking for `apm install` to succeed. Absent or invalid → hard failure. |
| **SHOULD** | Advisory. Won't block install but degrades consumer experience or CI gating. |

---

## 1. Manifest Schema Requirements (`apm.yml`)

### 1.1. `name` — REQUIRED
- **Classification:** MUST
- **Type:** `string`, free-form, no pattern enforced. Convention: alphanumeric, dots, hyphens, underscores.
- **Source:** [Manifest Schema §3.1](https://microsoft.github.io/apm/reference/manifest-schema/#31-name)
- **Validated by:** `apm install` parse-time. Missing → hard error.

### 1.2. `version` — REQUIRED
- **Classification:** MUST
- **Type:** `string`, must match `^\d+\.\d+\.\d+` (semver). Pre-release/build suffixes allowed. Non-matching produces validation warning (non-blocking).
- **Source:** [Manifest Schema §3.2](https://microsoft.github.io/apm/reference/manifest-schema/#32-version)
- **Validated by:** `apm install` parse-time. Missing → hard error.

### 1.3. `description` — OPTIONAL but strongly recommended
- **Classification:** SHOULD
- **Type:** Brief human-readable string. Rendered by `apm view`, `apm search`, `apm deps list`.
- **Source:** [Manifest Schema §3.3](https://microsoft.github.io/apm/reference/manifest-schema/#33-description)
- **Note:** `apm pack` warns when `description` is missing.

### 1.4. `author` — OPTIONAL
- **Classification:** SHOULD
- **Type:** Plain string (`"Jane Doe"` → `{name: "Jane Doe"}`) or structured object `{name, email?, url?}`.
- **Source:** [Manifest Schema §3.4](https://microsoft.github.io/apm/reference/manifest-schema/#34-author); [Pack a bundle](https://microsoft.github.io/apm/producer/pack-a-bundle/#the-pluginjson-contract)

### 1.5. `license` — OPTIONAL
- **Classification:** SHOULD
- **Type:** SPDX license expression (e.g. `MIT`, `Apache-2.0`). Recorded verbatim in consumer lockfile as `declared_license`. Omitted → SBOM marks unknown.
- **Source:** [Manifest Schema §3.5](https://microsoft.github.io/apm/reference/manifest-schema/#35-license)

### 1.6. `target` / `targets` — OPTIONAL
- **Classification:** SHOULD
- **Values:** `copilot`, `claude`, `cursor`, `opencode`, `codex`, `gemini`, `antigravity`, `windsurf`, `kiro`, `all`. Prefer plural `targets:` as YAML list.
- **Source:** [Manifest Schema §3.6](https://microsoft.github.io/apm/reference/manifest-schema/#36-target); [Targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/)

### 1.7. `includes` — OPTIONAL but audit-advisory if absent
- **Classification:** MUST for governance; SHOULD otherwise
- **Values:** `auto` (explicit consent), list of repo-relative paths, or omitted (legacy; audit warning). `includes: auto` is default for newly scaffolded projects.
- **Source:** [Manifest Schema §3.9](https://microsoft.github.io/apm/reference/manifest-schema/#39-includes)

### 1.8. `type` — OPTIONAL
- **Classification:** Advisory
- **Values:** `instructions`, `skill`, `hybrid`, `prompts`. Reserves future override; current behavior driven by package content.
- **Source:** [Manifest Schema §3.7](https://microsoft.github.io/apm/reference/manifest-schema/#37-type)

### 1.9. `scripts` — OPTIONAL
- **Classification:** SHOULD (for publishable packages: a `start` entry gives consumers a one-command entry point)
- **Source:** [Manifest Schema §3.8](https://microsoft.github.io/apm/reference/manifest-schema/#38-scripts)

### 1.10. Unknown top-level keys
- **Classification:** Advisory
- **Rule:** Unknown keys MUST be preserved by writers but MAY be ignored by resolvers.
- **Source:** [Manifest Schema §2](https://microsoft.github.io/apm/reference/manifest-schema/#2-document-structure)

---

## 2. `.apm/` Directory Layout

### 2.1. `.apm/` directory must exist (for APM package type)
- **Classification:** MUST (for `.apm/` layout)
- **Source:** [Package types — APM package](https://microsoft.github.io/apm/reference/package-types/#apm-package-apm-directory); [Package anatomy](https://microsoft.github.io/apm/concepts/package-anatomy/#the-apm-directory)
- **Alternative:** Five package layout types exist — the presence of `.apm/`, `SKILL.md` at root, `skills/<name>/SKILL.md`, `hooks/*.json`, or `plugin.json` determines the layout. See §3.

### 2.2. Required vs optional subdirectories under `.apm/`
- **All** subdirectories are **optional**. You may ship any subset:
  - `instructions/` — always-on rules
  - `skills/<name>/SKILL.md` — multi-file capabilities
  - `prompts/` — prompt templates (`.prompt.md`)
  - `agents/` — named agent definitions (`.agent.md`)
  - `chatmodes/` — chat-mode configs (`.chatmode.md`)
  - `context/` — shared context fragments
  - `hooks/` — lifecycle hooks (`.json`)
- **Source:** [Package anatomy — .apm/ directory](https://microsoft.github.io/apm/concepts/package-anatomy/#the-apm-directory)

### 2.3. Primitive file naming conventions
- **Classification:** MUST
- Instructions: `*.instructions.md`
- Prompts: `*.prompt.md`
- Agents: `*.agent.md`
- Chatmodes: `*.chatmode.md`
- Skills: `SKILL.md` (must be named exactly this)
- Hooks: `*.json`
- **Source:** [Pack a bundle — Source layout](https://microsoft.github.io/apm/producer/pack-a-bundle/#source-layout-and-install-time-discovery)

### 2.4. Canonical layout for marketplace publishers
- **Classification:** MUST (for marketplace packages)
- **Rule:** Use `.apm/<type>/` for EVERY primitive type. `apm install` does NOT discover instructions, commands, or prompts placed in root convention directories (e.g. `instructions/` at repo root). Packages relying on these primitives will install silently incomplete.
- **Source:** [Pack a bundle — Canonical layout](https://microsoft.github.io/apm/producer/pack-a-bundle/#canonical-layout-for-marketplace-publishers)

---

## 3. Package Types

### 3.1. Five valid package layouts
- **Classification:** Informational (the layout determines install semantics)
- **Source:** [Package types](https://microsoft.github.io/apm/reference/package-types/)

| Layout | Root Signal | Install Semantic |
|--------|------------|------------------|
| APM package | `.apm/` directory | Hoist each primitive into target runtime dirs |
| Skill bundle | `SKILL.md` at root | Copy entire dir to `<target>/skills/<name>/` |
| Skill collection | `skills/<name>/SKILL.md` | Promote each to `<target>/skills/<name>/` |
| Hook package | `hooks/*.json` only | Deploy to target hooks dir |
| Plugin collection | `plugin.json` | Dissect via plugin artifact mapping |

### 3.2. HYBRID packages (SKILL.md + apm.yml)
- **Classification:** Advisory
- **Rule:** `apm.yml.description` and `SKILL.md` frontmatter `description` are **independent** — APM never merges them. Populate both independently.
- **Source:** [Package types — Metadata model](https://microsoft.github.io/apm/reference/package-types/#metadata-model-hybrid-packages)

### 3.3. Skill collection validation rules
- **Classification:** MUST
- Frontmatter `name` field (if present) must match directory name.
- Frontmatter `description` should be present (warning if absent).
- All frontmatter values must be ASCII-only.
- Directory names must pass path-traversal checks.
- **Source:** [Package types — Skill collection](https://microsoft.github.io/apm/reference/package-types/#skill-collection-skillsnameskillmd)

---

## 4. `apm compile` Requirements

### 4.1. Compile scope
- **Classification:** MUST understand the scope
- **Rule:** `apm compile` only handles **instructions** primitives from `.apm/instructions/` (plus unpacked under `apm_modules/`). It does NOT deploy prompts, skills, agents, hooks, commands, or MCP — those are deployed by `apm install`.
- **Source:** [Compile your package](https://microsoft.github.io/apm/producer/compile/#compile-vs-install)

### 4.2. Compile must succeed (for non-copilot targets)
- **Classification:** MUST
- **Rule:** Compile is **optional for copilot** but **recommended for every other target** (claude, cursor, codex, gemini, antigravity, opencode, windsurf, kiro) — those harnesses load instructions through root context files that compile generates.
- **Source:** [Compile your package — Overview](https://microsoft.github.io/apm/producer/compile/#_top)

### 4.3. Compile validation flag
- **Classification:** SHOULD (pre-publish gate)
- **Rule:** `apm compile --validate` parses every primitive's frontmatter and structure, reporting errors without producing output.
- **Source:** [Preview and validate — apm compile dry-run](https://microsoft.github.io/apm/producer/preview-and-validate/#apm-compile-dry-run)

---

## 5. `apm pack` Requirements

### 5.1. Pack must produce valid output
- **Classification:** MUST
- **Rule:** `apm pack` produces `./build/<name>/` containing `plugin.json`, primitive folders, and embedded `apm.lock.yaml`. Only `name` is required in `plugin.json`; APM synthesizes from `apm.yml` if absent.
- **Source:** [Pack a bundle](https://microsoft.github.io/apm/producer/pack-a-bundle/)

### 5.2. Pack format
- **Classification:** MUST
- **Rule:** Use the default `--format plugin` (not legacy `--format apm`). `apm install` rejects legacy APM bundle layout.
- **Source:** [Pack a bundle — Pitfalls](https://microsoft.github.io/apm/producer/pack-a-bundle/#pitfalls)

### 5.3. Bundle integrity at install time
- **Classification:** MUST (automatic, no config needed)
- **Rule:** `apm install <bundle>` rehashes every file and rejects if: any hash mismatches, any file listed in `pack.bundle_files` is missing, any file present but not in manifest, or any path is a symlink.
- **Source:** [Pack a bundle — Integrity](https://microsoft.github.io/apm/producer/pack-a-bundle/#integrity-how-install-verifies-the-bundle)

### 5.4. Empty bundle prevention
- **Classification:** SHOULD
- **Rule:** If `apm pack` reports "No deployed files found", run `apm install` first — pack uses files from the last install, not raw `.apm/` source tree.
- **Source:** [Pack a bundle — Pitfalls](https://microsoft.github.io/apm/producer/pack-a-bundle/#pitfalls)

---

## 6. Git Tag Conventions for Version Pinning

### 6.1. Tag format for version pinning
- **Classification:** MUST
- **Rule:** Semver tags matched by `^v?\d+\.\d+\.\d+`. Valid formats: `v1.0.0`, `1.0.0` (bare), `v1.0.0-beta.1` (pre-release). When resolving semver ranges, APM matches against `v{version}` and `{name}--v{version}` patterns.
- **Source:** [Manifest Schema §4.1.1 — ref](https://microsoft.github.io/apm/reference/manifest-schema/#411-string-form); [Versioning strategies](https://microsoft.github.io/apm/producer/versioning-strategies/)

### 6.2. Tag publishing workflow
- **Classification:** MUST
- **Rule:** Tag your release commit with the version tag before consumers can pin to it:
  ```
  git tag v1.0.0 && git push --tags
  ```
- **Source:** [Publish to a marketplace — End to end](https://microsoft.github.io/apm/producer/publish-to-a-marketplace/#end-to-end)

### 6.3. Marketplace tag patterns
- **Classification:** MUST (for marketplace publishers)
- **Rule:** Marketplace `build.tagPattern` controls how tags are rendered. Default: `"v{version}"`. Other valid: `"{name}-v{version}"`.
- **Source:** [Versioning strategies — tag_pattern](https://microsoft.github.io/apm/producer/versioning-strategies/#tag_pattern)

---

## 7. `apm install` Version Resolution

### 7.1. Version specifier syntax
- **Classification:** MUST understand
- **Source:** [Manifest Schema §4.1.1](https://microsoft.github.io/apm/reference/manifest-schema/#411-string-form)

| Specifier | Resolution |
|-----------|-----------|
| No qualifier (e.g. `owner/repo`) | Resolves `latest` — lockfile pins commit SHA |
| `#v0.1.0` | Pinned to exact tag (immutable) |
| `#main` | Branch ref (may change over time) |
| `#<commit-sha>` | Matches `^[a-f0-9]{7,40}$` — exact commit |
| `ref: "^1.2.0"` (object form) | Semver range resolved against remote tags |
| `ref: "~1.4"` | Semver range |
| `ref: ">=2.0 <3"` | Compound semver range |

### 7.2. Semver range resolution
- **Classification:** MUST (for range users)
- **Rule:** When `ref:` is a semver range, APM resolves against remote tags matching `v{version}`, `{name}--v{version}`, and bare `{version}` patterns. Selects highest satisfying tag. Lockfile records: `constraint`, `resolved_tag`, `version`, `resolved_commit`, `resolved_at`.
- **Source:** [Manifest Schema §4.1.2 — ref](https://microsoft.github.io/apm/reference/manifest-schema/#412-object-form)

### 7.3. Lockfile generation and committing
- **Classification:** MUST
- **Rule:** `apm install` writes `apm.lock.yaml` at project root. **Always commit it.** This is what makes `apm install --frozen` (CI) reproduce identically.
- **Source:** [Lockfile spec — Location](https://microsoft.github.io/apm/reference/lockfile-spec/#location); [Quickstart — What to commit](https://microsoft.github.io/apm/quickstart/#what-to-commit)

---

## 8. `apm.lock.yaml` Format

### 8.1. Lockfile schema
- **Classification:** MUST (generated automatically)
- **Source:** [Lockfile spec](https://microsoft.github.io/apm/reference/lockfile-spec/)

**Top-level fields:**

| Field | Required | Notes |
|-------|----------|-------|
| `lockfile_version` | yes | `"1"` (Git-only) or `"2"` (registry deps present) |
| `generated_at` | yes | ISO 8601 UTC timestamp |
| `apm_version` | no | Diagnostic only |
| `dependencies` | yes | List of resolved `LockedDependency` entries |
| `mcp_servers` | no | Resolved MCP server names |
| `lsp_servers` | no | Resolved LSP server names |
| `local_deployed_files` | no | Files the project itself contributes |
| `local_deployed_file_hashes` | no | SHA-256 per local file |
| `pack` | no | Only in bundled lockfiles; contains `bundle_files` |

**Per-dependency key fields:**

| Field | Required | Notes |
|-------|----------|-------|
| `repo_url` | yes | Canonical repository path |
| `resolved_commit` | no | Exact 40-char SHA — the pin |
| `resolved_ref` | no | User-supplied ref (`main`, `v1.2.0`, SHA) |
| `version` | no | Resolved semver |
| `package_type` | no | `apm_package`, `skill_bundle`, `claude_skill`, `hook_package`, `hybrid`, `marketplace_plugin` |
| `deployed_files` | no | Project-relative paths APM wrote |
| `deployed_file_hashes` | no | SHA-256 per deployed file |
| `depth` | no | 0=self, 1=direct, 2+=transitive |
| `virtual_path` | no | Subpath for virtual packages |
| `is_dev` | no | `true` for devDependencies |

---

## 9. Validation Gates (`apm preview` / `apm audit`)

### 9.1. Pre-publish verification sequence
- **Classification:** SHOULD (recommended producer workflow)
- **Source:** [Preview and validate](https://microsoft.github.io/apm/producer/preview-and-validate/)

```
apm compile --validate         # 1. Structure check
apm compile --dry-run          # 2. Preview placement
apm view <your-package>        # 3. Confirm metadata
apm outdated                   # 4. Check dep freshness
apm audit                      # 5. Scan + drift
apm pack                       # 6. Ship it
```

### 9.2. `apm audit` security scan
- **Classification:** MUST
- **Rule:** `apm audit` scans every deployed prompt, instruction, skill, and agent for hidden Unicode (zero-width chars, bidi controls, tag characters). Rebuilds deployed context in scratch and diffs against working tree. Use `--ci` for non-zero exit on findings.
- **Source:** [Preview and validate — apm audit](https://microsoft.github.io/apm/producer/preview-and-validate/#apm-audit)

### 9.3. Marketplace check gate
- **Classification:** MUST (for marketplace publishers)
- **Rule:** `apm marketplace check` — every package's ref/range must resolve. Missing tag or unresolvable range exits non-zero.
- **Source:** [Publish to a marketplace — Validate](https://microsoft.github.io/apm/producer/publish-to-a-marketplace/#validate-before-you-ship)

---

## 10. CI/CD Expectations

### 10.1. Commit deployed files + lockfile
- **Classification:** MUST
- **Rule:** Commit `.github/`, `.claude/`, `.cursor/`, `.opencode/`, `.gemini/`, `.windsurf/`, `.kiro/` deployed files alongside `apm.yml` and `apm.lock.yaml`. `apm_modules/` is auto-gitignored.
- **Source:** [Quickstart — What to commit](https://microsoft.github.io/apm/quickstart/#what-to-commit)

### 10.2. CI drift check
- **Classification:** SHOULD
- **Rule:** Run `apm audit --ci` in CI to catch stale deployed files when `apm.yml` updates.
- **Source:** [Integrations — CI/CD pipelines](https://microsoft.github.io/apm/integrations/ci-cd/)

### 10.3. GitHub Action
- **Classification:** SHOULD
- **Rule:** APM provides a GitHub Action (`microsoft/apm-action`) for automated CI workflows.
- **Source:** [APM README — The three promises](https://github.com/microsoft/apm#1-portable-by-manifest)

### 10.4. Marketplace version checks in CI
- **Classification:** SHOULD (for marketplace publishers)
- **Rule:** `apm pack --check-versions` validates local-package version alignment per chosen strategy (`lockstep`, `tag_pattern`, `per_package`). `apm pack --check-clean` ensures working tree is clean.
- **Source:** [Versioning strategies](https://microsoft.github.io/apm/producer/versioning-strategies/)

---

## 11. Targets and Compile Output

### 11.1. Supported targets
- **Classification:** MUST understand the target model
- **Source:** [Targets matrix](https://microsoft.github.io/apm/reference/targets-matrix/)

| Target | Root Context | Deploy Root |
|--------|-------------|-------------|
| copilot | AGENTS.md | `.github/` |
| claude | CLAUDE.md | `.claude/` |
| cursor | — (`.mdc` rules) | `.cursor/` |
| codex | AGENTS.md | `.codex/` + `.agents/` |
| gemini | GEMINI.md | `.gemini/` |
| antigravity | AGENTS.md | `.agents/` |
| opencode | AGENTS.md | `.opencode/` |
| windsurf | AGENTS.md | `.windsurf/` |
| kiro | AGENTS.md | `.kiro/` |

### 11.2. Skills convergence
- **Classification:** Advisory
- **Rule:** By default, skills deploy to `.agents/skills/<name>/SKILL.md` (cross-tool convention). Override with `--legacy-skill-paths` or `APM_LEGACY_SKILL_PATHS=1`.
- **Source:** [Targets matrix — Skills convergence](https://microsoft.github.io/apm/reference/targets-matrix/#skills-convergence)

---

## 12. Marketplace Publishing Requirements (additional)

### 12.1. Marketplace block in apm.yml
- **Classification:** MUST (for marketplace publishers)
- **Key:** Use `packages:` (not `plugins:`) in the `marketplace:` block. The `plugins:` name only appears in the compiled `marketplace.json`.
- **Source:** [Publish to a marketplace — Author the registry](https://microsoft.github.io/apm/producer/publish-to-a-marketplace/#author-the-registry)

### 12.2. Generated marketplace artifacts
- **Classification:** MUST (for marketplace publishers)
- **Rule:** Commit `.claude-plugin/marketplace.json` (default output) and `.agents/plugins/marketplace.json` (if codex output enabled). `*.json` in `.gitignore` will silently skip these — add unignore overrides.
- **Source:** [Publish to a marketplace — What lives where](https://microsoft.github.io/apm/producer/publish-to-a-marketplace/#what-lives-where)

### 12.3. `apm marketplace check` before release
- **Classification:** MUST
- **Rule:** Every package's ref/range must resolve before pushing the release commit.
- **Source:** [Publish to a marketplace — Validate](https://microsoft.github.io/apm/producer/publish-to-a-marketplace/#validate-before-you-ship)

### 12.4. No concurrent `marketplace.yml` + `apm.yml marketplace:` block
- **Classification:** MUST
- **Rule:** Both present is a hard error. Prefer the block; run `apm marketplace migrate` to consolidate.
- **Source:** [Publish to a marketplace — Pitfalls](https://microsoft.github.io/apm/producer/publish-to-a-marketplace/#pitfalls)

---

## 13. Summary Compliance Matrix

| # | Requirement | Class | Validated By | Source |
|---|------------|-------|-------------|--------|
| 1 | `apm.yml` exists with `name` and `version` | MUST | `apm install` parse | [Manifest schema §3.1-3.2](https://microsoft.github.io/apm/reference/manifest-schema/#31-name) |
| 2 | `version` matches `^\d+\.\d+\.\d+` | MUST (warning if not) | Parse-time | [Manifest schema §3.2](https://microsoft.github.io/apm/reference/manifest-schema/#32-version) |
| 3 | `.apm/` directory exists (APM package layout) | MUST | Package type detection | [Package types](https://microsoft.github.io/apm/reference/package-types/#apm-package-apm-directory) |
| 4 | Primitive files use correct extensions (`.instructions.md`, `.prompt.md`, `.agent.md`, `SKILL.md`, etc.) | MUST | `apm compile --validate` / `apm install` | [Pack a bundle — Source layout](https://microsoft.github.io/apm/producer/pack-a-bundle/#source-layout-and-install-time-discovery) |
| 5 | `apm compile` succeeds (for non-copilot targets) | MUST | `apm compile` | [Compile your package](https://microsoft.github.io/apm/producer/compile/) |
| 6 | `apm.lock.yaml` committed to repo | MUST | Manual / CI gate | [Lockfile spec](https://microsoft.github.io/apm/reference/lockfile-spec/#location) |
| 7 | Deployed files (`.github/`, `.claude/`, etc.) committed to repo | MUST | Manual / CI drift check | [Quickstart](https://microsoft.github.io/apm/quickstart/#what-to-commit) |
| 8 | Git tags follow semver `v?.d+.d+.d+` for version pinning | MUST | `git ls-remote` at resolve time | [Manifest schema §4.1.1](https://microsoft.github.io/apm/reference/manifest-schema/#411-string-form) |
| 9 | `apm audit` passes (no hidden Unicode, no drift) | SHOULD (MUST for secure repos) | `apm audit --ci` | [Preview and validate](https://microsoft.github.io/apm/producer/preview-and-validate/#apm-audit) |
| 10 | `includes` field declared (`auto` or explicit list) | SHOULD (MUST if policy requires `explicit-includes`) | `apm audit` | [Manifest schema §3.9](https://microsoft.github.io/apm/reference/manifest-schema/#39-includes) |
| 11 | `description` populated (for `apm view` / marketplace listing) | SHOULD | `apm pack` warning | [Manifest schema §3.3](https://microsoft.github.io/apm/reference/manifest-schema/#33-description) |
| 12 | `targets:` declared in `apm.yml` | SHOULD | `apm compile` target detection | [Manifest schema §3.6](https://microsoft.github.io/apm/reference/manifest-schema/#36-target) |
| 13 | `README.md` at repo root (rendered on marketplace listing) | SHOULD | Marketplace UI | [Producer overview](https://microsoft.github.io/apm/producer/) |
| 14 | `apm pack` produces valid `plugin.json` bundle | MUST (for distribution) | `apm pack` | [Pack a bundle](https://microsoft.github.io/apm/producer/pack-a-bundle/) |
| 15 | Marketplace: `packages:` (not `plugins:`) in `apm.yml` | MUST (for marketplace) | `apm pack` | [Publish to a marketplace](https://microsoft.github.io/apm/producer/publish-to-a-marketplace/#author-the-registry) |
| 16 | Marketplace: `apm marketplace check` passes before release | MUST (for marketplace) | CI / pre-push | [Publish to a marketplace — Validate](https://microsoft.github.io/apm/producer/publish-to-a-marketplace/#validate-before-you-ship) |
| 17 | Marketplace: commit generated `marketplace.json` | MUST (for marketplace) | CI gate | [Publish to a marketplace — What lives where](https://microsoft.github.io/apm/producer/publish-to-a-marketplace/#what-lives-where) |
| 18 | No `marketplace.yml` + `apm.yml marketplace:` block coexistence | MUST (for marketplace) | Parse-time error | [Publish to a marketplace — Pitfalls](https://microsoft.github.io/apm/producer/publish-to-a-marketplace/#pitfalls) |
| 19 | CI pipeline runs `apm audit --ci` / drift check | SHOULD | CI | [CI/CD pipelines](https://microsoft.github.io/apm/integrations/ci-cd/) |
| 20 | All primitives under `.apm/<type>/` for marketplace packages (not root convention dirs) | MUST (for marketplace) | `apm pack --dry-run --verbose` | [Pack a bundle — Canonical layout](https://microsoft.github.io/apm/producer/pack-a-bundle/#canonical-layout-for-marketplace-publishers) |

---

## Appendix: Key Documentation URLs Referenced

| Page | URL |
|------|-----|
| APM Homepage | https://microsoft.github.io/apm/ |
| Quickstart | https://microsoft.github.io/apm/quickstart/ |
| Producer Ramp | https://microsoft.github.io/apm/producer/ |
| Compile | https://microsoft.github.io/apm/producer/compile/ |
| Preview and Validate | https://microsoft.github.io/apm/producer/preview-and-validate/ |
| Pack a Bundle | https://microsoft.github.io/apm/producer/pack-a-bundle/ |
| Publish to a Marketplace | https://microsoft.github.io/apm/producer/publish-to-a-marketplace/ |
| Versioning Strategies | https://microsoft.github.io/apm/producer/versioning-strategies/ |
| Manifest Schema | https://microsoft.github.io/apm/reference/manifest-schema/ |
| Lockfile Spec | https://microsoft.github.io/apm/reference/lockfile-spec/ |
| Package Types | https://microsoft.github.io/apm/reference/package-types/ |
| Targets Matrix | https://microsoft.github.io/apm/reference/targets-matrix/ |
| Primitive Types | https://microsoft.github.io/apm/reference/primitive-types/ |
| Package Anatomy | https://microsoft.github.io/apm/concepts/package-anatomy/ |
| GitHub Repository | https://github.com/microsoft/apm |
