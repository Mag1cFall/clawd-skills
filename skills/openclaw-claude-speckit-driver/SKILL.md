---
name: openclaw-claude-speckit-driver
description: "Drive Claude Code through SpecKit phases in OpenClaw with robust interaction patterns: slash-command sequencing, timeout handling, progress checkpoints, and recovery from long-thinking stalls. Uses interactive tmux mode for reliable slash-command execution. Use when building software via /speckit.constitution -> /speckit.specify -> /speckit.plan -> /speckit.tasks -> /speckit.implement in CLI sessions."
---

# OpenClaw Claude + SpecKit Driver

Use this skill to orchestrate SpecKit development with Claude Code as if a human is driving terminal sessions.

This skill uses **interactive tmux mode** for all SpecKit workflows because:
- Slash commands (`/speckit.*`) can hang or be killed when run via headless `-p`.
- SpecKit runs multiple steps (Bash + file writes + git) and may pause for confirmations.
- Headless runs can appear idle and be killed (SIGKILL) by supervisors.

## Quick checks

Verify Claude Code is installed:
```bash
claude --version
```

Verify SpecKit is available:
```bash
specify --version
```

Run a minimal wrapper test:
```bash
../../scripts/claude_code_run.py -p "Return only the single word OK." --permission-mode plan
```

## Prerequisites (important)

### 1) Initialize SpecKit (once per repo)
```bash
specify init . --ai claude
```

### 2) Ensure git repo (SpecKit uses git branches/scripts)
```bash
git init
git add -A
git commit -m "chore: init"
```

### 3) Recommended: set an `origin` remote
This prevents `git fetch --all --prune` from behaving oddly:
```bash
git init --bare ../origin.git
git remote add origin ../origin.git
git push -u origin main || git push -u origin master
```

### 4) Tool permissions for the full pipeline
Spec creation/tasks/implement need file writes + Bash:
```bash
--permission-mode acceptEdits --allowedTools "Bash,Read,Edit,Write"
```

## Phase order (strict)

1. `/speckit.constitution` — Define project principles
2. `/speckit.specify` — Create feature specification
3. `/speckit.plan` — Generate implementation plan
4. `/speckit.tasks` — Break plan into tasks
5. `/speckit.implement` — Execute tasks

Do not skip order. Each phase depends on artifacts from the previous one.

## Core workflow

### Run the full SpecKit pipeline (recommended)

```bash
../../scripts/claude_code_run.py \
  --mode interactive \
  --tmux-session cc-speckit \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit,Write" \
  -p $'/speckit.constitution Create project principles for quality, accessibility, and security.\n/speckit.specify <your feature description>\n/speckit.plan I am building with <your stack/constraints>\n/speckit.tasks\n/speckit.implement'
```

### Run individual phases

```bash
../../scripts/claude_code_run.py \
  --mode interactive \
  --tmux-session cc-speckit \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit,Write" \
  -p '/speckit.constitution Create principles for a REST API with security and test coverage.'
```

### Monitoring / interacting

The wrapper prints tmux commands for you:
- `tmux -S <socket> attach -t <session>` — watch in real time
- `tmux -S <socket> capture-pane -p -J -t <target> -S -200` — snapshot output

If Claude Code asks a question mid-run (e.g., "Proceed?"), attach and answer.

## Session launch rules

- Start Claude Code with PTY (the wrapper handles this).
- Use background session for long work.
- Submit slash command + concise arguments.
- Require stage marker output: `STAGE_DONE: <phase> => <path>`.

## Robust interaction loop

1. Send one phase command.
2. Poll logs every 20–40s.
3. If only spinner/animation with no file changes after timeout window:
   - interrupt once,
   - resend a shorter command,
   - keep the same phase target.
4. Verify artifacts on disk before declaring phase done.

## Validation checklist per phase

| Phase | Expected Artifacts | Checks |
|-------|-------------------|--------|
| constitution | Project principles file | No placeholder tokens (`[PROJECT_NAME]`, etc.) |
| specify | `specs/<feature>/` directory | Spec files present, meaningful content |
| plan | Implementation plan | Concrete steps, not generic |
| tasks | Task breakdown | Individual tasks with clear scope |
| implement | App files, tests, configs | Files exist, tests pass, build succeeds |

Additional checks:
- Phase marker printed
- Git diff contains meaningful updates
- No obvious placeholder tokens remain

## Reporting style to user

At each completed phase report:

- Phase name
- Artifact path(s)
- One-line quality note
- Next phase started

Keep updates short and factual.

## Safety constraints

- Do not manually replace full implementation while claiming it came from SpecKit.
- If slash command wrapper is broken, document workaround explicitly.
- Keep all changes inside project workdir.

## OpenSpec workflow (opsx)

OpenSpec is another spec-driven workflow powered by slash commands (`/opsx:*`).
Same reliability constraints apply — prefer **interactive tmux mode**.

### Setup (per machine)
```bash
npm install -g @fission-ai/openspec@latest
```

### Setup (per project)
```bash
openspec init --tools claude
# Optional: disable telemetry
export OPENSPEC_TELEMETRY=0
```

### Recommended command sequence (interactive)
1. `/opsx:onboard`
2. `/opsx:new <change-name>`
3. `/opsx:ff` (fast-forward: generates proposal/design/specs/tasks)
4. `/opsx:apply` (implements tasks)
5. `/opsx:archive` (optional: archive finished change)

## Operational gotchas (learned in practice)

### 1) Slash commands MUST use interactive mode
Never run `/speckit.*` or `/opsx:*` commands via headless `-p`. They will hang, produce incomplete output, or be killed by supervisors. Always use `--mode interactive` or `--mode auto`.

### 2) Workspace trust prompt on first run
The wrapper auto-handles the "Yes, I trust this folder" prompt. If running manually, watch for it and press Enter.

### 3) Vite + ngrok host blocking
If you expose a Vite dev server through ngrok:
- **Vite 7**: set `server.allowedHosts: true` or `['xxxx.ngrok-free.app']`
- ❌ Do **not** set `allowedHosts: 'all'` (won't work in Vite 7)

### 4) Don't let your shell eat the prompt
When driving tmux via `send-keys`, avoid unescaped backticks and shell substitutions. The wrapper handles quoting, but be careful with manual commands.

### 5) Long-running processes need persistent sessions
Backgrounded dev servers can get SIGKILL in automation. Run them in OpenClaw exec background or tmux, and explicitly stop them when done.

### 6) After correcting Claude's mistakes
Always instruct Claude Code to run:
> "Update your CLAUDE.md so you don't make that mistake again."

This ensures Claude records lessons learned.

### 7) Git state matters
SpecKit uses git branches internally. Ensure:
- Working tree is clean before starting
- Remote is configured (even a local bare repo)
- No uncommitted changes that could conflict

## Bundled script

- `../../scripts/claude_code_run.py`: shared wrapper that runs the local `claude` binary with a pseudo-terminal and forwards flags. Auto-detects the `claude` binary location.

Timeout guidance and fallback modes: see `references/speckit-recovery-playbook.md`.
