---
name: openclaw-codex-claude-cli-dev
description: "Drive Codex CLI and Claude Code like a human developer in terminal sessions: start, prompt, iterate, answer follow-up questions, inspect files, retry, and finish with validation. Supports headless mode (-p) for structured output and interactive tmux mode for slash commands. Use when users want real interactive CLI development instead of hand-written patches by the assistant."
---

# OpenClaw Codex + Claude Code CLI Dev

Use this skill to orchestrate coding through interactive CLI sessions, not by replacing the coding agent.

This skill supports two execution styles:
- **Headless mode** (non-interactive): best for normal prompts and structured output.
- **Interactive mode (tmux)**: required for **slash commands** like `/speckit.*`, `/opsx:*`, which can hang or be killed when run via headless `-p`.

## Quick checks

Verify Claude Code is installed:
```bash
claude --version
```

Run a minimal headless prompt (should print "OK"):
```bash
../../scripts/claude_code_run.py -p "Return only the single word OK." --permission-mode plan
```

Verify Codex is installed (if using Codex):
```bash
codex --version
```

## Core rule

Run the requested coding agent first.

- If user asks for Codex, run Codex.
- If user asks for Claude Code, run Claude Code.
- Keep the same agent unless user asks to switch.
- Default to **headless** mode for single prompts; use **interactive tmux** for multi-step or slash-command workflows.

## Core workflow

### 1) Run a headless prompt in a repo

```bash
cd /path/to/repo
../../scripts/claude_code_run.py \
  -p "Summarize this project and point me to the key modules." \
  --permission-mode plan
```

### 2) Allow tools (auto-approve with least privilege)

Claude Code supports tool allowlists via `--allowedTools`.
```bash
../../scripts/claude_code_run.py \
  -p "Run the test suite and fix any failures." \
  --allowedTools "Bash,Read,Edit"
```

### 3) Get structured output

```bash
../../scripts/claude_code_run.py \
  -p "Summarize this repo in 5 bullets." \
  --output-format json
```

### 4) Add extra system instructions

```bash
../../scripts/claude_code_run.py \
  -p "Review the staged diff for security issues." \
  --append-system-prompt "You are a security engineer. Be strict." \
  --allowedTools "Bash(git diff *),Bash(git status *),Read"
```

## Launch commands (human-style, without wrapper)

Always use PTY when running directly.

```bash
# Codex one-shot
codex exec "<task>"

# Codex interactive/autonomous
codex --yolo "<task>"

# Claude Code interactive
claude --dangerously-skip-permissions
# then paste task in session
```

OpenClaw pattern:

```bash
exec command:"cd <workdir> && <command>" pty:true background:true
process log/poll/paste/send-keys ...
```

## Workflow

1. **Prepare workdir**
   - `cd <workdir>`
   - ensure git repo (`git init`) when needed (especially Codex scratch runs)
   - clear folder only if user explicitly asks

2. **Start agent session**
   - run Codex/Claude with PTY + background
   - keep returned `sessionId`

3. **Send first prompt**
   - include target file paths
   - include feature checklist
   - include finish marker (`DONE`)

4. **Interact like a human**
   - poll logs periodically
   - if agent asks a question, answer directly in same session
   - if stalled, send short corrective prompt instead of restarting immediately
   - only interrupt/kill when clearly stuck

5. **Validate output yourself**
   - `ls`, `grep`, `wc`, test command
   - do not claim complete from agent text only

6. **Close session cleanly**
   - `/exit` (Claude) or let Codex exit
   - summarize artifacts + checks + next step

## Prompt templates

### Template A: feature build

```text
Build in <workdir>.
Output files: <paths>
Requirements:
1) ...
2) ...
Done criteria:
- Files exist
- Key features verifiable
- Output DONE
Start now.
```

### Template B: iterative fix

```text
Continue from last version, don't rewrite.
Read <files> first, then only modify what's necessary.
Fix target: ...
Output DONE + change summary when complete.
```

