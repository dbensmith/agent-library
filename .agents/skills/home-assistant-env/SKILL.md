---
name: home-assistant-env
description: "Set up and verify the Home Assistant CLI (hass-cli) environment. Use when asked to setup Home Assistant, configure hass-cli, connect to Home Assistant, or when interacting with Home Assistant entities. Automates running load-op-env for authentication and verifying connectivity with hass-cli entity list."
---

# Home Assistant Environment Setup

A skill for setting up the environment required to interact with Home Assistant via `hass-cli`. This skill ensures you are authenticated and can retrieve entities.

## When to Use This Skill

- User asks to "setup Home Assistant" or "configure hass-cli"
- User asks to "connect to Home Assistant"
- You need to interact with Home Assistant entities but `hass-cli` is not yet authenticated in your current session

## Prerequisites

- **Operating System:** Supported on Linux and Windows Subsystem for Linux (WSL).
- **Shell:** You SHOULD be operating within an interactive login shell (e.g., `bash --login`) to ensure that user-defined aliases and scripts (like `load-op-env`) are correctly sourced.
- **Dependencies:**
  - `hass-cli` must be installed and accessible.
  - **Chezmoi:** The `load-op-env` script is managed and run via Chezmoi. Ensure Chezmoi is installed and initialized.
  - `load-op-env` alias or script must be available to manage 1Password-based secrets.
  - 1Password CLI (`op`) must be configured, as `load-op-env` relies on it for secret management.

## Step-by-Step Workflows

### 1. Authenticate with Home Assistant

Run the `load-op-env` command to load the required environment variables (`HASS_SERVER` and `HASS_TOKEN`).

```bash
load-op-env
```

**CRITICAL:** This command prompts the user for their 1Password credentials on the first run within a session. You MUST execute this command and then defer to the user's input (expose the terminal to the user and notify them) so they can enter their credentials. Do not attempt to input anything yourself.

### 2. Verify Connectivity

After loading the environment variables, verify that `hass-cli` can successfully connect to Home Assistant.

```bash
hass-cli entity list | head -n 5
```

If the command outputs a list of entities (and does not error out), the environment is successfully configured.

## Troubleshooting

| Issue                            | Solution                                                                                                                                                    |
| :------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `load-op-env: command not found` | Ensure you are in the correct WSL environment where the user's aliases/scripts are configured.                                                              |
| `hass-cli` connection error      | Verify that `HASS_SERVER` and `HASS_TOKEN` are actually set in the environment by running `env \| grep HASS`. If not, re-run `load-op-env`.                 |
| `hass-cli info` fails            | On Home Assistant OS environments, `hass-cli info` may fail with a 404 error perfectly normally. Use `hass-cli entity list` to verify connectivity instead. |

## References

- [hass-cli Documentation](https://github.com/home-assistant-ecosystem/home-assistant-cli)
- [Chezmoi Documentation](https://www.chezmoi.io/)
- [1Password CLI Documentation](https://developer.1password.com/docs/cli/)
- [Home Assistant API Specification](https://developers.home-assistant.io/docs/api/rest/)
