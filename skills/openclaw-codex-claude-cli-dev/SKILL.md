---
name: openclaw-codex-claude-cli-dev
description: "Drive Codex CLI and Claude Code like a human developer in terminal sessions: start, prompt, iterate, answer follow-up questions, inspect files, retry, and finish with validation. Use when users want real interactive CLI development, run `claude -p`, use Plan Mode, auto-approve tools with --allowedTools, generate JSON output, or integrate Claude Code into OpenClaw workflows/cron."
---

# OpenClaw Codex + Claude Code CLI Dev

Use this skill to orchestrate coding through interactive CLI sessions, not by replacing the coding agent.

This skill supports two execution styles:
- **Headless mode** (non-interactive): best for normal prompts and structured output.
- **Interactive mode (tmux)**: required for slash commands (e.g. `/speckit.*`, `/opsx:*`) which can hang in headless `-p`.

## Quick checks

Verify installation:
```bash
claude --version
```

Run a minimal headless prompt:
```bash
../../scripts/claude_code_run.py -p "Return only the single word OK."
```

## Core rule

Run the requested coding agent first.

- If user asks for Codex → run Codex.
- If user asks for Claude Code → run Claude Code.
- Keep the same agent unless user asks to switch.

## Launch commands

### Headless (via wrapper)

```bash
cd /path/to/repo
/home/mgf/openclaw-projects/my-skills/scripts/claude_code_run.py \
  -p "Summarize this project and point me to the key modules." \
  --permission-mode plan
```

### Allow tools (auto-approve, least privilege)

```bash
./scripts/claude_code_run.py \
  -p "Run the test suite and fix any failures." \
  --allowedTools "Bash,Read,Edit"
```

### Structured output

```bash
./scripts/claude_code_run.py \
  -p "Summarize this repo in 5 bullets." \
  --output-format json
```

### Add extra system instructions

```bash
./scripts/claude_code_run.py \
  -p "Review the staged diff for security issues." \
  --append-system-prompt "You are a security engineer. Be strict." \
  --allowedTools "Bash(git diff *),Bash(git status *),Read"
```

### Interactive (via OpenClaw exec)

```bash
# Start
exec command:"cd /path/project && claude --dangerously-skip-permissions" pty:true background:true

# Send prompt
process paste sessionId:<id> bracketed:true text:"..."
process send-keys sessionId:<id> keys:["ENTER"]

# Monitor
process poll sessionId:<id>
process log sessionId:<id> limit:300
```

### Codex launch

```bash
# one-shot task
codex exec "<task>"

# autonomous task
codex --yolo "<task>"
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
   - poll logs periodically (every 20-40s)
   - if agent asks a question, answer directly in same session
   - if stalled, send short corrective prompt instead of restarting
   - only interrupt/kill when clearly stuck (>2 min no progress)

5. **Validate output yourself**
   - `ls`, `grep`, `wc`, test command
   - do not claim complete from agent text only

6. **Close session cleanly**
   - `/exit` (Claude) or let Codex exit
   - summarize artifacts + checks + next step

## High-leverage tips (from official docs)

### 1) Always give Claude a way to verify

Claude performs dramatically better when it can verify its work:
- "Fix the bug **and run tests**. Done when `npm test` passes."
- "Implement UI change, **take a screenshot** and compare."

### 2) Explore → Plan → Implement (use Plan Mode)

```bash
./scripts/claude_code_run.py -p "Analyze and propose a plan" --permission-mode plan
```
Then switch to execution (`acceptEdits`) once the plan is approved.

### 3) Manage context: /clear and /compact

Long, mixed-topic sessions degrade quality.
- Use `/clear` between unrelated tasks.
- Use `/compact Focus on <X>` when nearing limits.

### 4) Use CLAUDE.md for durable rules

Best practice is a concise CLAUDE.md (global or per-project) for:
- build/test commands Claude should use
- repo etiquette / style rules
- non-obvious environment quirks

### 5) Permissions: deny > ask > allow

In `.claude/settings.json`, rules match in order: **deny first**, then ask, then allow.
Use deny rules to block secrets (e.g. `.env`, `secrets/**`).

### 6) Treat Claude as a Unix utility

```bash
cat build-error.txt | claude -p "Explain root cause"
claude -p "List endpoints" --output-format json
```

## Prompt templates

### Template A: feature build

```text
在 <workdir> 中开发。
输出文件：<paths>
要求：
1) ...
2) ...
完成标准：
- 文件存在
- 关键功能可验证
- 输出 DONE
现在开始。
```

### Template B: iterative fix

```text
继续上一版，不要重写。
先读 <files>，再只修改必要位置。
修复目标：...
完成后输出 DONE + 变更摘要。
```

## Notes (important)

- **After correcting Claude Code's mistakes**: Always instruct Claude Code to run:
  > "Update your CLAUDE.md so you don't make that mistake again."
- **Local router warning**: When using custom API endpoint (e.g. cliproxyapi), Claude Code shows a warning at startup. **This is expected — ignore it.**
- Use `--permission-mode plan` for read-only planning.
- Keep `--allowedTools` narrow (principle of least privilege).

## Operational gotchas

### 1) Codex refuses outside repo
Run `git init` first.

### 2) TTY/UI glitches
Relaunch with `pty:true`.

### 3) Claude spinner too long
Check logs, then send concise nudge. If no progress >60s, interrupt.

### 4) Agent produced output but no file
Request explicit write step, then re-validate.

### 5) Bash env vars don't persist
Each Bash tool call runs in a fresh shell. Use `CLAUDE_ENV_FILE` for persistence:
```bash
export CLAUDE_ENV_FILE=/path/to/env-setup.sh
```

### 6) Don't let your shell eat your prompt
When driving tmux via shell commands, avoid unescaped backticks and shell substitutions. Prefer sending prompts from a file.

## Bundled script

- `../../scripts/claude_code_run.py`: shared wrapper that runs the local `claude` binary with a pseudo-terminal and forwards flags. Auto-detects claude binary location.

More command examples: `references/interactive-cli-playbook.md`.