## High-leverage tips (from Claude Code official docs)

### 1) Always give Claude a way to verify (tests / build / screenshots)

Claude performs dramatically better when it can verify its work.
Make verification explicit in the prompt:
- "Fix the bug **and run tests**. Done when `npm test` passes."
- "Implement UI change, **take a screenshot** and compare to this reference."

### 2) Explore → Plan → Implement (use Plan Mode)

For multi-step work, start in plan mode for safe, read-only analysis:
```bash
../../scripts/claude_code_run.py -p "Analyze and propose a plan" --permission-mode plan
```
Then switch to execution (`acceptEdits`) once the plan is approved.

### 3) Manage context aggressively: /clear and /compact

Long, mixed-topic sessions degrade quality.
- Use `/clear` between unrelated tasks.
- Use `/compact Focus on <X>` when nearing limits to preserve the right details.

### 4) Rewind aggressively: /rewind (checkpoints)

Claude checkpoints before changes. If an approach is wrong, use `/rewind` (or Esc Esc) to restore:
- conversation only
- code only
- both

### 5) Prefer CLAUDE.md for durable rules; keep it short

A concise CLAUDE.md (global or per-project) for:
- build/test commands Claude should use
- repo etiquette / style rules
- non-obvious environment quirks

Overlong CLAUDE.md files get ignored.

### 6) Permissions: deny > ask > allow (and scope matters)

In `.claude/settings.json` / `~/.claude/settings.json`, rules match in order:
**deny first**, then ask, then allow.
Use deny rules to block secrets (e.g. `.env`, `secrets/**`).

### 7) Use subagents for heavy investigation

Subagents can read many files without polluting the main context.
Use them for broad codebase research or post-implementation review.

### 8) Treat Claude as a Unix utility (headless, pipes, structured output)

```bash
cat build-error.txt | claude -p "Explain root cause"
claude -p "List endpoints" --output-format json
```

## Interactive mode (tmux)

If your prompt contains slash commands, the wrapper defaults to **auto → interactive**.

```bash
../../scripts/claude_code_run.py \
  --mode interactive \
  --tmux-session cc-dev \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit,Write" \
  -p "Implement the auth module and run tests."
```

It will print tmux attach/capture commands so you can monitor progress.

### Monitoring / interacting

- `tmux -S <socket> attach -t <session>` — watch in real time
- `tmux -S <socket> capture-pane -p -J -t <target> -S -200` — snapshot output
- If Claude asks a question mid-run (e.g., "Proceed?"), attach and answer.

## Interaction etiquette

- Report start / milestone / done to user
- Keep updates short and factual
- Do not silently switch from CLI orchestration to manual coding

## Operational gotchas (learned in practice)

### 1) Codex refuses outside a git repo
Run `git init` first. Codex requires a git-managed directory.

### 2) TTY / UI glitches
Relaunch with `pty:true`. The wrapper script handles this automatically.

### 3) Claude spinner too long
Check logs, then send a concise nudge. If no progress >60s, interrupt and resend a shorter prompt.

### 4) Agent produced output but no file
Request an explicit write step, then re-validate.

### 5) Don't let your shell eat the prompt
When driving tmux via `send-keys`, avoid unescaped backticks and shell substitutions.
Prefer sending prompts from a file, or ensure the wrapper quotes safely.

### 6) Bash env vars don't persist across Claude tool calls
Each Bash tool call runs in a fresh shell; `export FOO=bar` won't persist.
If you need persistent env, set `CLAUDE_ENV_FILE=/path/to/env-setup.sh` before starting.

### 7) Long-running dev servers should run in a persistent session
Backgrounded `vite` / `ngrok` processes can get SIGKILL in automation.
Prefer running them in a managed background session (OpenClaw exec background) or tmux.

## Bundled script

- `../../scripts/claude_code_run.py`: shared wrapper that runs the local `claude` binary with a pseudo-terminal and forwards flags. Auto-detects the `claude` binary location.

More command examples: `references/interactive-cli-playbook.md`.
