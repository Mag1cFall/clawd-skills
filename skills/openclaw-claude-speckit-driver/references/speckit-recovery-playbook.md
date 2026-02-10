# SpecKit Recovery Playbook (Claude CLI)

## Common failure patterns

1. **Long spinner / no visible output**
   - Symptom: terminal animation continues, no stage marker, no file mtime change.
2. **Command wrapper path issues**
   - Symptom: command references wrong scaffold path and never completes useful write.
3. **User-aborted run**
   - Symptom: process exits with signal 9 before artifact is written.

## Recovery sequence

1. Confirm process still alive.
2. Check target artifact mtime and content quickly.
3. If no progress over timeout window, interrupt and resend concise prompt.
4. If wrapper issue is identified, patch command file and rerun same phase.
5. Do not advance phase until artifact validation passes.

## Suggested timeout windows

- constitution/specify/plan/tasks: 2-4 minutes soft timeout
- implement: 8-15 minutes per checkpoint

## Artifact checks

- constitution: no placeholder tokens (`[PROJECT_NAME]`, etc.)
- specify/plan/tasks: expected files present under `specs/<feature>/`
- implement: app files/tests/docker updates present
