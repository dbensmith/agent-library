#!/usr/bin/env python3
"""pr-review-loop.py — PR review-loop actions. Cross-platform (Linux/macOS/Windows), stdlib-only.

Backend auto-selected (not enforced): gh (if authed) -> GitHub REST/GraphQL via urllib (+token).
In a cloud Claude Code container the GitHub API is egress-blocked -> use the GitHub MCP tools.
Run `doctor` first: it tells you which path works so you never guess auth state.
"""
import datetime as _dt
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

HALT_DATE = "2026-07-17"          # Gemini GitHub reviews end permanently; /gemini review halts here.
API = "https://api.github.com"
_BACKEND = None
_TOKEN = None

# Top agentic reviewers on GitHub -> next-round trigger. (login/keyword substring, label, kind, command)
# kind: halt=comment but stops on HALT_DATE, rerequest=re-request review (no comment cmd), comment=post command.
# Bot command syntax drifts — if unsure, read the bot's own PR comment footer (usually "@<bot> help").
BOTS = [
    ("gemini",     "Gemini Code Assist", "halt",      "/gemini review"),
    ("copilot",    "GitHub Copilot",     "rerequest", "copilot-pull-request-reviewer[bot]"),
    ("claude",     "Claude",             "comment",   "@claude review"),
    ("coderabbit", "CodeRabbit",         "comment",   "@coderabbitai review"),
    ("qodo",       "Qodo Merge",         "comment",   "/review"),
    ("codium",     "Qodo/PR-Agent",      "comment",   "/review"),
    ("pr-agent",   "PR-Agent",           "comment",   "/review"),
    ("sourcery",   "Sourcery",           "comment",   "@sourcery-ai review"),
    ("cursor",     "Cursor Bugbot",      "comment",   "bugbot run"),
    ("greptile",   "Greptile",           "comment",   "@greptile review"),
    ("codegen",    "Codegen",            "comment",   "@codegen review"),
    ("ellipsis",   "Ellipsis",           "comment",   "@ellipsis review"),
    ("bito",       "Bito",               "comment",   "/review"),
]


def die(msg, code=1):
    sys.stderr.write(f"pr-review-loop: {msg}\n")
    sys.exit(code)


def _run(args, inp=None):
    if args and args[0] == "gh":
        resolved = shutil.which("gh")
        if resolved:
            args = [resolved] + args[1:]
    return subprocess.run(args, input=inp, capture_output=True, text=True, encoding="utf-8")


def today():
    return os.environ.get("PR_REVIEW_TODAY") or _dt.date.today().isoformat()


def is_cloud():
    """Cloud Claude Code container? Then GitHub API egress is policy-gated -> prefer MCP."""
    if os.path.isdir("/root/.ccr"):
        return True
    if any(k in os.environ for k in ("CLAUDECODE", "CLAUDE_CODE_CONTAINER_ID", "CCR_AGENT_PROXY_ENABLED")):
        return True
    return "42371" in os.environ.get("HTTPS_PROXY", "")


def have_gh():
    return bool(shutil.which("gh")) and _run(["gh", "auth", "status"]).returncode == 0


def token():                                         # cached: avoid a `gh auth token` subprocess per request
    global _TOKEN
    if _TOKEN is None:
        _TOKEN = ""
        for v in ("GH_TOKEN", "GITHUB_TOKEN"):
            if os.environ.get(v):
                _TOKEN = os.environ[v]
                break
        else:
            if shutil.which("gh"):
                r = _run(["gh", "auth", "token"])
                if r.returncode == 0 and r.stdout.strip():
                    _TOKEN = r.stdout.strip()
    return _TOKEN


def backend():
    global _BACKEND
    if _BACKEND is None:
        _BACKEND = "gh" if have_gh() else ("api" if token() else "none")
    return _BACKEND


def slug():
    val = os.environ.get("PR_REPO")
    if not val and shutil.which("gh"):
        r = _run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"])
        if r.returncode == 0 and r.stdout.strip():
            val = r.stdout.strip()
    if not val:
        r = _run(["git", "remote", "get-url", "origin"])
        if r.returncode == 0 and r.stdout.strip():
            u = re.sub(r"^.*github\.com[:/]+", "", r.stdout.strip())
            val = re.sub(r"\.git$", "", u).rstrip("/")
    if not val or "/" not in val:                    # guard slug().split("/") downstream
        die("no repo or invalid format: set PR_REPO=owner/repo")
    return val


