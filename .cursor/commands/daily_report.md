# /daily_report

Activation of Daily Work Reporter mode.
See rules: `.cursor/rules/10-work-reporter.mdc`
See rules: `.cursor/rules/00-router.mdc`
See rules: `.cursor/rules/99-environment.mdc`

Profile: **Work Reporter**.

## Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `repos_path` | `~/repos` | Directory to scan for git repositories |
| `clickup_list` | `168529345` | ClickUp List ID for daily tasks |
| `date` | today | Report date (YYYY-MM-DD format) |
| `include_uncommitted` | `false` | Include uncommitted changes in report |
| `include_agents` | `true` | Include agent activity section |

## Usage Examples
```bash
/daily_report                              # Default: scan ~/repos, post to ClickUp
/daily_report repos_path=~/work            # Custom repos path
/daily_report date=2025-12-20              # Report for specific date
/daily_report clickup_list=123456789       # Different ClickUp list
/daily_report include_uncommitted=true     # Include uncommitted work
```

## What it does

### 1. 🔍 Git Analysis
- Scans all git repositories in `repos_path`
- Collects **commits** made today
- Analyzes **diff statistics** (files, insertions, deletions)
- Captures **uncommitted changes** (work in progress)
- Notes **current branch** for context

### 2. 🤖 Agent Activity (Agents repo)
- Identifies agents used/invoked today
- Lists new agents or commands created
- Shows modified rules/skills

### 3. 📊 Report Generation
- Structures report using BLUF (Bottom Line Up Front)
- Creates detailed commit tables per repository
- Aggregates statistics across all repos

### 4. 🎯 ClickUp Integration
- Finds today's task in specified List (pattern: `{YYYY.MM.DD}*`)
- Posts formatted Markdown comment with work summary

## Output
```
✅ Scanned: 15 repositories
📝 Active repos: 3 (Agents, AviStocks, ExchangeBot)
📊 Commits: 12 | Files: 45 | Lines: +320/-89
🤖 Agents used: 4 (software_engineer, ai_senior_engineer, ...)
🎯 ClickUp: "2025.12.21 Воскресенье" (HOME-2978)
💬 Comment posted ✓
```
