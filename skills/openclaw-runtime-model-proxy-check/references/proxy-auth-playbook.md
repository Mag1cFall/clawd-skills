# Proxy/Auth Playbook

## Symptoms

- Claude Code loops on authentication.
- Debug log contains token rejection or missing authorization behavior.
- Proxy `/health` returns OK but real requests fail.

## Fast triage order

1. `openclaw models list --plain`
2. `openclaw models status --json`
3. `curl /health` on proxy
4. one minimal POST request to proxy
5. inspect `~/.claude.json` key-state cache

## Key lesson

Proxy health success does not guarantee Claude CLI auth state is valid.

## Recovery pattern

- Backup `~/.claude.json`
- Adjust `customApiKeyResponses` approved/rejected entries for current custom key suffix
- Retry Claude CLI request
- Confirm end-to-end success
