# Configuring Gemini to use a Centralized Library

This guide explains how to configure the Gemini CLI to point to this repository (or any centralized agent library). This setup allows you to manage instructions and skills in one place while making them natively accessible to the agent.

## Prerequisites
- Gemini CLI installed.
- The `agent-library` repository cloned to a local path (e.g., `Z:\agent-library` or `C:\Repos\agent-library`).

## 1. Trust the Library Path
Gemini must trust the directory where the library is located to execute skills or read files.
```powershell
# Open your trustedFolders.json (usually in ~/.gemini/)
# Add the path to your library
{
  "C:\\Users\\YourUser": "TRUST_FOLDER",
  "Z:\\agent-library": "TRUST_FOLDER"
}
```

## 2. Link the Library Components
Use directory junctions (Windows) or symlinks (macOS/Linux) to map the library folders into your `.gemini` configuration directory. This makes the files appear as if they are part of the local config.

### Windows (PowerShell)
```powershell
# Define your library root
$LibraryPath = "Z:\agent-library"

# Link Skills
New-Item -ItemType Junction -Path "$HOME\.gemini\skills" -Value "$LibraryPath\skills"

# Link Instructions
New-Item -ItemType Junction -Path "$HOME\.gemini\instructions" -Value "$LibraryPath\instructions"
```

### macOS / Linux
```bash
# Define your library root
LIBRARY_PATH="/path/to/agent-library"

# Link Skills
ln -s "$LIBRARY_PATH/skills" "$HOME/.gemini/skills"

# Link Instructions
ln -s "$LIBRARY_PATH/instructions" "$HOME/.gemini/instructions"
```

## 3. Configure the Global Entry Point
Update (or create) `~/.gemini/GEMINI.md`. This file acts as the "brain" for the agent's self-awareness of its tools.

```markdown
# Agent Context & Library

## Repository
- **Agent Library**: [Path to your repo]
- **Contains**: System instructions, reusable skills, and prompt templates.

## Instructions
- Refer to the linked `instructions/` directory for task-specific personas.

## Skills
- Use `activate_skill [skill-name]` for any skill located in the linked `skills/` directory.
```

## 4. Verification
Run the following command in Gemini to verify the setup:
> "List my available skills and instructions from the agent library."

The agent should now be able to see the linked files and understand how to use them.