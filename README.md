# Agent Library

A centralized repository for AI agent instructions, skills, prompts, and documentation.

## Directory Structure

- `instructions/` — High-level system instructions and personas
- `skills/` — Specialized agent capabilities (each in its own folder with a `SKILL.md`)
- `prompts/` — Reusable prompt templates
- `docs/` — Architecture patterns and general guides

## Getting Started

### Instructions

Instructions define an agent's persona, capabilities, and behavioral rules. To use one:

1. Open the desired file in `instructions/` (e.g., `marketplace-listings.md`).
2. Copy its content into your agent's system prompt or persona field.
3. Use `instructions/template.md` as a starting point for new instructions.

### Skills

Skills are self-contained capabilities that extend an agent with specialized workflows. Each skill lives in its own folder with a `SKILL.md` file.

1. Copy `skills/make-skill-template/` and rename it to your skill name (e.g., `skills/my-skill/`).
2. Edit `SKILL.md` — update the YAML frontmatter (`name`, `description`) and the Markdown body.
3. See `instructions/agent-skills.instructions.md` for the full specification, resource bundling, and best practices.

## Platform Compatibility

Instructions and skills are written in Markdown and work across multiple AI agent platforms.

### Gemini CLI

| Type         | Location                                                                   |
| ------------ | -------------------------------------------------------------------------- |
| Instructions | Paste into `~/.gemini/GEMINI.md` (global) or `.gemini/GEMINI.md` (project) |
| Skills       | Copy folder to `~/.gemini/skills/<name>/` or `.gemini/skills/<name>/`      |

### GitHub Copilot

| Type          | Location                                                                   |
| ------------- | -------------------------------------------------------------------------- |
| Instructions  | Paste into `.github/copilot-instructions.md` (repo-wide)                   |
| Path-specific | Create `.github/instructions/<name>.instructions.md` with YAML frontmatter |
| Skills        | Copy folder to `.github/skills/<name>/`                                    |

### Other Agents

Any agent that accepts Markdown system prompts can use these files directly. Copy the content into the agent's instruction or persona field.

## License

[MIT](./LICENSE.md)
