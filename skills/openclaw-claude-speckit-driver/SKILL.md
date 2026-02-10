---
name: openclaw-claude-speckit-driver
description: "Drive Claude Code through SpecKit phases in OpenClaw with robust interaction patterns: slash-command sequencing, timeout handling, progress checkpoints, and recovery from long-thinking stalls. Use when building software via /speckit.constitution -> /speckit.specify -> /speckit.plan -> /speckit.tasks -> /speckit.implement in CLI sessions."
---

# OpenClaw Claude + SpecKit Driver

Use this skill to orchestrate SpecKit development with Claude Code as if a human is driving terminal sessions.

## Phase order (strict)

1. `/speckit.constitution`
2. `/speckit.specify`
3. `/speckit.plan`
4. `/speckit.tasks`
5. `/speckit.implement`

Do not skip order.

## Session launch rules

- Start Claude Code with PTY.
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

Timeout guidance and fallback modes: see `references/speckit-recovery-playbook.md`.

## Validation checklist per phase

- Phase marker printed.
- Expected artifact file exists.
- No obvious placeholder tokens remain in generated docs.
- Git diff contains meaningful updates.

## Reporting style to user

At each completed phase report:

- phase name
- artifact path(s)
- one-line quality note
- next phase started

Keep updates short and factual.

## Safety constraints

- Do not manually replace full implementation while claiming it came from SpecKit.
- If slash command wrapper is broken, document workaround explicitly.
- Keep all changes inside project workdir.
