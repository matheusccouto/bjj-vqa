---
name: plan-first
description: Always produce a written plan and wait for user approval before making non-trivial changes. Make sure to use this skill whenever the user gives a task that involves creating multiple files, modifying multiple files, or any work expected to take more than a few minutes. Always use it for tasks tied to a GitHub issue or a multi-step prompt.
---

# Plan first, implement second

For any non-trivial task:

1. Read the relevant files (issue, methodology, existing code)
2. Produce a plan in chat that includes:
   - Files to be created (with one-line purpose each)
   - Files to be modified (with summary of change)
   - Any ambiguities that need user clarification
   - Estimated PR size
3. Wait for the user to approve, refine, or reject the plan
4. Only after approval, make a branch and start implementing
5. If you discover during implementation that the plan was wrong, stop and revise the plan rather than silently changing direction

This applies even when the user seems to expect immediate action. A 30-second plan check prevents 30 minutes of rework.
