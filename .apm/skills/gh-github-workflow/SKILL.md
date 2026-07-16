---
name: gh-github-workflow
description: 'Workflow for git, GitHub, and gh CLI interactions. Use when committing, branching, opening issues/PRs, viewing repos, or any GitHub operation via the gh CLI. Includes path resolution for the mise-installed gh binary and repo context.'
---

### Instructions

This environment may have:

- `gh` CLI installed via **mise**, NOT in default `PATH`
- Git protocol: **SSH** (`git@github.com:...`)
- Token scopes: `admin:public_key`, `gist`, `read:org`, `repo`

### Workflow

**Always do these three things first, in one batch, before any gh/git operation:**

1. Resolve `gh` and confirm auth:

   ```bash
   export PATH="$HOME/.local/share/mise/shims:$PATH"
   gh auth status
   ```

2. Verify the binary resolves: `type gh`.

3. Confirm repo context with `gh repo view --json nameWithOwner`.

**Do NOT** call `which gh` — mise-managed binaries are not on the default `PATH`.

### Common operations

**Open an issue with a long body from a file (preferred over `--body` for >2 paragraphs):**

```bash
gh issue create \
  --title "Short imperative title" \
  --body-file docs/tmp/issue-body.md
```

**Open a PR:**

```bash
gh pr create \
  --base main \
  --head <branch> \
  --title "type(scope): description" \
  --body-file docs/tmp/pr-body.md
```

**View issue/PR:**

```bash
gh issue view <number> --comments
gh pr view <number> --comments
```

**List/filter:**

```bash
gh issue list --state open --label bug
gh pr list --state open --author @me
```

### Git operations

**Inspect state before any commit/PR/merge:**

```bash
git status
git diff
git log --oneline -10
git remote -v
```

**Branch hygiene:** name pattern is `feature/`, `bugfix/`, `hotfix/`, `release/`, `chore/` (see `conventional-branch` skill). Current branch name is in `git branch --show-current`.

**Never** use `git commit --amend` to fix a failing hook — fix and make a new commit. **Never** skip hooks (`--no-verify`). **Never** force-push without explicit user instruction.

**Conventional commits:** see `conventional-commit` skill. Format: `type(scope): description`.

### Issue/PR body file pattern

For issues/PRs with structured content, write the body to `docs/tmp/issue-*.md` or `docs/tmp/pr-*.md` first, then:

```bash
gh issue create --title "..." --body-file docs/tmp/issue-<slug>.md
```

This keeps the body out of argv (avoids quoting issues) and lets the user review the file before submission.

### Secrets handling

**Never** include plaintext secrets in `--body`, issue text, PR descriptions, or commit messages. The 1Password workflow uses `op` CLI + OPCS/Service Account auth — do not paste resolved secret values into GitHub. See AGENTS.md "Never resolve a 1Password secret to plaintext" rule.

### Gotchas

- `gh` path can change if mise upgrades gh. Always re-resolve if `gh: command not found` appears.
- Token scope is `repo` (not `public_repo` only) — private repos work.
- `gh issue create` with `--body` (inline) loses newlines on some shells. Use `--body-file` for anything multi-line.
- Check for repo-specific pre-commit/CI steps and run them before opening the PR to catch breakage early.
- `gh auth status` returns verbose output — pipe to `head -5` for the quick "logged in?" check.
