---
name: openclaw-claude-cli-loop
description: Run Claude Code in a controlled OpenClaw CLI loop (exec + process + PTY), including task kickoff, live progress polling, interruption/retry, and completion validation. Use when a user asks to let Claude Code implement files/projects while the assistant orchestrates the terminal interaction instead of hand-writing code directly.
---

# OpenClaw Claude CLI Loop

Use this workflow to orchestrate Claude Code safely and transparently.

## Workflow

1. Prepare workspace.
2. Start Claude Code with PTY and background session.
3. Submit structured task prompt.
4. Poll logs and report milestone progress to user.
5. Validate outputs on disk.
6. Exit Claude session and summarize deliverables.

## Step 1: Prepare workspace

- Create/clean target directory if user requested reset.
- Initialize git when useful for diff tracking:

```bash
cd <workdir>
mkdir -p .
git init -q
```

## Step 2: Start Claude Code

Always use PTY for Claude Code TUI:

```bash
exec command="cd <workdir> && claude --dangerously-skip-permissions" pty=true background=true
```

Capture returned `sessionId` for `process log/poll/paste/send-keys`.

## Step 3: Send task prompt

- Use one complete prompt with explicit success criteria.
- Require final marker text (for example `DONE`).
- Require output path(s) and runtime constraints.

Use bracketed paste to avoid broken multiline input.

## Step 4: Monitor and communicate

- Poll with `process poll` during long runs.
- Watch for actual tool actions (`Write(...)`, completion summary), not spinner frames only.
- If stalled, send short follow-up prompt or interrupt and retry.
- Send user progress at milestone boundaries (started / file written / validated / finished).

Detailed triage patterns: see `references/claude-loop-checklist.md`.

## Step 5: Validate result

Validate from shell after Claude reports completion:

```bash
ls -la <workdir>
wc -l <target-file>
grep -n "<required-keyword>" <target-file>
```

Do not declare done until required file(s) exist and key requirements are present.

## Step 6: Close session

Send `/exit` to Claude Code and verify process exit.

If process remains open unexpectedly, kill it and report that cleanup step.

## Output format to user

Return:

- What Claude produced
- Validation evidence (file path + key checks)
- Remaining risks or TODOs
- Next optional action (deploy/test/commit)
