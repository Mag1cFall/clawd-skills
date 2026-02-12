# SpecKit Recovery Playbook (Claude CLI)

## Common failure patterns

### 1) Long spinner / no visible output
- **Symptom**: terminal animation continues, no stage marker, no file mtime change.
- **Cause**: Claude is "thinking" deeply, or the slash command hung waiting for input.
- **Recovery**: Wait up to the timeout window (see below). If no progress, interrupt once and resend a shorter, more specific command for the same phase.

### 2) Command wrapper path issues
- **Symptom**: command references wrong scaffold path and never completes useful write.
- **Cause**: SpecKit or the project wasn't properly initialized.
- **Recovery**: Verify `specify init . --ai claude` was run. Check that `speckit.yaml` or equivalent config exists. Patch command file and rerun same phase.

### 3) User-aborted run (SIGKILL)
- **Symptom**: process exits with signal 9 before artifact is written.
- **Cause**: Supervisor or OOM killer terminated the process.
- **Recovery**: Check partial artifacts. Resume from last completed phase. Use `--resume <session-id>` if Claude Code supports it.

### 4) Tmux session disappeared
- **Symptom**: `tmux attach` says "no such session".
- **Cause**: Server restart, OOM, or manual cleanup.
- **Recovery**: Restart with a fresh tmux session. Check git log for any commits made before the crash.

### 5) Trust prompt loop
- **Symptom**: Claude keeps showing "Yes, I trust this folder" repeatedly.
- **Cause**: First-time directory trust not properly acknowledged.
- **Recovery**: The wrapper auto-handles this. If running manually, type `1` and press Enter. If it loops, try: `claude --trust-dir /path/to/project`.

### 6) Git conflicts during SpecKit
- **Symptom**: SpecKit commands fail with git merge errors.
- **Cause**: Uncommitted changes or branch conflicts.
- **Recovery**: `git stash`, run SpecKit, then `git stash pop`. Or commit/clean the working tree first.

## Recovery sequence

1. Confirm process still alive (`process poll` or `tmux ls`).
2. Check target artifact mtime and content quickly.
3. If no progress over timeout window, interrupt and resend concise prompt.
4. If wrapper issue is identified, patch command file and rerun same phase.
5. Do not advance phase until artifact validation passes.
6. If all else fails, restart from the last successfully validated phase.

## Suggested timeout windows

| Phase | Soft Timeout | Hard Timeout | Notes |
|-------|-------------|--------------|-------|
| constitution | 2 min | 4 min | Should be fast — defining principles |
| specify | 3 min | 6 min | Feature description, moderate complexity |
| plan | 3 min | 6 min | Implementation planning |
| tasks | 2 min | 4 min | Breaking down the plan |
| implement | 8 min | 15 min | Per checkpoint; may need multiple rounds |

## Artifact checks

### constitution
- Principles file exists
- No placeholder tokens (`[PROJECT_NAME]`, `[DESCRIPTION]`, etc.)
- Content reflects the actual project intent

### specify
- Expected files present under `specs/<feature>/`
- Feature description is specific, not generic boilerplate
- Acceptance criteria are defined

### plan
- Implementation plan file exists
- Steps are concrete and reference actual files/modules
- Dependencies between steps are noted

### tasks
- Individual task files or sections exist
- Each task has clear scope and acceptance criteria
- Tasks are ordered logically

### implement
- App files created/modified as planned
- Tests exist and pass
- Docker/config updates present (if applicable)
- Build succeeds
- No leftover TODO/FIXME from SpecKit (unless intentional)

## Monitoring commands

### Via OpenClaw
```bash
# Check if session is alive
process poll sessionId:<id>

# Get last N lines of output
process log sessionId:<id> limit:300

# Send a nudge
process paste sessionId:<id> text:"Continue with the current phase."
process send-keys sessionId:<id> keys:["ENTER"]
```

### Via tmux (when using wrapper)
```bash
# List sessions
tmux -S /tmp/openclaw-tmux-sockets/claude-code.sock ls

# Attach to watch
tmux -S /tmp/openclaw-tmux-sockets/claude-code.sock attach -t cc-speckit

# Capture output snapshot
tmux -S /tmp/openclaw-tmux-sockets/claude-code.sock capture-pane -p -J -t cc-speckit:0.0 -S -200

# Kill stuck session
tmux -S /tmp/openclaw-tmux-sockets/claude-code.sock kill-session -t cc-speckit
```

## Emergency: manual phase completion

If a phase is fundamentally broken (wrapper bug, Claude API down, etc.):

1. Document the failure clearly.
2. Create the expected artifact manually, clearly marking it as manually created.
3. Commit with message: `chore: manual <phase> (speckit automation failed)`.
4. Proceed to next phase.
5. File a bug/note for fixing the automation later.

**Never**: claim manual work was produced by SpecKit automation.
