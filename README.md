# clawd-skills

**OpenClaw skills** for driving Claude Code and Codex CLI in automated/interactive workflows.

## Skills

### 🔧 openclaw-codex-claude-cli-dev
Drive Codex CLI and Claude Code like a human developer — start sessions, prompt, iterate, answer follow-ups, inspect files, retry, and validate. Supports headless and interactive (tmux) modes.

### 🏗️ openclaw-claude-speckit-driver
Orchestrate SpecKit spec-driven development through Claude Code with robust interaction patterns: slash-command sequencing, timeout handling, progress checkpoints, and recovery.

## Shared scripts

- `scripts/claude_code_run.py` — Wrapper that runs the local `claude` binary reliably. Auto-detects binary location. Supports headless (`-p`) and interactive (tmux) modes with PTY allocation.

## Quick start

```bash
# Clone
git clone https://github.com/Mag1cFall/clawd-skills.git

# Verify Claude Code is installed
claude --version

# Test headless prompt
./scripts/claude_code_run.py -p "Return only the single word OK."
```

## Install into OpenClaw

Add the skills directory to OpenClaw's skill loading path:

```json5
{
  skills: {
    load: {
      extraDirs: ["/home/mgf/openclaw-projects/my-skills/skills"]
    }
  }
}
```

Or symlink individual skills into `~/.openclaw/skills/`.

## Requirements

- Claude Code CLI (`claude`) installed and in PATH
- `tmux` (for interactive mode)
- Python 3.10+ (for wrapper script)

---

# 中文说明

用于 **OpenClaw** 的自定义 skill 集合，通过 Claude Code 和 Codex CLI 自动化开发工作流。

## 包含的 Skills

- **openclaw-codex-claude-cli-dev**：像人类开发者一样驱动 Codex/Claude Code CLI
- **openclaw-claude-speckit-driver**：通过 Claude Code 驱动 SpecKit 规范化开发流程

## 快速使用

```bash
# 克隆仓库
git clone https://github.com/Mag1cFall/clawd-skills.git

# 测试
./scripts/claude_code_run.py -p "返回 OK"
```

## 安装到 OpenClaw

在 OpenClaw 配置中添加 skills 加载路径，或创建软链接到 `~/.openclaw/skills/`。
