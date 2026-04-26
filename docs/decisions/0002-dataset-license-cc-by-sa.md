# 0002: Dataset license — CC BY-SA 4.0

**Status**: Accepted

## Context

The dataset consists of frames extracted from CC-licensed YouTube videos. The majority of current sources are CC BY 4.0. When creating a derivative work from CC BY content, any license is permitted (CC BY does not require share-alike). However, if CC BY-SA 4.0 sources are ever included, the derivative must also be CC BY-SA 4.0.

## Decision

License the dataset under CC BY-SA 4.0 now, rather than CC BY 4.0. This is the more conservative choice: it pre-emptively accommodates any CC BY-SA sources that may be added, avoids a future license migration, and ensures the benchmark remains freely usable and shareable with attribution.

## Consequences

- Researchers can use the dataset freely with attribution
- Derivative datasets must also be CC BY-SA 4.0
- The code (GPL-3.0) and dataset (CC BY-SA 4.0) have different licenses; this is standard practice and clearly documented in the README
