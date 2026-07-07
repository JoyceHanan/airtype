# ADR 0001: Record Architecture Decisions

## Status
Approved

## Context
We are starting a long-term software engineering project called **AirType**. The system involves a React frontend, Node.js gateway server, and Python ML service. To ensure that the design choices, trade-offs, and design constraints are well-documented and accessible to any developer joining the project over its lifecycle, we need a standard process for documenting decisions.

## Decision
We will use Architectural Decision Records (ADRs) to document significant architectural choices, tech stack changes, algorithm selections, and software designs. 

- ADRs will be written in Markdown format and stored in the [`docs/adrs/`](file:///docs/adrs/) directory.
- File names will follow the sequential format: `NNNN-short-description.md` (e.g., `0002-tap-detection-method.md`).
- Each ADR will follow a standard structure:
  - **Title**
  - **Status** (Proposed, Accepted, Rejected, Deprecated, Superseded)
  - **Context** (Why this choice is being considered, alternatives, trade-offs)
  - **Decision** (The chosen solution and rationale)
  - **Consequences** (Impact on development, testing, performance, maintenance, future scalability)

## Consequences
- Every major technical decision will have a clear trace showing why a specific path was chosen.
- Reduced onboarding friction for new developers.
- Avoids repetitive debates on previously solved architectural problems.
- Minor overhead in writing and updating ADR files when making major changes.
