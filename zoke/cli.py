#!/usr/bin/env python3
"""zoke - Convert natural language to shell commands using OpenAI."""

import argparse
import os
import platform
import subprocess
import sys
import tempfile
from typing import Optional

from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError, APIStatusError


def getch() -> str:
    """Read a single character from stdin without waiting for Enter."""
    try:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    except Exception:
        # Fallback for Windows or other systems
        return input()[0] if input() else ""


def get_os_info() -> str:
    """Detect and return OS information."""
    system = platform.system()
    if system == "Darwin":
        return "macOS"
    elif system == "Linux":
        return "Linux"
    elif system == "Windows":
        return "Windows"
    return system

from . import config


def get_shell_command(client: OpenAI, intent: str) -> str:
    """Convert natural language intent to a shell command using OpenAI."""
    os_info = get_os_info()
    system_prompt = f"""You are a shell command generator. Convert the user's natural language intent into a single executable shell command.

The user is running {os_info}.

Rules:
- Output ONLY the command, nothing else
- No explanations, no markdown, no code blocks
- Use commands appropriate for {os_info}
- For macOS, use brew for package installation
- For Linux, use apt or the appropriate package manager
- Prefer simple, safe commands when possible
- If the intent is unclear or cannot be converted to a command, output: echo "Unable to convert intent to command"
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": intent},
        ],
        temperature=0,
        max_tokens=500,
    )

    return response.choices[0].message.content.strip()


def edit_command(command: str) -> str:
    """Allow user to edit the command using bash read -e -i for pre-filled input."""
    try:
        # Use bash's read -e -i for pre-filled editable input
        result = subprocess.run(
            ["bash", "-c", f'read -e -i {repr(command)} -p "Edit command: " cmd && echo "$cmd"'],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            # Fallback if bash read fails
            print(f"Current command: {command}")
            edited = input("Enter new command (or press Enter to keep): ")
            return edited.strip() if edited.strip() else command
    except Exception:
        # Fallback for systems without bash
        print(f"Current command: {command}")
        edited = input("Enter new command (or press Enter to keep): ")
        return edited.strip() if edited.strip() else command


def confirm_execution(command: str) -> Optional[str]:
    """Ask user to confirm, edit, or cancel command execution.

    Returns:
        The command to execute (original or edited), or None if cancelled.
    """
    print(f"\nGenerated command:\n  {command}\n")
    while True:
        print("Execute? [y]es / [n]o / [e]dit: ", end="", flush=True)
        response = getch().lower()
        print(response)  # Echo the character

        if response == "y":
            return command
        if response == "n":
            return None
        if response == "e":
            edited_command = edit_command(command)
            if edited_command:
                print(f"\nEdited command:\n  {edited_command}\n")
                return edited_command
            else:
                print("Empty command. Cancelled.")
                return None
        print("Please press 'y', 'n', or 'e'")


def execute_command(command: str) -> int:
    """Execute the shell command and return the exit code."""
    result = subprocess.run(command, shell=True)
    return result.returncode


def cmd_configure(args):
    """Handle the configure subcommand."""
    if args.openai_key:
        config.set_api_key(args.openai_key)
        print("OpenAI API key configured successfully.")
    else:
        print("Error: --openai-key is required", file=sys.stderr)
        sys.exit(1)


def cmd_run(intent: str, auto_approve: bool = False):
    """Handle the default run command."""
    api_key = config.get_api_key()
    if not api_key:
        print("Error: OpenAI API key not configured.", file=sys.stderr)
        print("Run: zoke configure --openai-key=YOUR_KEY", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    try:
        command = get_shell_command(client, intent)
    except AuthenticationError:
        print("Error: Invalid OpenAI API key.", file=sys.stderr)
        print("Run: zoke configure --openai-key=YOUR_KEY", file=sys.stderr)
        sys.exit(1)
    except RateLimitError:
        print("Error: OpenAI rate limit exceeded. Please try again later.", file=sys.stderr)
        sys.exit(1)
    except APIConnectionError:
        print("Error: Could not connect to OpenAI. Check your internet connection.", file=sys.stderr)
        sys.exit(1)
    except APIStatusError as e:
        print(f"Error: OpenAI API error ({e.status_code}): {e.message}", file=sys.stderr)
        sys.exit(1)

    if auto_approve:
        print(f"Executing: {command}")
        exit_code = execute_command(command)
        sys.exit(exit_code)
    else:
        final_command = confirm_execution(command)
        if final_command:
            exit_code = execute_command(final_command)
            sys.exit(exit_code)
        else:
            print("Command cancelled.")
            sys.exit(0)


def main():
    # Check if first arg is "configure"
    if len(sys.argv) > 1 and sys.argv[1] == "configure":
        parser = argparse.ArgumentParser(prog="zoke configure")
        parser.add_argument(
            "--openai-key",
            required=True,
            help="Your OpenAI API key",
        )
        args = parser.parse_args(sys.argv[2:])
        cmd_configure(args)
    elif len(sys.argv) > 1 and sys.argv[1] not in ["-h", "--help"]:
        # Parse -y flag and intent
        args = sys.argv[1:]
        auto_approve = False
        if "-y" in args:
            auto_approve = True
            args.remove("-y")

        if not args:
            print("Error: No intent provided.", file=sys.stderr)
            sys.exit(1)

        intent = " ".join(args)
        cmd_run(intent, auto_approve)
    else:
        print("Usage: zoke [-y] <intent>")
        print("       zoke configure --openai-key=YOUR_KEY")
        print()
        print("Convert natural language to shell commands using OpenAI.")
        print()
        print("Options:")
        print("  -y    Auto-approve and execute the generated command")
        print()
        print("Examples:")
        print('  zoke "list all files in current directory"')
        print('  zoke -y "show current date"')
        print()
        print("Setup:")
        print("  zoke configure --openai-key=YOUR_KEY")


if __name__ == "__main__":
    main()
