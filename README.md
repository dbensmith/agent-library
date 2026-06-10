# Agent Library

A centralized repository for AI agent instructions, skills, prompts, and documentation.

## How to Use This Library

### Via APM (Recommended)

You can consume this repository directly using the [Agent Package Manager (APM)](https://microsoft.github.io/apm/). Add the following to your project's `apm.yml`:

```yaml
dependencies:
  apm:
    - dbensmith/agent-library
```

Then run `apm install`.

### Standard Usage

- **Instructions**: Copy content from `.apm/instructions/` into your agent's System Instructions.
- **Skills**: Use `activate_skill [skill-name]` for any skill folder in `.apm/skills/`.

---

## Configuration: Linking Antigravity to this Library

To make this library natively accessible to Antigravity CLI and Antigravity IDE (Antigravity 2.0), follow these steps to link it to your global configuration.

### 1. Trust the Library Path

Antigravity must trust the directory where the library is located.
Open the `settings.json` file for your Antigravity tool:

- **Antigravity CLI**: `~/.gemini/antigravity-cli/settings.json`
- **Antigravity IDE**: `~/.gemini/antigravity-ide/settings.json`

Add the absolute path of this repository to the `trustedWorkspaces` array:

```json
{
  "trustedWorkspaces": ["C:\\Users\\YourUser\\some-workspace", "Z:\\agent-library"]
}
```

### 2. Link the Library Components

Use directory junctions (Windows) or symlinks (macOS/Linux) to map the library folders into your global Antigravity configuration directory `.gemini`.

#### Windows (PowerShell)

```powershell
$LibraryPath = "Z:\agent-library" # Change to your local path

# Link Skills and Instructions
New-Item -ItemType Junction -Path "$HOME\.gemini\skills" -Value "$LibraryPath\.apm\skills"
New-Item -ItemType Junction -Path "$HOME\.gemini\instructions" -Value "$LibraryPath\.apm\instructions"
```

#### macOS / Linux

```bash
LIBRARY_PATH="/path/to/agent-library" # Change to your local path

# Link Skills and Instructions
ln -s "$LIBRARY_PATH/.apm/skills" "$HOME/.gemini/skills"
ln -s "$LIBRARY_PATH/.apm/instructions" "$HOME/.gemini/instructions"
```

### 3. Configure the Global Entry Point

Create or update the global entry point file `~/.gemini/GEMINI.md` (which is loaded by both Antigravity CLI and IDE) to provide the agent with context about this library:

```markdown
# Agent Context & Library

## Repository

- **Agent Library**: [Path to this repo]
- **Contains**: System instructions, reusable skills, and prompt templates.

## Instructions

- Refer to the linked `instructions/` directory for task-specific personas.

## Skills

- Use `activate_skill [skill-name]` for any skill located in the linked `skills/` directory.
```

---

## Directory Structure

- `.apm/instructions/`: High-level system instructions and personas.
- `.apm/skills/`: Tool definitions and specialized agent capabilities (each in its own folder).
- `.apm/prompts/`: Reusable prompt templates.
- `docs/`: Architecture patterns and general configuration guides.

## License

MIT
