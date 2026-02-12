# SpecKit Recovery Playbook (Claude CLI)

## Common failure patterns

### 1) Long spinner / no visible output
- **Symptom**: terminal animation continues, no stage marker, no file mtime change.
- **Cause**: Claude thinking deeply or network stall.
- **Timeout**: 2-4 min for constitution/specify/plan/tasks; 8-15 min for implement.

### 2) Command wrapper path issues
- **Symptom**: command references wrong scaffold path and never completes useful write.
- **Cause**: SpecKit not initialized or wrong working directory.

### 3) User-aborted run
- **Symptom**: process exits with signal 9 before artifact is written.
- **Cause**: manual kill or supervisor timeout.

### 4) Workspace trust prompt blocks execution
- **Symptom**: Claude Code waits for "Yes, I trust this folder" confirmation.
- **Cause**: first run in a new folder. The wrapper script handles this automatically.

### 5) Local router warning blocks execution
- **Symptom**: Claude Code shows API warning and waits for acknowledgment.
- **Cause**: using custom API endpoint (cliproxyapi). **This is expected — ignore it.** The wrapper script handles this automatically.

## Recovery sequence

1. Confirm process still alive (`process poll` or `tmux` check).
2. Check target artifact mtime and content:
   ```bash
   stat specs/<feature>/*.md
   head -20 specs/<feature>/constitution.md
   ```
3. If no progress over timeout window, interrupt and resend concise prompt.
4. If wrapper issue is identified, patch command file and rerun same phase.
5. **Do not advance phase until artifact validation passes.**

## Suggested timeout windows

| Phase | Soft timeout | Hard timeout |
|-------|-------------|-------------|
| constitution | 2 min | 4 min |
| specify | 2 min | 4 min |
| plan | 3 min | 5 min |
| tasks | 2 min | 4 min |
| implement (per checkpoint) | 8 min | 15 min |

## Artifact validation checks

### constitution
- File exists at expected path
- No placeholder tokens (`[PROJECT_NAME]`, `[TODO]`, `<PLACEHOLDER>`)
- Contains meaningful project principles

### specify
- Expected files present under `specs/<feature>/`
- Feature description is concrete, not boilerplate

### plan
- Plan document has concrete implementation steps
- References actual files/modules in the project

### tasks
- Task breakdown file present
- Tasks are actionable (not vague "implement feature")

### implement
- App files created/modified
- Tests present (if applicable)
- Docker/config updates present (if applicable)
- Build/lint passes (if available)

## Escalation path

If recovery fails after 2 attempts:
1. Save all current artifacts (`git stash` or copy).
2. Report failure to user with:
   - Which phase failed
   - Last output snapshot
   - Artifacts generated so far
3. Ask user whether to retry with simplified prompt or switch approach.

## tmux recovery commands

```bash
# Check if session is alive
tmux -S /tmp/openclaw-tmux-sockets/claude-code.sock has-session -t cc-speckit

# Snapshot current state
tmux -S /tmp/openclaw-tmux-sockets/claude-code.sock capture-pane -p -J -t cc-speckit:0.0 -S -200

# Send interrupt (Ctrl-C)
tmux -S /tmp/openclaw-tmux-sockets/claude-code.sock send-keys -t cc-speckit:0.0 C-c

# Kill and restart
tmux -S /tmp/openclaw-tmux-sockets/claude-code.sock kill-session -t cc-speckit
```
