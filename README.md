# Agent Library

A centralized repository for AI agent instructions, skills, prompts, and documentation.

## How to Use This Library

### Standard Usage
- **Instructions**: Copy content from `instructions/` into your agent's System Instructions.
- **Skills**: Use `activate_skill [skill-name]` for any skill folder in `skills/`.

---

## Configuration: Linking Gemini to this Library

To make this library natively accessible to your Gemini CLI, follow these steps to link it to your global configuration.

### 1. Trust the Library Path
Gemini must trust the directory where the library is located.
Open your `trustedFolders.json` (usually in `~/.gemini/`) and add the absolute path to this repository:
```json
{
  "C:\\Users\\YourUser": "TRUST_FOLDER",
  "Z:\\agent-library": "TRUST_FOLDER"
}
```

### 2. Link the Library Components
Use directory junctions (Windows) or symlinks (macOS/Linux) to map the library folders into your `.gemini` directory.

#### Windows (PowerShell)
```powershell
$LibraryPath = "Z:\agent-library" # Change to your local path

# Link Skills and Instructions
New-Item -ItemType Junction -Path "$HOME\.gemini\skills" -Value "$LibraryPath\skills"
New-Item -ItemType Junction -Path "$HOME\.gemini\instructions" -Value "$LibraryPath\instructions"
```

#### macOS / Linux
```bash
LIBRARY_PATH="/path/to/agent-library" # Change to your local path

# Link Skills and Instructions
ln -s "$LIBRARY_PATH/skills" "$HOME/.gemini/skills"
ln -s "$LIBRARY_PATH/instructions" "$HOME/.gemini/instructions"
```

### 3. Configure the Global Entry Point
Create or update `~/.gemini/GEMINI.md` to provide the agent with context about this library:

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
- `instructions/`: High-level system instructions and personas.
- `skills/`: Tool definitions and specialized agent capabilities (each in its own folder).
- `prompts/`: Reusable prompt templates.
- `docs/`: Architecture patterns and general configuration guides.

## License
MIT