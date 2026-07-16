# Agent Library

A centralized repository for AI agent instructions, skills, and agents. Consume this package using the [Agent Package Manager (APM)](https://microsoft.github.io/apm/).

## Install

Add this package to your project's `apm.yml`:

```yaml
dependencies:
  apm:
    - dbensmith/agent-library
```

Then run `apm install`. APM deploys primitives to your configured targets (Copilot, Claude, OpenCode, Gemini, etc.).

### Install Specific Skills

Use virtual subdirectory references to install individual skills without the full package:

```yaml
dependencies:
  apm:
    - dbensmith/agent-library/skills/git-commit
    - dbensmith/agent-library/skills/home-assistant-env
```

### Pin a Version

Append `#<ref>` to pin to a tag, branch, or commit:

```yaml
dependencies:
  apm:
    - dbensmith/agent-library#v0.1.0
```

See the [APM consumer documentation](https://microsoft.github.io/apm/consumer/) for full reference on dependency management, updates, and authentication.

## Package Contents

- **Skills** (`.apm/skills/`): Reusable agent capabilities (each in its own folder)
- **Instructions** (`.apm/instructions/`): System instructions for agent behavior
- **Agents** (`.apm/agents/`): Agent definitions with metadata

## Repository Layout

**Source (committed):**
- `.apm/` — Published primitives (skills, instructions, agents)

**Generated (gitignored):**
- `.agents/`, `.claude/`, `.opencode/` — Deployed runtime config (created by `apm install`)
- `build/` — Packed bundle (created by `apm pack`)
- `apm_modules/` — Installed dependencies

## License

MIT
