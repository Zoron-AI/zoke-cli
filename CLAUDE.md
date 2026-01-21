# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

```bash
# Install locally for development
pip install -e .

# Install from source
pip install .

# Install from GitHub
pip install git+https://github.com/Zoron-AI/zoke-cli.git
```

## Testing the CLI

```bash
# Configure API key
zoke configure --openai-key=YOUR_KEY

# Run with confirmation prompt
zoke "your intent here"

# Run with auto-approve (skip confirmation)
zoke -y "your intent here"
```

## Architecture

**Entry point:** `zoke/cli.py:main()` - Handles argument parsing with manual sys.argv processing (not argparse for the main command) to allow natural language intents as positional arguments.

**Two subcommands:**
- `zoke configure --openai-key=KEY` - Stores API key in `~/.config/zoke/config.json`
- `zoke [-y] "intent"` - Converts intent to shell command via OpenAI, optionally auto-executes

**Key modules:**
- `cli.py` - CLI logic, OpenAI API calls, command execution
- `config.py` - JSON config file management at `~/.config/zoke/`

**OpenAI integration:** Uses `gpt-4o-mini` with OS detection (macOS/Linux/Windows) embedded in the system prompt to generate platform-appropriate commands.
