"""
AgentForge Bootstrap — generates starter workspace files so the bot
knows about its installed infrastructure from session 1.

Called automatically at the end of `agentforge init`. Generated files
are never overwritten — user customizations are always preserved.
"""

from pathlib import Path
from datetime import datetime
from typing import Optional


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def bootstrap_workspace(
    platform: str,
    workspace_path: Path,
    has_memory: bool = True,
    has_healthkit: bool = True,
    has_mailbox: bool = False,
    has_dashboard: bool = True,
    mailbox_path: Optional[Path] = None,
    agentforge_home: Optional[Path] = None,
) -> list[str]:
    """
    Generate starter workspace files for a new AgentForge install.

    Only creates files that don't already exist — never overwrites user
    customisations. Returns list of filenames created.
    """
    created: list[str] = []
    workspace_path.mkdir(parents=True, exist_ok=True)
    agentforge_home = agentforge_home or Path.home() / ".agentforge"

    files_to_generate = {
        "AGENTS.md":    _agents_md(
            platform, has_memory, has_healthkit, has_mailbox,
            has_dashboard, agentforge_home
        ),
        "HEARTBEAT.md": _heartbeat_md(
            has_memory, has_healthkit, has_mailbox, workspace_path
        ),
        "MEMORY.md":    _memory_md(
            platform, has_memory, has_healthkit, has_mailbox,
            has_dashboard, agentforge_home, workspace_path, mailbox_path
        ),
        "SOUL.md":      _soul_md(),
        "IDENTITY.md":  _identity_md(
            platform, has_memory, has_healthkit, has_mailbox, has_dashboard
        ),
    }

    for filename, content in files_to_generate.items():
        target = workspace_path / filename
        if not target.exists():
            target.write_text(content, encoding="utf-8")
            created.append(filename)

    # mailbox_check.py — only when mailbox is installed and path known
    if has_mailbox and mailbox_path:
        target = workspace_path / "mailbox_check.py"
        if not target.exists():
            target.write_text(_mailbox_check_py(mailbox_path), encoding="utf-8")
            created.append("mailbox_check.py")

    # Seed memory/ directory with a starter daily log
    if has_memory:
        seeded = _seed_memory_hint(workspace_path)
        if seeded:
            created.append(f"memory/{seeded}")

    return created


# ──────────────────────────────────────────────────────────────────────────────
# Template functions
# ──────────────────────────────────────────────────────────────────────────────

