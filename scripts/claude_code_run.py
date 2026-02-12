#!/usr/bin/env python3
"""Run Claude Code (claude CLI) reliably — headless or interactive via tmux.

Default mode is *auto*:
- If the prompt contains slash commands (lines starting with `/`),
  we start an interactive Claude Code session in tmux (PTY).
- Otherwise we run headless (`-p`) through `script(1)` to force a pseudo-terminal.

Why this wrapper exists:
- Claude Code can hang when run without a TTY.
- CI / exec / cron environments are often non-interactive.

Docs: https://docs.anthropic.com/en/docs/claude-code
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

# Auto-detect claude binary: env override > PATH > common locations
_COMMON_PATHS = [
    "/home/linuxbrew/.linuxbrew/bin/claude",
    os.path.expanduser("~/.local/bin/claude"),
    "/usr/local/bin/claude",
]


def _find_claude() -> str:
    env = os.environ.get("CLAUDE_CODE_BIN")
    if env:
        return env
    w = which("claude")
    if w:
        return w
    for p in _COMMON_PATHS:
        if Path(p).is_file() and os.access(p, os.X_OK):
            return p
    return "claude"  # fallback; will fail loudly if not found


DEFAULT_CLAUDE = _find_claude()


def which(name: str) -> str | None:
    for p in os.environ.get("PATH", "").split(":"):
        cand = Path(p) / name
        try:
            if cand.is_file() and os.access(cand, os.X_OK):
                return str(cand)
        except OSError:
            pass
    return None


def looks_like_slash_commands(prompt: str | None) -> bool:
    if not prompt:
        return False
    return any(line.strip().startswith("/") for line in prompt.splitlines())


def build_headless_cmd(args: argparse.Namespace) -> list[str]:
    cmd: list[str] = [args.claude_bin]

    if args.permission_mode:
        cmd += ["--permission-mode", args.permission_mode]
    if args.prompt is not None:
        cmd += ["-p", args.prompt]
    if args.allowedTools:
        cmd += ["--allowedTools", args.allowedTools]
    if args.output_format:
        cmd += ["--output-format", args.output_format]
    if args.json_schema:
        cmd += ["--json-schema", args.json_schema]
    if args.append_system_prompt:
        cmd += ["--append-system-prompt", args.append_system_prompt]
    if args.system_prompt:
        cmd += ["--system-prompt", args.system_prompt]
    if args.continue_latest:
        cmd.append("--continue")
    if args.resume:
        cmd += ["--resume", args.resume]
    if args.extra:
        cmd += args.extra
    return cmd


def run_with_pty(cmd: list[str], cwd: str | None) -> int:
    cmd_str = " ".join(shlex.quote(c) for c in cmd)
    script_bin = which("script")
    if not script_bin:
        return subprocess.run(cmd, cwd=cwd, text=True).returncode
    return subprocess.run(
        [script_bin, "-q", "-c", cmd_str, "/dev/null"], cwd=cwd, text=True
    ).returncode


# ── tmux helpers ──────────────────────────────────────────────


def tmux_cmd(socket_path: str, *args: str) -> list[str]:
    return ["tmux", "-S", socket_path, *args]


def tmux_capture(socket_path: str, target: str, lines: int = 200) -> str:
    return subprocess.check_output(
        tmux_cmd(socket_path, "capture-pane", "-p", "-J", "-t", target, "-S", f"-{lines}"),
        text=True,
    )


def tmux_wait_for_text(
    socket_path: str, target: str, pattern: str, timeout_s: int = 30, poll_s: float = 0.5
) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            if pattern in tmux_capture(socket_path, target, 200):
                return True
        except subprocess.CalledProcessError:
            pass
        time.sleep(poll_s)
    return False


def run_interactive_tmux(args: argparse.Namespace) -> int:
    if not which("tmux"):
        print("tmux not found in PATH; cannot run interactive mode.", file=sys.stderr)
        return 2

    socket_dir = (
        args.tmux_socket_dir
        or os.environ.get("OPENCLAW_TMUX_SOCKET_DIR")
        or f"{os.environ.get('TMPDIR', '/tmp')}/openclaw-tmux-sockets"
    )
    Path(socket_dir).mkdir(parents=True, exist_ok=True)
    socket_path = str(Path(socket_dir) / args.tmux_socket_name)

    session = args.tmux_session
    target = f"{session}:0.0"

    subprocess.run(
        tmux_cmd(socket_path, "kill-session", "-t", session),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.check_call(tmux_cmd(socket_path, "new", "-d", "-s", session, "-n", "shell"))

    cwd = args.cwd or os.getcwd()

    claude_parts = [args.claude_bin]
    if args.permission_mode:
        claude_parts += ["--permission-mode", args.permission_mode]
    if args.allowedTools:
        claude_parts += ["--allowedTools", args.allowedTools]
    if args.append_system_prompt:
        claude_parts += ["--append-system-prompt", args.append_system_prompt]
    if args.system_prompt:
        claude_parts += ["--system-prompt", args.system_prompt]
    if args.continue_latest:
        claude_parts.append("--continue")
    if args.resume:
        claude_parts += ["--resume", args.resume]
    if args.extra:
        claude_parts += args.extra

    launch = f"cd {shlex.quote(cwd)} && " + " ".join(shlex.quote(p) for p in claude_parts)
    subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "-l", "--", launch))
    subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"))

    # Handle workspace trust prompt
    if tmux_wait_for_text(socket_path, target, "Yes, I trust this folder", timeout_s=20):
        subprocess.run(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"), check=False)
        time.sleep(0.8)
        if tmux_wait_for_text(socket_path, target, "Yes, I trust this folder", timeout_s=2):
            subprocess.run(tmux_cmd(socket_path, "send-keys", "-t", target, "1"), check=False)
            subprocess.run(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"), check=False)

    # Handle local-router warning (expected when using custom API endpoint)
    if tmux_wait_for_text(socket_path, target, "warning", timeout_s=5):
        subprocess.run(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"), check=False)

    if args.prompt:
        for line in (ln for ln in args.prompt.splitlines() if ln.strip()):
            subprocess.check_call(
                tmux_cmd(socket_path, "send-keys", "-t", target, "-l", "--", line)
            )
            subprocess.check_call(tmux_cmd(socket_path, "send-keys", "-t", target, "Enter"))
            time.sleep(args.interactive_send_delay_ms / 1000.0)

    print("Started interactive Claude Code in tmux.")
    print("To monitor:")
    print(f"  tmux -S {shlex.quote(socket_path)} attach -t {shlex.quote(session)}")
    print("To snapshot output:")
    print(
        f"  tmux -S {shlex.quote(socket_path)} capture-pane -p -J -t {shlex.quote(target)} -S -200"
    )

    if args.interactive_wait_s > 0:
        time.sleep(args.interactive_wait_s)
        try:
            snap = tmux_capture(socket_path, target, lines=200)
            print("\n--- tmux snapshot (last 200 lines) ---\n")
            print(snap)
        except subprocess.CalledProcessError:
            pass

    return 0


# ── main ──────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run Claude Code reliably (headless or interactive via tmux)"
    )

    ap.add_argument("-p", "--prompt", help="Prompt text.")
    ap.add_argument(
        "--mode",
        choices=["auto", "headless", "interactive"],
        default="auto",
        help="Execution mode. 'auto' switches to interactive when prompt contains slash commands.",
    )
    ap.add_argument("--permission-mode", default=None, help="Claude Code permission mode.")
    ap.add_argument("--allowedTools", help="Allowed tools allowlist string.")
    ap.add_argument(
        "--output-format", choices=["text", "json", "stream-json"], help="Output format (headless)."
    )
    ap.add_argument("--json-schema", help="JSON schema when using --output-format json.")
    ap.add_argument("--append-system-prompt", help="Append to default system prompt.")
    ap.add_argument("--system-prompt", help="Replace system prompt.")
    ap.add_argument("--continue", dest="continue_latest", action="store_true", help="Continue most recent session.")
    ap.add_argument("--resume", help="Resume a specific session ID.")
    ap.add_argument("--claude-bin", default=DEFAULT_CLAUDE, help=f"Path to claude binary (default: {DEFAULT_CLAUDE}).")
    ap.add_argument("--cwd", help="Working directory.")

    # tmux options
    ap.add_argument("--tmux-session", default="cc", help="tmux session name.")
    ap.add_argument("--tmux-socket-dir", default=None, help="tmux socket dir.")
    ap.add_argument("--tmux-socket-name", default="claude-code.sock", help="tmux socket file name.")
    ap.add_argument("--interactive-wait-s", type=int, default=0, help="Wait N seconds then snapshot.")
    ap.add_argument("--interactive-send-delay-ms", type=int, default=800, help="Delay between lines in interactive mode.")

    ap.add_argument("extra", nargs=argparse.REMAINDER, help="Extra args after --.")

    args = ap.parse_args()
    extra = args.extra
    if extra and extra[0] == "--":
        extra = extra[1:]
    args.extra = extra

    if not Path(args.claude_bin).exists():
        print(f"claude binary not found: {args.claude_bin}", file=sys.stderr)
        print("Tip: set CLAUDE_CODE_BIN=/path/to/claude or install claude globally.", file=sys.stderr)
        return 2

    mode = args.mode
    if mode == "auto" and looks_like_slash_commands(args.prompt):
        mode = "interactive"

    if mode == "interactive":
        return run_interactive_tmux(args)

    cmd = build_headless_cmd(args)
    return run_with_pty(cmd, cwd=args.cwd)


if __name__ == "__main__":
    raise SystemExit(main())
