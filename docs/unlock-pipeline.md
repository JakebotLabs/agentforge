# How to Unlock Your Dev Pipeline

Thank you for sponsoring AgentForge! 🎉

As a Builder ($25+) sponsor, you now have access to the **Dev Pipeline** — CodeBot and OpusBot for autonomous code writing and review.

## Step 1: Accept the Repository Invitation

After sponsoring, GitHub automatically grants you access to the private repo. You should receive an email invitation within a few minutes.

**If you don't see the email:**
1. Go to [github.com/JakebotLabs/agentforge-pipeline](https://github.com/JakebotLabs/agentforge-pipeline)
2. If you see a 404 page, the invitation is pending — check your GitHub notifications
3. Click "Accept invitation"

## Step 2: Install or Update AgentForge

If you already have AgentForge installed:

```bash
agentforge install
```

If you're installing fresh:

```bash
curl -fsSL https://agentsforge.dev/install.sh | bash
```

The installer will now successfully clone the pipeline:

```
🔐 pipeline (Pro feature)...
  ✅ pipeline: Cloned
```

## Step 3: Verify It Works

```bash
agentforge doctor
```

You should see:

```
✅ Config file: ~/.agentforge/agentforge.yml
✅ Memory (ChromaDB): Database found
✅ HealthKit: Monitor found
✅ Dashboard: Found
✅ Pipeline: CodeBot + OpusBot available   ← You have this now!
✅ Python version: 3.12.x
```

## Using the Dev Pipeline

### CodeBot — Autonomous Code Writing

```bash
cd ~/.agentforge/components/pipeline
python -m orchestrate codebot "Create a FastAPI endpoint that returns system health"
```

CodeBot will:
- Write the code
- Create a feature branch
- Run tests
- Report back with results

### OpusBot — Architecture Review

```bash
python -m orchestrate opusbot "Review the auth module in /path/to/project for security issues"
```

OpusBot will:
- Read all relevant code
- Analyze for security, reliability, and design
- Return a structured review with verdict

## Troubleshooting

### "Authentication failed" when cloning pipeline

Make sure you're using the same GitHub account that sponsored:

```bash
git config --global user.name
```

If you sponsored with a different account, you'll need to either:
- Switch your Git credentials to the sponsoring account, or
- Let us know and we can add your other account manually

### Pipeline not showing in `agentforge doctor`

Run the install again:

```bash
agentforge install
```

### Still having issues?

Email [jakebot2ops@gmail.com](mailto:jakebot2ops@gmail.com) with:
- Your GitHub username
- The error message you're seeing

We'll get you sorted within 24 hours.

---

## What's in the Pipeline?

```
~/.agentforge/components/pipeline/
├── orchestrate.py      # Main dispatcher with retry/fallback
├── codebot/
│   ├── SOUL.md         # CodeBot's persona and constraints
│   └── AGENTS.md       # Runtime configuration
└── opusbot/
    ├── SOUL.md         # OpusBot's persona and constraints
    └── AGENTS.md       # Runtime configuration
```

You can customize the SOUL.md and AGENTS.md files to tune how the bots behave for your specific use case.

---

Thank you for supporting AgentForge. You're funding the future of open source AI tooling.

— Jake & Jakebot