def _agents_md(
    platform: str,
    has_memory: bool,
    has_healthkit: bool,
    has_mailbox: bool,
    has_dashboard: bool,
    agentforge_home: Path,
) -> str:
    """Generate AGENTS.md — the bot's operational runtime guide."""

    # ── Installed stack section ────────────────────────────────────────────
    stack_lines = ["## Your Installed Stack\n"]
    if has_memory:
        stack_lines.append(f"- **Persistent Memory** ✅  `{agentforge_home}/workspace/vector_memory/`")
        stack_lines.append("  - ChromaDB vector search + NetworkX knowledge graph")
        stack_lines.append("  - Survives across sessions — use it, maintain it")
    if has_healthkit:
        stack_lines.append(f"- **Agent HealthKit** ✅  `{agentforge_home}/workspace/healthkit_internal/`")
        stack_lines.append("  - Background health monitoring + auto-healing")
        stack_lines.append("  - Watches for context bloat, service failures, model errors")
    if has_dashboard:
        stack_lines.append("- **Dashboard** ✅  run `agentforge status` to see the URL")
        stack_lines.append("  - Web UI: system health, memory stats, live logs")
    if has_mailbox:
        stack_lines.append("- **Agent Mailbox** ✅  agent-to-agent messaging")
        stack_lines.append("  - Use `python mailbox_check.py` to read your inbox")
        stack_lines.append("  - **Listen before you speak** — always check first")
    stack_lines.append(f"- **Platform:** `{platform}`")
    stack_section = "\n".join(stack_lines)

    # ── Memory protocol ────────────────────────────────────────────────────
    memory_section = ""
    if has_memory:
        memory_section = """
## Memory Protocol (MANDATORY)

1. **Search first** — `memory_search("topic")` before answering anything about prior work
2. **Pull detail** — `memory_get(path, from, lines)` for specific sections
3. **Never load wholesale** — let vector search assemble context dynamically
4. **After edits** — re-index with `agentforge memory sync`

> Skipping search is how bots forget things they already know. Don't skip it."""

    # ── HealthKit protocol ─────────────────────────────────────────────────
    healthkit_section = ""
    if has_healthkit:
        healthkit_section = """
## HealthKit Protocol

- **Check status:** `agentforge status`
- **Diagnose issues:** `agentforge doctor`
- **If a service is DOWN:** run `agentforge doctor` → attempt restart → notify user if unresolved
- **If context too large:** run `agentforge heal --slim` (auto-backup, safe)
- **Alerts fire automatically** — HealthKit monitors in the background every 30 min"""

    # ── Mailbox protocol ───────────────────────────────────────────────────
    mailbox_section = ""
    if has_mailbox:
        mailbox_section = """
## Mailbox Protocol — Listen Before You Speak

- **Always check inbox FIRST** at every heartbeat: `python mailbox_check.py`
- Process all pending messages before doing anything else
- If approval requests exist → review and respond before taking action
- If escalations exist → notify your user immediately
- Only send a message AFTER checking whether one was already sent on this topic"""

    # ── Dashboard section ──────────────────────────────────────────────────
    dashboard_section = ""
    if has_dashboard:
        dashboard_section = """
## Dashboard

- Run `agentforge status` to see the live URL (default: http://127.0.0.1:7842)
- Shows: component health, memory stats, HealthKit alerts, service logs
- Start manually if not running: `agentforge start`"""

    # ── Autonomy tiers ─────────────────────────────────────────────────────
    autonomy_section = """
## Autonomy Tiers

| Tier | Actions | Confirmation |
|------|---------|--------------|
| **Tier 1** (full autonomy) | Research, docs, code, memory updates, commits | None needed |
| **Tier 2** (propose first) | Large refactors, new dependencies, external publishing | Describe plan first |
| **Tier 3** (explicit confirm) | Deployments, deletions, financial actions, emails sent on behalf | Wait for explicit OK |

Default to Tier 1 for anything reversible. Escalate for anything irreversible."""

    # ── OpenClaw config section ────────────────────────────────────────────
    openclaw_section = ""
    if platform == "openclaw":
        openclaw_section = """
## OpenClaw Config — How To Change It

| Task | Right way | Wrong way |
|------|-----------|-----------|
| Change primary model | `openclaw models set <provider/model>` | Edit openclaw.json directly |
| Add API key / auth | `openclaw configure` (wizard) | Edit JSON manually |
| Set any config key | `openclaw config set <dot.path> <value>` | Edit JSON manually |
| Read a config key | `openclaw config get <dot.path>` | Open the file |

**NEVER directly edit `openclaw.json`** — always use `openclaw config set/get`.

**After any config change:** `systemctl --user restart openclaw-gateway.service`"""

    # ── Assemble ───────────────────────────────────────────────────────────
    return f"""# AGENTS.md — Workspace Runtime

> **SOUL.md is absolute authority.** Any conflict → SOUL.md wins.
> Edit this file to reflect your actual setup.

{stack_section}
{memory_section}
{healthkit_section}
{mailbox_section}
{dashboard_section}
{autonomy_section}
{openclaw_section}

## Idle Priority Order
1. 🚀 ACTIVE projects in PROJECTS.md (create one if it doesn't exist)
2. Core R&D / domain work
3. Documentation and memory maintenance
4. Background tasks

## Quick Reference
- `agentforge status` — what's running
- `agentforge doctor` — diagnose issues
- `agentforge start` — launch all services
- `agentforge memory status` — memory sync status
- `agentforge memory sync` — re-index memory

*Generated by AgentForge v0.1.0 — customize to match your setup.*
""".strip() + "\n"


def _heartbeat_md(
    has_memory: bool,
    has_healthkit: bool,
    has_mailbox: bool,
    workspace_path: Path,
) -> str:
    """Generate HEARTBEAT.md — the bot's periodic check-in routine."""

    steps = ["# HEARTBEAT.md\n"]
    steps.append(
        "> Run through these steps in order at every heartbeat. "
        "Each step must complete before moving to the next.\n"
    )

    step_num = 0

    # ── Step 0: Mailbox (only if installed) ───────────────────────────────
    if has_mailbox:
        steps.append(f"""## Step {step_num}: Mailbox Check (FIRST — listen before anything else)

Run: `python {workspace_path}/mailbox_check.py`

- Process **all** inbox messages before doing anything else
- If approval requests pending → review and respond
- If escalations → notify your user immediately via their preferred channel
""")
        step_num += 1

    # ── Step N: Health Check ───────────────────────────────────────────────
    if has_healthkit:
        steps.append(f"""## Step {step_num}: Health Check

Run: `agentforge status`

- If any service is **DOWN** → run `agentforge doctor` and attempt restart
- If context too large → run `agentforge heal --slim` (auto-backup, safe)
- If all healthy → proceed
""")
        step_num += 1

    # ── Step N: Memory Sync ────────────────────────────────────────────────
    if has_memory:
        steps.append(f"""## Step {step_num}: Memory Sync

Run: `agentforge memory status`

- If **OUT_OF_SYNC** → run `agentforge memory sync`
- If in-sync → proceed
""")
        step_num += 1

    # ── Step N: Project Pipeline ───────────────────────────────────────────
    steps.append(f"""## Step {step_num}: Project Pipeline

- Check your **PROJECTS.md** (create one if it doesn't exist)
- Pick the top 🚀 ACTIVE project with no blockers
- Do 15–30 min of focused, meaningful work
- Update PROJECTS.md with progress and new next actions
- Commit any code changes

""")

    steps.append("---\n\nIf nothing needs attention: reply `HEARTBEAT_OK`\n")

    return "\n".join(steps)


