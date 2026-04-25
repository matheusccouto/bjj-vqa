---
name: files-owned
description: Limit changes to the files declared in the issue's "files owned" section. Make sure to use this skill whenever the user is implementing a GitHub issue, opening a PR, or modifying files based on a spec. Use it on every coding task that has a defined scope.
---

# Files-owned discipline

When implementing a GitHub issue or any scoped change:

1. Read the issue body and locate the "files owned" section (or equivalent scope declaration)
2. List the files you plan to touch
3. Cross-check that every file in your plan is within the declared scope
4. If a needed change requires touching a file outside the scope, stop and ask the user. Do not silently expand scope.
5. When in doubt, prefer creating a new file inside the declared scope over modifying a file outside it
6. After implementation, list the files you actually touched and confirm they all fit the scope

This discipline keeps PRs reviewable and prevents merge conflicts when work is parallelized across agents.
