# /install_repo

Initiates the replication of the Agents architecture to a target repository.
See rules: `.cursor/rules/10-install-to-repo.mdc`
See rules: `.cursor/rules/00-router.mdc`
See rules: `.cursor/rules/99-environment.mdc`

Profile: **Repo Installer**
Action:
1.  Ask for the target repository path (if not provided).
2.  Copy `.cursor/`, `mcp.json`, and `src/engine/` (if needed).
3.  Configure the target environment.
