# Interactive CLI Playbook (Codex + Claude Code)

## 1) Start sessions

### Codex

```bash
# one-shot task
codex exec "add unit tests for auth service"

# autonomous task
codex --yolo "refactor src/api and keep tests passing"
```

### Claude Code (direct)

```bash
claude --dangerously-skip-permissions
# paste multiline task, press Enter
```

### Claude Code (via wrapper — recommended)

```bash
# Headless one-shot
../../scripts/claude_code_run.py \
  -p "Add unit tests for auth service" \
  --allowedTools "Bash,Read,Edit"

# Interactive tmux session
../../scripts/claude_code_run.py \
  --mode interactive \
  --tmux-session cc-dev \
  --permission-mode acceptEdits \
  --allowedTools "Bash,Read,Edit,Write" \
  -p "Refactor the auth module. Run tests after."
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

1. Give concrete task with clear acceptance criteria.
2. Watch tool actions in logs.
3. Answer follow-up questions quickly.
4. Ask for correction if output drifts — don't restart.
5. Validate files/tests locally.

## 4) Headless mode patterns

### Structured output

```bash
../../scripts/claude_code_run.py \
  -p "List all API endpoints in this repo" \
  --output-format json
```

### Plan mode (read-only analysis)

```bash
../../scripts/claude_code_run.py \
  -p "Analyze this codebase and suggest improvements" \
  --permission-mode plan
```

### Piped input

```bash
cat error.log | claude -p "Explain the root cause of this error"
git diff HEAD~3 | claude -p "Summarize what changed and flag any issues"
```

### Custom system prompt

```bash
../../scripts/claude_code_run.py \
  -p "Review this code for security vulnerabilities" \
  --append-system-prompt "You are a senior security engineer. Flag OWASP Top 10 issues." \
  --allowedTools "Read"
```

## 5) Recovery tactics

- If no progress >60s: send short nudge prompt.
- If malformed output: ask for targeted rewrite, not full restart.
- If session broken: restart same agent with a smaller prompt.
- If wrapper can't find `claude`: set `CLAUDE_CODE_BIN=/path/to/claude`.

## 6) Context management

- Use `/clear` between unrelated tasks in the same session.
- Use `/compact Focus on <topic>` when context is getting long.
- Use `/rewind` (or Esc Esc) to undo a bad approach.
- Keep `CLAUDE.md` concise — overlong files get ignored.

## 7) Tool permission patterns

```bash
# Read-only analysis
--permission-mode plan

# Auto-approve edits only
--permission-mode acceptEdits

# Specific tools (least privilege)
--allowedTools "Bash(npm test),Bash(npm run build),Read,Edit"

# Full access (use sparingly)
--allowedTools "Bash,Read,Edit,Write"
```

## 8) Completion checklist

- Required files exist
- grep finds expected key text/features
- (if available) tests/build pass
- User gets concise summary + paths
- Session closed cleanly (`/exit` for Claude, natural exit for Codex)

## 9) Common mistakes to avoid

1. **Not providing verification method**: Always include a way for the agent to verify (tests, build, grep).
2. **Too-broad tool permissions**: Start narrow, expand only if needed.
3. **Ignoring context limits**: Use `/compact` proactively, don't wait for degraded output.
4. **Manual coding during CLI orchestration**: Don't silently switch from agent-driven to manual.
5. **Forgetting to update CLAUDE.md**: After correcting mistakes, tell Claude to update CLAUDE.md so it doesn't repeat them.
