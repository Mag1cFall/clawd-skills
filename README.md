# clawd-skills

**OpenClaw skills** for driving coding CLI agents (Claude Code, Codex) with robust automation patterns.

## Skills

### 1. [openclaw-codex-claude-cli-dev](skills/openclaw-codex-claude-cli-dev/)

Drive **Codex CLI** and **Claude Code** like a human developer in terminal sessions. Supports headless mode (`-p`) for structured output and interactive tmux mode for complex workflows.

**Use when**: users want real interactive CLI development instead of hand-written patches.

### 2. [openclaw-claude-speckit-driver](skills/openclaw-claude-speckit-driver/)

Drive **Claude Code** through **SpecKit** phases (`/speckit.constitution` → `/speckit.specify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`) with robust interaction patterns, timeout handling, and recovery from stalls.

**Use when**: building software through the SpecKit spec-driven workflow.

## Shared scripts

### `scripts/claude_code_run.py`

A wrapper that runs the `claude` CLI reliably in automation environments:

- **PTY allocation** via `script(1)` — prevents non-TTY hangs
- **Auto mode**: automatically switches between headless and interactive based on prompt content
- **Headless mode**: direct `-p` execution with structured output support
- **Interactive mode**: launches Claude Code in tmux for slash commands and multi-step workflows
- **Auto-detection**: finds the `claude` binary automatically (PATH, common locations, or `CLAUDE_CODE_BIN` env var)

Quick test:
```bash
./scripts/claude_code_run.py -p "Return only the single word OK." --permission-mode plan
```

## Installation

### Option 1: Configure OpenClaw extraDirs

Add to your OpenClaw config (`~/.openclaw/config.yaml`):
```yaml
skills:
  load:
    extraDirs:
      - /path/to/clawd-skills/skills
```

### Option 2: Symlink into OpenClaw skills directory

```bash
ln -s /path/to/clawd-skills/skills/openclaw-codex-claude-cli-dev ~/.openclaw/skills/openclaw-codex-claude-cli-dev
ln -s /path/to/clawd-skills/skills/openclaw-claude-speckit-driver ~/.openclaw/skills/openclaw-claude-speckit-driver
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) (`claude` CLI) installed
- [OpenClaw](https://openclaw.com/) running
- `tmux` (for interactive mode)
- Python 3.10+ (for the wrapper script)
- Optional: [Codex CLI](https://github.com/openai/codex) for Codex workflows
- Optional: [SpecKit](https://github.com/nichochar/speckit) (`specify` CLI) for spec-driven development

---

# 中文说明

这是一组 **OpenClaw 技能**，用于通过自动化模式驱动编程 CLI 代理（Claude Code、Codex）。

## 包含的技能

1. **openclaw-codex-claude-cli-dev** — 像人类开发者一样在终端中驱动 Codex / Claude Code
2. **openclaw-claude-speckit-driver** — 通过 SpecKit 阶段驱动 Claude Code 进行规范驱动开发

## 共享脚本

`scripts/claude_code_run.py` — 对 `claude` CLI 的封装，解决无 TTY 环境下的挂起问题：
- 通过 `script(1)` 分配伪终端
- 自动检测 `claude` 二进制路径
- 支持 headless 和 tmux 交互两种模式

## 安装

在 OpenClaw 配置 (`~/.openclaw/config.yaml`) 中添加：
```yaml
skills:
  load:
    extraDirs:
      - /path/to/clawd-skills/skills
```

或通过软链接安装到 `~/.openclaw/skills/` 目录。
