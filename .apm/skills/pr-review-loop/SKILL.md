---
name: pr-review-loop
description: "Iterative PR review loop: fetch review feedback, fix, reply to AND resolve every conversation,
 then trigger the next review for the correct reviewer and repeat until zero unresolved.
 Cross-platform stdlib-only helper scripts/pr-review-loop.py (gh→API, else GitHub MCP tools).
 NOTE: `/gemini review` stops working 2026-07-17 (Gemini GitHub reviews end); route to the reviewer you answered instead."
---

# pr-review-loop

Loop: fetch feedback → fix → **reply to every conversation** → **resolve every
conversation** → trigger the next review for the reviewer you answered → repeat
until none unresolved. Drive it with
`.agents/skills/pr-review-loop/scripts/pr-review-loop.py` (Python 3, stdlib-only,
runs on Linux/macOS/Windows). Keep replies and commits terse — this is a loop;
tokens matter.

## Start here: `pr-review-loop.py doctor`

Run once, first. Never assume auth/tool state; never tell the user "I can't
authenticate" without it. It prints a verdict and, in a cloud Claude Code
container, **skips straight to MCP without a network call** (cheap):

```text
os=…  env=cloud-claude-code|generic  recommend=mcp|api
api=gh|api|none  token=present|absent  git_remote=ssh|https
```

- `recommend=api` → use the script's gh/API path directly.
- `recommend=mcp` → API egress is blocked or absent; use the GitHub MCP tools
  (below). `doctor --probe` adds a live `api_check=` (200 ok · 401 bad token ·
  403/407 blocked → MCP) when you want proof. API auth (token) and git-push auth
  (SSH key vs HTTPS) are **separate** — a working API can still fail to push.
  Confirmed live in a cloud container: both REST and GraphQL 403 even with a
  present token — `"GitHub access is not enabled for this session"` (REST) and
  `"This GraphQL query is not enabled for this session — only the pinned set of
  PR-review operations is served"` (GraphQL). Don't debug that as an auth bug —
  it's the expected signature for "must use MCP here," and `doctor` already
  told you so before you spent a call finding out.

## Backends (suggested priority, auto-selected — not enforced)

1. **`gh` CLI** if authenticated. (mise: `export PATH="$HOME/.local/share/mise/shims:$PATH"`.)
2. **GitHub MCP tools** (`mcp__github__*`) — the working path in the cloud
   container, where `gh` is absent and the API is egress-blocked.
3. **Direct API** via Python stdlib `urllib` + `GH_TOKEN`/`GITHUB_TOKEN`.
4. **`git`** for commit/push only.

The script auto-picks gh→API. **Resolving a conversation always needs the
GraphQL `resolveReviewThread` mutation** — there is no plain `gh` subcommand or
REST endpoint for it, so any path (gh, curl, MCP) must call GraphQL or a wrapper.
Confirm your MCP toolset exposes `resolve_review_thread` and
`add_reply_to_pull_request_comment` before relying on it; if not, resolve via
GraphQL through whatever backend `doctor` says works.

## Guardrails — reply to AND resolve every conversation (do this unprompted)

The top failure in this loop is fixing code but never answering the threads.
Every iteration, for **every** unresolved thread, **without being asked**:
**reply** (what changed + commit SHA) **then resolve**. Never resolve without a
reply; never leave a replied thread unresolved. `reply-resolve` does both.

**"conversation" ≠ "comment":** a *conversation* is GitHub's resolvable review
thread (the "Resolve conversation" button) — the thing this loop closes. Users
say "comment" when they mean *conversation*. So when asked to handle "comments"/
"feedback"/"the review", **assume it may mean conversations and check both**:
enumerate resolvable review threads AND any standalone PR/issue comments, and
address all of them.

**Check for a concurrent session on the same PR before every fix-and-push.**
Long-lived self-scheduled loops (`send_later`/Routines) persist independently
of whatever spawned this run — a PR can have more than one autonomous agent
watching it (e.g. the session that originally opened the PR, still running its
own hourly check-in, plus a separately-scheduled review-loop run). Before
fixing anything: `git fetch` and diff against your last-known HEAD — if it
moved without you, another session already acted; re-read the *current*
thread/reply state instead of trusting what you fixed last time, skip threads
someone else already answered, and don't post a second `/gemini review` on top
of a trigger someone else just posted (check recent PR comments first — a
duplicate trigger call wastes a review round or wedges the loop waiting on two
in-flight reviews). If you find a concurrent session actively driving the same
branch, prefer standing down over racing it — a lost `git push` (non-fast-forward)
is recoverable, a stepped-on `/gemini review` cadence or duplicated reply isn't.

