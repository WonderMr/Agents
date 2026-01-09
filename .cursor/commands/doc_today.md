# /doc_today

Create or update today's architecture documentation file.
See rules: `.cursor/rules/10-tech-writer.mdc`
See rules: `.cursor/rules/00-router.mdc`
See rules: `.cursor/rules/99-environment.mdc`

Profile: **Tech Writer**
Action:
1. Execute a shell command to get the current date in YYYY-MM-DD format (e.g., `date +%F`).
2. Construct the target file path: `docs/<YYYY-MM-DD>-architecture.md`.
3. Check if the file exists using `ls`.
4. If the file does **not** exist:
   - Create it using the structure from `@docs/2025-12-13-architecture.md` as a template.
   - Update the "Date" field in the header.
   - Ensure the content reflects the current project structure (check `src/`, `.cursor/`, `scripts/` directories if needed).
5. If the file **does** exist:
   - Read the file.
   - Review its content against the current codebase.
   - Update any outdated sections or append new architectural findings.
6. Open the file for the user to see.
