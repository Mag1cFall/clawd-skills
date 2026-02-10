#!/usr/bin/env bash
set -euo pipefail

PROXY_URL="${1:-http://127.0.0.1:8045}"
CLAUDE_JSON="${HOME}/.claude.json"

echo "== Runtime models =="
openclaw models list --plain || true
openclaw models status --json || true

echo
echo "== Proxy health =="
curl -fsS "${PROXY_URL}/health" || {
  echo "[FAIL] proxy health check failed: ${PROXY_URL}/health" >&2
  exit 1
}

echo
echo "== Claude key-state summary =="
if [[ -f "${CLAUDE_JSON}" ]]; then
  python3 - <<'PY'
import json
from pathlib import Path
p = Path.home()/'.claude.json'
obj = json.loads(p.read_text())
r = obj.get('customApiKeyResponses', {})
for k in ('approved','rejected'):
    v = r.get(k, [])
    print(f"{k}: {len(v)} entries")
    for x in v:
        print(f"  - {x}")
PY
else
  echo "[WARN] ~/.claude.json not found"
fi

echo
echo "[OK] check complete"
