# zoke

Convert natural language to shell commands using OpenAI.

## Installation

```bash
pip install zoke-cli
```

Or install from source:

```bash
pip install git+https://github.com/Zoron-AI/zoke-cli.git
```

## Setup

Configure your OpenAI API key:

```bash
zoke configure --openai-key=YOUR_OPENAI_API_KEY
```

## Usage

```bash
zoke "list all files in current directory"
zoke "find python files modified in the last week"
zoke "show disk usage sorted by size"
```

The tool will display the generated command and ask for confirmation before executing.

### Auto-approve

Use the `-y` flag to skip confirmation and execute immediately:

```bash
zoke -y "show current date"
```