def _urllib(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API}/{path}", data=data, method=method)
    tok = token()
    if tok:                                          # empty Bearer -> 401 even on public repos
        req.add_header("Authorization", f"Bearer {tok}")
    req.add_header("Accept", "application/vnd.github+json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    ctx = None
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if ca:
        import ssl
        ctx = ssl.create_default_context(cafile=ca)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        raw = r.read().decode("utf-8")
    return json.loads(raw) if raw else None


def _mcp_hint():
    die("no usable API backend (gh unauthed, no token) — use the GitHub MCP tools (mcp__github__*)")


def rest(method, path, body=None):
    b = backend()
    if b == "gh":
        args = ["gh", "api", path, "-X", method]
        inp = None
        if body is not None:
            args += ["--input", "-"]
            inp = json.dumps(body)
        r = _run(args, inp=inp)
        if r.returncode != 0:
            die(f"gh api {method} {path} failed: {(r.stderr or r.stdout).strip()}")
        return json.loads(r.stdout) if r.stdout.strip() else None
    if b == "api":
        try:
            return _urllib(method, path, body)
        except urllib.error.URLError as e:
            details = ""
            if isinstance(e, urllib.error.HTTPError):
                try:
                    details = f" - {e.read().decode()}"
                except Exception:
                    pass
            die(f"API {getattr(e, 'code', 'network error')} on {path} ({e}){details} — run 'doctor'; if blocked, use GitHub MCP tools")
    _mcp_hint()


def graphql(query, variables=None):
    payload = {"query": query, "variables": variables or {}}
    b = backend()
    if b == "gh":
        r = _run(["gh", "api", "graphql", "--input", "-"], inp=json.dumps(payload))
        if r.returncode != 0:
            die(f"gh graphql failed: {(r.stderr or r.stdout).strip()}")
        res = json.loads(r.stdout)
    elif b == "api":
        try:
            res = _urllib("POST", "graphql", payload)
        except urllib.error.URLError as e:
            details = ""
            if isinstance(e, urllib.error.HTTPError):
                try:
                    details = f" - {e.read().decode()}"
                except Exception:
                    pass
            die(f"GraphQL {getattr(e, 'code', 'network error')} ({e}){details} — run 'doctor'; if blocked, use GitHub MCP tools")
    else:
        _mcp_hint()
    if not res or res.get("errors"):
        die(f"GraphQL error: {(res or {}).get('errors') or 'empty response'}")
    return res


# --- commands ---------------------------------------------------------------
def _probe():
    try:
        if backend() == "gh":
            return "200" if _run(["gh", "api", f"repos/{slug()}"]).returncode == 0 else "fail"
        _urllib("GET", f"repos/{slug()}")
        return "200"
    except urllib.error.HTTPError as e:
        return str(e.code)
    except Exception:
        return "000"


def cmd_doctor(args):
    """Ground truth so agents don't guess. Cloud marker -> recommend MCP without a network probe."""
    b, cloud = backend(), is_cloud()
    remote = _run(["git", "remote", "get-url", "origin"]).stdout.strip()
    proto = "ssh" if remote.startswith(("git@", "ssh://")) else ("https" if remote.startswith("https://") else "na")
    recommend = "mcp" if (cloud or b == "none") else "api"
    for k, v in (("os", sys.platform), ("env", "cloud-claude-code" if cloud else "generic"),
                 ("recommend", recommend), ("api", b),
                 ("token", "present" if token() else "absent"), ("git_remote", proto)):
        print(f"{k}={v}")
    if recommend == "mcp":
        print("hint=use GitHub MCP tools (mcp__github__*); confirm these exist before relying on them:")
        print("  read=pull_request_read  reply=add_reply_to_pull_request_comment  resolve=resolve_review_thread")
        print("note=resolving a conversation needs GraphQL resolveReviewThread — no plain gh/REST command; "
              "resolve_review_thread wraps it. If your toolset lacks it, resolve via GraphQL through any working backend.")
    if "--probe" in args and b != "none":
        print(f"api_check={_probe()}")


_Q = ("query($o:String!,$r:String!,$p:Int!){repository(owner:$o,name:$r){pullRequest(number:$p){"
      "reviewThreads(first:100){nodes{id isResolved comments(first:1){nodes{databaseId path author{login} body}}}}}}}")


def _threads(pr):
    o, r = slug().split("/", 1)
    d = graphql(_Q, {"o": o, "r": r, "p": int(pr)})
    repo = (d.get("data") or {}).get("repository")
    if not repo:
        die(f"repo '{o}/{r}' not found or inaccessible")
    pr_data = repo.get("pullRequest")
    if not pr_data:
        die(f"PR #{pr} not found")
    out = []
    for n in (pr_data.get("reviewThreads") or {}).get("nodes") or []:
        if not n or n.get("isResolved"):
            continue
        comments = (n.get("comments") or {}).get("nodes") or []
        if not comments or not comments[0]:
            continue
        c = comments[0]
        out.append({"t": n.get("id"), "id": c.get("databaseId"),
                    "by": (c.get("author") or {}).get("login") or "ghost",
                    "path": c.get("path"), "body": c.get("body")})
    return out


def cmd_threads(a):                                  # unresolved conversations: [{t,id,by,path,body}]
    print(json.dumps(_threads(a[0]), separators=(",", ":")))


def cmd_count(a):                                    # 0 = loop done
    print(len(_threads(a[0])))


def cmd_reply(a):                                    # reply to conversation <id>  (silent on success)
    _ = a[2]                                         # IndexError if body missing
    rest("POST", f"repos/{slug()}/pulls/{a[0]}/comments/{a[1]}/replies", {"body": " ".join(a[2:])})


def cmd_resolve(a):                                  # resolve conversation thread <t>  (needs GraphQL)
    graphql("mutation($t:ID!){resolveReviewThread(input:{threadId:$t}){thread{isResolved}}}", {"t": a[0]})


def cmd_reply_resolve(a):                            # pr id t body — reply THEN resolve (do both, every thread)
    _ = a[3]                                         # IndexError if body missing
    cmd_reply([a[0], a[1], " ".join(a[3:])])
    cmd_resolve([a[2]])


def _post(pr, body):
    rest("POST", f"repos/{slug()}/issues/{pr}/comments", {"body": body})


def cmd_trigger(a):                                  # next review for the reviewer you answered (use thread 'by')
    pr, who = a[0], a[1].lower()
    if who in ("user", "human", "maintainer", "reviewer"):
        sys.stderr.write(f"human reviewer: reply in the agent session (no bot comment), then "
                         f"mcp__github__subscribe_pr_activity(owner,repo,{pr})\n")
        return
    for key, label, kind, cmd in BOTS:
        if key in who:
            if kind == "halt":
                if today() < HALT_DATE:
                    _post(pr, cmd)
                else:
                    die(f"{label} GitHub reviews ended {HALT_DATE} — do NOT post {cmd!r}; "
                        f"route to another reviewer or 'user'")
            elif kind == "rerequest":
                rest("POST", f"repos/{slug()}/pulls/{pr}/requested_reviewers", {"reviewers": [cmd]})
            else:
                _post(pr, cmd)
            return
    sys.stderr.write(
        f"unknown reviewer {who!r}. Options:\n"
        f"  1) a new push usually re-triggers a bot review automatically — you may already be done;\n"
        f"  2) read the bot's PR comment footer for its command (often '@{who} help');\n"
        f"  3) re-request its review via requested_reviewers API (or the reviewer UI);\n"
        f"  if it's a human, use: trigger {pr} user\n")
    sys.exit(1)


HELP = """pr-review-loop.py — PR review-loop actions. Cross-platform, stdlib-only.
backend auto: gh(authed) -> API via urllib(+GH_TOKEN); cloud container -> use GitHub MCP tools.
  doctor [--probe]                     env + backend + auth verdict (run first; --probe = live check)
  threads <pr>                         unresolved conversations: [{t,id,by,path,body}]
  count   <pr>                         # unresolved (0 = done)
  reply   <pr> <id> <body>             reply to conversation <id>
  resolve <t>                          resolve conversation thread <t>  (GraphQL under the hood)
  reply-resolve <pr> <id> <t> <body>   reply THEN resolve (do both, every thread)
  trigger <pr> <reviewer|user>         next review; reviewer = thread 'by' or a name below
keys: t=thread id  id=comment id  by=author | env: PR_REPO GH_TOKEN PR_REVIEW_TODAY
reviewers: gemini copilot claude coderabbit qodo sourcery cursor greptile codegen ellipsis bito (+user)
note: /gemini review halts %s (Gemini GitHub reviews end) — route elsewhere after.
""" % HALT_DATE

CMDS = {"doctor": cmd_doctor, "threads": cmd_threads, "count": cmd_count, "reply": cmd_reply,
        "resolve": cmd_resolve, "reply-resolve": cmd_reply_resolve, "trigger": cmd_trigger}


def main(argv):
    if not argv or argv[0] in ("help", "-h", "--help"):
        print(HELP)
        return
    cmd, rest_args = argv[0], argv[1:]
    fn = CMDS.get(cmd)
    if not fn:
        sys.stderr.write(HELP)
        die(f"unknown command: {cmd}")
    try:
        fn(rest_args)
    except IndexError:
        die(f"missing arguments for '{cmd}' — see: pr-review-loop.py help")
    except ValueError as e:
        die(f"invalid argument: {e}")


if __name__ == "__main__":
    main(sys.argv[1:])
