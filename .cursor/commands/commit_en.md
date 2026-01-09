# /commit_en

Commit all changes with an English message.
See rules: `.cursor/rules/10-tech-writer.mdc`
See rules: `.cursor/rules/00-router.mdc`
See rules: `.cursor/rules/99-environment.mdc`

Profile: **Tech Writer**
Action:
1. Run `git add .cursor/ docs/` to explicitly stage architecture and config changes.
2. Run `git add .` to stage all other changes.
3. Run `git diff --cached` to inspect staged changes.
4. Generate a concise Conventional Commits message in **English**, highlighting architecture changes if present.
5. Run `git commit -m "..."` with the generated message.
