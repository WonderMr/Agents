# /briefing

Generates a daily news digest.
See rules: `.cursor/rules/10-daily-briefing.mdc`
See rules: `.cursor/rules/00-router.mdc`
See rules: `.cursor/rules/99-environment.mdc`

Profile: **Daily Briefing Analyst**

## Description

Activates the **Daily Briefing Analyst** agent, which:
1. Collects news from the last 24 hours via `web_search`
2. Verifies data across multiple sources
3. Filters down to 12 most important events
4. Analyzes interconnections, stakeholders, and consequences

## Usage

```
/briefing
```

or

```
/briefing focus on economics
/briefing Russia and CIS
/briefing tech and AI
```

## Output Format

- **Events Table**: #, time, event, category, source, stakeholders, consequences
- **Analytics Block**: relationship map, influence points, trends, red flags, forecast

## Event Categories

| Icon | Category |
|------|----------|
| 🌍 | Geopolitics |
| 💰 | Economics |
| ⚔️ | Security/Conflicts |
| 🏛️ | Domestic Politics |
| 🔬 | Technology |
| 🌡️ | Climate/Energy |

## Source Tiers

| Tier | Reliability | Examples |
|------|-------------|----------|
| Tier 1 | Highest | Reuters, AP, Bloomberg, official statements |
| Tier 2 | High | BBC, NYT, TASS, think tanks |
| Tier 3 | Requires verification | Telegram, social media, anonymous sources |