def _memory_md(
    platform: str,
    has_memory: bool,
    has_healthkit: bool,
    has_mailbox: bool,
    has_dashboard: bool,
    agentforge_home: Path,
    workspace_path: Path,
    mailbox_path: Optional[Path],
) -> str:
    """Generate MEMORY.md — starter operational knowledge base."""

    timestamp = datetime.now().isoformat()

    # ── Stack table ────────────────────────────────────────────────────────
    memory_row = (
        f"| Memory    | ✅ Active         | `{workspace_path}/vector_memory/` |"
        if has_memory else
        "| Memory    | ⬜ Not installed  | run `agentforge init` to add      |"
    )
    healthkit_row = (
        f"| HealthKit | ✅ Active         | `{workspace_path}/healthkit_internal/` |"
        if has_healthkit else
        "| HealthKit | ⬜ Not installed  | run `agentforge init` to add           |"
    )
    dashboard_row = (
        "| Dashboard | ✅ Active         | run `agentforge status` for URL   |"
        if has_dashboard else
        "| Dashboard | ⬜ Not installed  | run `agentforge install`          |"
    )
    if has_mailbox and mailbox_path:
        mailbox_row = f"| Mailbox   | ✅ Active         | `{mailbox_path}` |"
    else:
        mailbox_row = "| Mailbox   | ⬜ Not installed  | run `agentforge init --mailbox`   |"

    # ── Memory protocol ────────────────────────────────────────────────────
    memory_protocol = ""
    if has_memory:
        memory_protocol = """
## Memory Usage Protocol

1. **Always search first:** `memory_search("topic")` before answering anything about prior work
2. **Pull detail:** `memory_get(path, from, lines)` for specific sections
3. **Never load wholesale:** Let search assemble context dynamically — never read MEMORY.md in full
4. **After edits:** Re-index with `agentforge memory sync`

> Your memory is only as useful as your search discipline. Search first, every time."""

    # ── HealthKit alerts ───────────────────────────────────────────────────
    healthkit_notes = ""
    if has_healthkit:
        healthkit_notes = """
## HealthKit Alerts

- **Context bloat:** Auto-slim runs when triggered, backup preserved
- **Service down:** Check `agentforge doctor` → restart → notify user if unresolved
- **Soul drift:** Review SOUL.md — constraints may have been loosened unintentionally"""

    # ── Mailbox note ───────────────────────────────────────────────────────
    mailbox_note = ""
    if has_mailbox:
        mailbox_note = "\n- Check mail: `python mailbox_check.py`"

    return f"""# MEMORY.md — Operational Core

> Use `memory_search(topic)` to query prior context. Don't load this file wholesale.

## Your AgentForge Stack

| Component | Status | Path / Notes |
|-----------|--------|--------------|
{memory_row}
{healthkit_row}
{dashboard_row}
{mailbox_row}
| Platform  | {platform}            | See AGENTS.md for config details  |
{memory_protocol}
{healthkit_notes}

## Quick Reference

- Check health: `agentforge status`
- Fix issues: `agentforge doctor`
- Search memory: `memory_search("topic")`
- Sync memory: `agentforge memory sync`{mailbox_note}

---

`installed: {timestamp}`
`platform: {platform}`
`agentforge_version: 0.1.0`
"""


