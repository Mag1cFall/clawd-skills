---
name: openclaw-claude-speckit-driver
description: "Drive Claude Code through SpecKit phases in OpenClaw with robust interaction patterns: slash-command sequencing, timeout handling, progress checkpoints, and recovery from long-thinking stalls. Use when building software via /speckit.constitution -> /speckit.specify -> /speckit.plan -> /speckit.tasks -> /speckit.implement in CLI sessions, or when using OpenSpec (/opsx:*) workflows."
---

# OpenClaw Claude + SpecKit Driver

Use this skill to orchestrate SpecKit (and OpenSpec) development with Claude Code as if a human is driving terminal sessions.

This skill uses **interactive tmux mode** exclusively — SpecKit slash commands hang in headless `-p` mode.

## Quick checks

```bash
# Verify Claude Code
claude --version

# Verify SpecKit
speckit --version  # or: specify --version

# Verify tmux
tmux -V
```

## Prerequisites (important)

### 1) Initialize SpecKit (once per repo)

```bash
specify init . --ai claude
```

### 2) Ensure proper git repo

SpecKit uses git branches/scripts internally:

```bash
git init
git add -A
git commit -m "chore: init"
```

### 3) Recommended: set an origin remote

Prevents `git fetch --all --prune` issues:

```bash
git init --bare ../origin.git
git remote add origin ../origin.git
git push -u origin main || git push -u origin master
```

### 4) Claude Code permissions

SpecKit needs file writes + bash:

```bash
--permission-mode acceptEdits --allowedTools "Bash,Read,Edit,Write"
```

## Phase order (strict)

1. `/speckit.constitution` — project principles
2. `/speckit.specify` — feature specification
3. `/speckit.plan` — implementation plan
4. `/speckit.tasks` — task breakdown
5. `/speckit.implement` — code generation

**Do not skip phases. Do not advance until current phase artifacts are validated.**

## Running the full pipeline

### Via wrapper script (recommended)

```bash
/home/mgf/openclaw-projects/my-skills/scripts/claude_code_run.py \
  --mode interactive \
  --tmux-session cc-speckit \
  --cwd /path/to/project \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit,Write" \
  -p $'/speckit.constitution Create project principles for quality, accessibility, and security.\n/speckit.specify <your feature description>\n/speckit.plan I am building with <your stack/constraints>\n/speckit.tasks\n/speckit.implement'
```

### Via OpenClaw exec

```bash
exec command:"cd /path/project && claude --dangerously-skip-permissions" pty:true background:true

# Then send each phase command:
process paste sessionId:<id> bracketed:true text:"/speckit.constitution ..."
process send-keys sessionId:<id> keys:["ENTER"]
```

## Robust interaction loop

1. Send one phase command.
2. Poll logs every 20–40s.
3. If only spinner/animation with no file changes after timeout window:
   - interrupt once
   - resend a shorter command
   - keep the same phase target
4. Verify artifacts on disk before declaring phase done.

## Monitoring / interacting

```bash
# Attach to watch in real time
tmux -S /tmp/openclaw-tmux-sockets/claude-code.sock attach -t cc-speckit

# Snapshot output
tmux -S /tmp/openclaw-tmux-sockets/claude-code.sock capture-pane -p -J -t cc-speckit:0.0 -S -200
```

If Claude Code asks a question mid-run (e.g., "Proceed?"), attach and answer.

## Validation checklist per phase

| Phase | Check |
|-------|-------|
| constitution | No placeholder tokens (`[PROJECT_NAME]` etc.) |
| specify | Expected files under `specs/<feature>/` |
| plan | Plan doc exists with concrete steps |
| tasks | Task breakdown file present |
| implement | App files, tests, docker updates present |

Additionally for all phases:
- Phase marker printed in output
- Expected artifact file exists on disk
- Git diff contains meaningful updates

## Reporting style to user

At each completed phase report:
- Phase name
- Artifact path(s)
- One-line quality note
- Next phase started

Keep updates short and factual.

## OpenSpec workflow (opsx)

OpenSpec is another spec-driven workflow powered by slash commands (`/opsx:*`). Same reliability constraints as SpecKit — use **interactive tmux mode**.

### Setup

```bash
npm install -g @fission-ai/openspec@latest
openspec init --tools claude
```

### Command sequence

1. `/opsx:onboard`
2. `/opsx:new <change-name>`
3. `/opsx:ff` (fast-forward: generates proposal/design/specs/tasks)
4. `/opsx:apply` (implements tasks)
5. `/opsx:archive` (optional)

## Safety constraints

- Do not manually replace full implementation while claiming it came from SpecKit.
- If slash command wrapper is broken, document workaround explicitly.
- Keep all changes inside project workdir.

## Notes

- **Local router warning**: When using custom API endpoint (e.g. cliproxyapi), Claude Code shows a warning at startup. **This is expected — ignore it.**
- **After correcting mistakes**: Always instruct Claude Code to update its CLAUDE.md so it doesn't repeat errors.

Timeout guidance and fallback modes: see `references/speckit-recovery-playbook.md`.
