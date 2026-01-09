# /new_agent

Starts the interactive process to create a new agent persona.
See rules: `.cursor/rules/10-agent-builder.mdc`
See rules: `.cursor/rules/00-router.mdc`
See rules: `.cursor/rules/99-environment.mdc`

Profile: **Agent Builder**
Action:
1.  Read `.cursor/agents/common/agent-schema.json`.
2.  Interview the user to fill the schema.
3.  Generate agent files and update the router.
