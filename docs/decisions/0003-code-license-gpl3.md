# 0003: Code license — GPL-3.0

**Status**: Accepted (under review)

## Context

The repository contains both a dataset (CC BY-SA 4.0) and Python code for validation, evaluation, and tooling (CLI, scripts). The code license needs to be chosen independently of the dataset license.

Options considered: MIT, Apache-2.0, GPL-3.0.

## Decision

Use GPL-3.0-or-later for the code. The primary motivation was alignment with the copyleft spirit of the CC BY-SA dataset license: if the dataset must be shared alike, it is consistent for the tooling to also require derivative works to remain open.

## Consequences

- Any project that incorporates this code must also release their derivative under GPL-3.0 or later
- This may limit adoption in commercial or proprietary research pipelines
- MIT or Apache-2.0 would lower the barrier to adoption; the maintainer may revisit this decision if it becomes a friction point for the research community
- The dataset license (CC BY-SA 4.0) is unaffected by this decision
