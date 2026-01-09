# /alerts_describer

Creates concise engineering cards for infrastructure alerts.
See rules: `.cursor/rules/10-alerts-describer.mdc`
See rules: `.cursor/rules/00-router.mdc`
See rules: `.cursor/rules/99-environment.mdc`

Profile: **Alerts Describer**
Action:
1. Analyze the alert (name, rule, context).
2. Create an engineering card with: Summary, Impact, Diagnostic Commands, Links.
3. Follow the "NOT a recipe" principle — no fix instructions.

## Usage Examples

### Single Alert
```
/alerts_describer HighMemoryUsage
```

### From Alert Rule
```
/alerts_describer
<paste prometheus rule here>
```

### Batch Mode
```
/alerts_describer --batch
<list of alert names>
```

### Review Existing
```
/alerts_describer --review
<existing documentation>
```