## The loop

```bash
SKILL=.agents/skills/pr-review-loop/scripts/pr-review-loop.py   # run from repo root
python3 "$SKILL" doctor                 # once, first
python3 "$SKILL" count   <pr>           # 0 => done
python3 "$SKILL" threads <pr>           # [{t,id,by,path,body}]
# fix, then ./run-tests.sh, then commit & push:
git add -A && git commit -m "fix: <what>" && git push origin <branch>
python3 "$SKILL" reply-resolve <pr> <id> <t> "Done — <what> in <sha>."   # per thread
python3 "$SKILL" trigger <pr> <by>      # by = the thread's author
# wait ~3m, repeat until count = 0 and no review pending
```

Keys: `t`=thread id (resolve), `id`=comment id (reply), `by`=author (routing).
On Windows use `python` instead of `python3`.

## Trigger routing — start the next round for the reviewer you answered

Use the thread's `by` (or a name below), not a blanket `/gemini review`. Trigger
syntax drifts — if a bot isn't matched, read its own PR comment footer (usually
`@<bot> help`). Top agentic reviewers on GitHub:

| Reviewer (`by`) | `trigger` name | Action |
| --- | --- | --- |
| `gemini-code-assist[bot]` | `gemini` | `/gemini review` — **only before 2026-07-17** (halt below) |
| `copilot-pull-request-reviewer[bot]` | `copilot` | re-request review (or `request_copilot_review` MCP tool) |
| `claude[bot]` | `claude` | `@claude review` |
| `coderabbitai[bot]` | `coderabbit` | `@coderabbitai review` |
| `qodo-merge-pro[bot]` / `codiumai-pr-agent[bot]` | `qodo` | `/review` |
| `sourcery-ai[bot]` | `sourcery` | `@sourcery-ai review` |
| `cursor[bot]` (Bugbot) | `cursor` | `bugbot run` |
| `greptile-apps[bot]` | `greptile` | `@greptile review` |
| `codegen-sh[bot]` | `codegen` | `@codegen review` |
| `ellipsis-dev[bot]` | `ellipsis` | `@ellipsis review` |
| A human (the user running this agent) | `user` | reply in the agent session, no bot comment, then `mcp__github__subscribe_pr_activity(owner,repo,pr)` |

**No match?** A new push usually re-triggers a bot review automatically (you may
already be done); else check the bot's comment footer for its command, or
re-request its review via the reviewers API. If it's a human, use `user`.

### HARD STOP: `/gemini review` ends 2026-07-17

Google **permanently ends Gemini code reviews on GitHub on 2026-07-17**. On/after
that date `/gemini review` does nothing and hangs the loop forever, so this
action **MUST halt**: never post it — route to the reviewer you answered
(Copilot, Claude, CodeRabbit, …) or `user`. The script enforces this (`trigger
<pr> gemini` refuses on/after `HALT_DATE`); do not hand-post it around the refusal.

## MCP fallback (when `doctor` says `recommend=mcp`)

Same loop via `mcp__github__*`: `pull_request_read` (list threads/comments) →
`add_reply_to_pull_request_comment` (reply) → resolve (wraps the GraphQL
mutation) → `add_issue_comment` (post trigger) / `request_copilot_review`
(Copilot) → `subscribe_pr_activity` (watch for the next round). Guardrails and
routing above apply identically.

**Resolve tool name varies by MCP server version** — confirmed both exist in
the wild, use whichever ToolSearch surfaces:
`mcp__github__resolve_review_thread(threadId)` on some servers, or
`mcp__github__pull_request_review_write(method:"resolve_thread", threadId, owner,
repo, pullNumber)` on others (`owner`/`repo`/`pullNumber` are accepted but
unused by that method — only `threadId` does anything). Don't assume the name
from this doc; check what's actually loaded before the first call fails.

## Notes

- Run lint and tests as per repo specifications and git hooks before committing.
- Conventional commits: `fix: <desc>`. Override: `PR_REPO=owner/repo`, `PR_REVIEW_TODAY=YYYY-MM-DD`.
- `pr-review-loop.py help` lists every command.
