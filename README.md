# Agent Library

A centralized repository for AI agent instructions, skills, prompts, and documentation.

## How to Use This Library

### Instructions
1. Navigate to the ``instructions/`` directory.
2. Copy the content of the desired agent instruction file (e.g., ``marketplace-listings.md``).
3. Paste it into your agent's **System Instructions** or **Persona** field.

### Skills
1. Navigate to the ``skills/`` directory.
2. Locate the folder for the skill you want to activate (e.g., ``marketplace-listings/``).
3. Use the Gemini CLI command to activate the skill:
   ```bash
   activate_skill marketplace-listings
   ```
   *Note: If the skill is not in your local ``.gemini/skills`` directory, you may need to symlink or copy it there first.*

## Directory Structure
- ``instructions/``: High-level system instructions and personas.
- ``skills/``: Tool definitions and specialized agent capabilities (each in its own folder).
- ``prompts/``: Reusable prompt templates.
- ``docs/``: Architecture patterns and general guides.

## License
MIT