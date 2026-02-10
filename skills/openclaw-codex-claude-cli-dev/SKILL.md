---
name: openclaw-codex-claude-cli-dev
description: "Drive Codex CLI and Claude Code like a human developer in terminal sessions: start, prompt, iterate, answer follow-up questions, inspect files, retry, and finish with validation. Use when users want real interactive CLI development instead of hand-written patches by the assistant."
---

# OpenClaw Codex + Claude Code CLI Dev

Use this skill to orchestrate coding through interactive CLI sessions, not by replacing the coding agent.

## Core rule

Run the requested coding agent first.

- If user asks for Codex, run Codex.
- If user asks for Claude Code, run Claude Code.
- Keep the same agent unless user asks to switch.

## Launch commands (human-style)

Always use PTY.

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

## Interaction etiquette

- report start / milestone / done to user
- keep updates short and factual
- do not silently switch from CLI orchestration to manual coding

## Troubleshooting

- **Codex refuses outside repo**: run `git init`
- **TTY/UI glitches**: relaunch with `pty:true`
- **Claude spinner too long**: check logs, then send concise nudge
- **agent produced output but no file**: request explicit write step, then re-validate

More command examples: `references/interactive-cli-playbook.md`.
