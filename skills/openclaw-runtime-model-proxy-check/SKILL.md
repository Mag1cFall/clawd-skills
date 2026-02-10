---
name: openclaw-runtime-model-proxy-check
description: Verify OpenClaw model availability from runtime (not static config) and troubleshoot local Claude proxy/auth chains (for example localhost:8045 antigravity + ~/.claude.json key state). Use when model lists mismatch config, when Claude Code shows 401/403 token_rejected, or when users require proof of effective runtime routing.
---

# OpenClaw Runtime Model & Proxy Check

Run this workflow when users ask "what models are really available now" or when Claude proxy auth is unstable.

## Workflow

1. Read runtime model state.
2. Verify proxy health and API behavior.
3. Inspect Claude local key-state cache.
4. Fix rejected-key state when needed.
5. Re-test and document evidence.

## 1) Read runtime model state

Always prefer runtime commands:

```bash
openclaw models list --plain
openclaw models status --json
```

Do not treat `openclaw.json` as authoritative availability.

## 2) Verify proxy health (example: 8045)

```bash
curl -s http://127.0.0.1:8045/health
```

Then run a minimal API request with expected headers to confirm non-health path behavior.

## 3) Check Claude key-state cache

Inspect `~/.claude.json` field `customApiKeyResponses`.

If target custom key suffix appears under `rejected`, Claude Code can emit:

- `401 status code (no body)`
- `403 token_rejected`

## 4) Repair key-state cache

Move relevant key suffix from `rejected` to `approved`, then retry Claude request.

Use a backup before editing and log what changed.

## 5) Re-test and record evidence

Capture:

- runtime model default + fallback evidence
- proxy health response
- test request status code
- Claude end-to-end success sample

Put concise findings in memory file for persistence.

Detailed playbook: `references/proxy-auth-playbook.md`.

Quick local checker script: `scripts/check_proxy_and_claude_state.sh`.