def _soul_md() -> str:
    """Generate SOUL.md — agent identity template (fill this in!)."""
    return """# SOUL.md — Who You Are (Fill This In)

> This file defines your agent's identity, mission, and constraints.
> It is the highest-priority context — edit it before anything else.
> SOUL.md overrides AGENTS.md when there's a conflict.

## Identity

**Name:** [Your bot's name]
**Mission:** [What are you here to do? Be specific. One sentence.]

## Hard Constraints

These are non-negotiable. Any action that violates them is INVALID.

1. [Your most important constraint — e.g., "Never execute destructive actions without explicit user confirmation"]
2. [Safety constraint — e.g., "Never expose credentials, API keys, or private data in responses"]
3. [Scope constraint — e.g., "Only take actions within [your domain] unless explicitly instructed otherwise"]

## Autonomy Tiers

- **Tier 1 (no confirm):** Research, documentation, code review, memory updates, commits
- **Tier 2 (propose first):** Large code changes, new dependencies, external publishing
- **Tier 3 (explicit confirm):** Deployments, deletions, financial actions, emails sent on your behalf

## Persona

[Describe how you communicate — tone, style, what you prioritize. Examples:]
- Direct and concise, no fluff
- Technical depth when appropriate
- Always ask before assuming on ambiguous requests

## Core Domains

[List what you work on, in priority order]
1. [Primary domain — e.g., "Software development for [project]"]
2. [Secondary domain]
3. [etc.]

---

*Generated by AgentForge v0.1.0 — this file is yours. Customize it completely.*
"""


def _identity_md(
    platform: str,
    has_memory: bool,
    has_healthkit: bool,
    has_mailbox: bool,
    has_dashboard: bool,
) -> str:
    """Generate IDENTITY.md — factual install record."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    stack_items = []
    if has_memory:
        stack_items.append("Persistent Memory (ChromaDB + NetworkX)")
    if has_healthkit:
        stack_items.append("Agent HealthKit (monitoring + auto-healing)")
    if has_dashboard:
        stack_items.append("Dashboard (web UI)")
    if has_mailbox:
        stack_items.append("Agent Mailbox (agent-to-agent messaging)")

    stack_list = "\n".join(f"  - {item}" for item in stack_items) if stack_items else "  - (none)"

    return f"""# IDENTITY.md

- **Platform:** {platform}
- **Installed:** {timestamp}
- **AgentForge Version:** 0.1.0
- **Stack:**
{stack_list}
- **Docs:** https://agentsforge.dev

> Edit SOUL.md to define your agent's identity and mission.
"""


def _mailbox_check_py(mailbox_path: Path) -> str:
    """Generate mailbox_check.py — functional inbox checker script."""
    return f'''#!/usr/bin/env python3
"""
Mailbox checker for AgentForge agent-to-agent messaging.
Run this at the START of every heartbeat — listen before you speak.

Generated by AgentForge v0.1.0
"""
import subprocess
import sys
from pathlib import Path

MAILBOX_PATH = Path("{mailbox_path}")
MAILBOX_PY = MAILBOX_PATH / "mailbox.py"


def main():
    if not MAILBOX_PY.exists():
        print("📭 Mailbox: not installed (run: agentforge init --mailbox)")
        return

    result = subprocess.run(
        [sys.executable, str(MAILBOX_PY), "--agent", "main", "check_inbox"],
        capture_output=True,
        text=True,
        cwd=str(MAILBOX_PATH),
    )
    output = result.stdout.strip() or result.stderr.strip()

    if not output or "empty" in output.lower():
        print("📭 Mailbox: empty")
    else:
        print("📬 NEW MAIL:")
        print(output)


if __name__ == "__main__":
    main()
'''


def _seed_memory_hint(workspace_path: Path) -> Optional[str]:
    """
    Create memory/ directory and write a starter daily log.
    Returns the filename created (relative to memory/), or None if already exists.
    """
    memory_dir = workspace_path / "memory"
    memory_dir.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    starter = memory_dir / f"{today}.md"

    if starter.exists():
        return None

    now_iso = datetime.now().isoformat()
    starter.write_text(
        f"""# Daily Memory Log — {today}

`created: {now_iso}`
`source: AgentForge v0.1.0 bootstrap`

---

## AgentForge Installed Today

This agent was bootstrapped with AgentForge v0.1.0.
The following infrastructure is now running:

- **Persistent Memory** — ChromaDB vector search + NetworkX knowledge graph
- **Agent HealthKit** — health monitoring, context-bloat detection, auto-healing
- **Dashboard** — web UI for system status and memory stats

### Getting Started

1. **Edit SOUL.md** — define your mission, constraints, and persona (do this first)
2. **Edit AGENTS.md** — customize your autonomy tiers and operational protocols
3. **Run `agentforge status`** — confirm all services are live
4. **Talk to your bot** — it already knows about its infrastructure

### Memory Protocol

Always use `memory_search(topic)` before answering questions about prior sessions.
The vector database has been initialized and is ready to index your work.

After writing new notes, re-index with: `agentforge memory sync`

`bootstrap: complete`
""",
        encoding="utf-8",
    )
    return f"{today}.md"
