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
# Interactive (skip permissions for trusted repos)
claude --dangerously-skip-permissions

# Headless via wrapper
/home/mgf/openclaw-projects/my-skills/scripts/claude_code_run.py \
  -p "Return only the single word OK." \
  --permission-mode plan
```

## 2) OpenClaw orchestration snippets

```bash
# start background session
exec command:"cd /path/project && claude --dangerously-skip-permissions" pty:true background:true

# send prompt
process paste sessionId:<id> bracketed:true text:"..."
process send-keys sessionId:<id> keys:["ENTER"]

# monitor
process poll sessionId:<id>
process log sessionId:<id> limit:300
```

## 3) Headless with tools + structured output

```bash
# Allow specific tools (least privilege)
./scripts/claude_code_run.py \
  -p "Run tests and fix failures" \
  --allowedTools "Bash,Read,Edit"

# JSON output
./scripts/claude_code_run.py \
  -p "List all API endpoints with methods" \
  --output-format json

# Custom system prompt
./scripts/claude_code_run.py \
  -p "Review staged diff for security issues" \
  --append-system-prompt "You are a security engineer." \
  --allowedTools "Bash(git diff *),Read"
```

## 4) Interactive tmux mode (for slash commands)

```bash
./scripts/claude_code_run.py \
  --mode interactive \
  --tmux-session my-project \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit,Write" \
  -p "Implement the auth module"
```

Monitor:
```bash
tmux -S /tmp/openclaw-tmux-sockets/claude-code.sock attach -t my-project
```

Snapshot:
```bash
tmux -S /tmp/openclaw-tmux-sockets/claude-code.sock capture-pane -p -J -t my-project:0.0 -S -200
```

## 5) Human-like interaction loop

1. Give concrete task with clear completion criteria.
2. Watch tool actions in logs (poll every 20-40s).
3. Answer follow-up questions quickly.
4. Ask for correction if output drifts — don't restart.
5. Validate files/tests locally before declaring done.

## 6) Recovery tactics

| Symptom | Action |
|---------|--------|
| No progress >60s | Send short nudge prompt |
| Malformed output | Ask for targeted rewrite, not full restart |
| Session broken | Restart same agent with smaller prompt |
| Codex refuses | Run `git init` in workdir |
| Local router warning | Expected — ignore it |

## 7) Piping and Unix-style usage

```bash
# Pipe error logs to Claude
cat build-error.txt | claude -p "Explain root cause"

# Chain with other tools
git diff HEAD~3 | claude -p "Summarize changes" --output-format json

# CI integration
claude -p "Are there any security issues in this diff?" \
  --output-format json --json-schema '{"type":"object","properties":{"issues":{"type":"array"}}}'
```

## 8) Completion checklist

- [ ] Required files exist
- [ ] grep finds expected key text/features
- [ ] Tests/build pass (if available)
- [ ] User gets concise summary + paths
- [ ] Session closed cleanly
