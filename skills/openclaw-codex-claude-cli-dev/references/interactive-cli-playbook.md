# Interactive CLI Playbook (Codex + Claude Code)

## 1) Start sessions

### Codex

```bash
# one-shot task
codex exec "add unit tests for auth service"

# autonomous task
codex --yolo "refactor src/api and keep tests passing"
```

### Claude Code

```bash
claude --dangerously-skip-permissions
# paste multiline task, press Enter
```

## 2) OpenClaw orchestration snippets

```bash
# start
exec command:"cd /path/project && claude --dangerously-skip-permissions" pty:true background:true

# send prompt
process paste sessionId:<id> bracketed:true text:"..."
process send-keys sessionId:<id> keys:["ENTER"]

# monitor
process poll sessionId:<id>
process log sessionId:<id> limit:300
```

## 3) Human-like interaction loop

1. Give concrete task.
2. Watch tool actions in logs.
3. Answer follow-up question quickly.
4. Ask for correction if output drifts.
5. Validate files/tests locally.

## 4) Recovery tactics

- If no progress >60s: send short nudge prompt.
- If malformed output: ask for targeted rewrite, not full restart.
- If session broken: restart same agent with a smaller prompt.

## 5) Completion checklist

- required files exist
- grep finds expected key text/features
- (if available) tests/build pass
- user gets concise summary + paths
