# Project Design Process

> 🤖 **AI Transparency Notice:** This document was written with AI assistance (Claude by Anthropic). The decisions, requirements and validations are human-driven; the drafting and structuring were AI-assisted. See [AI Transparency](./ai-transparency.md) for details.

This document describes the step-by-step process followed to design, build and publish this project. It serves as a living record of where we are and what comes next.

---

## Steps Overview

| # | Step | Status |
|---|------|--------|
| 1 | Functional Specifications | ✅ Done |
| 2 | Acceptance Tests | ✅ Done |
| 3 | Technical Choices & Best Practices | ✅ Done |
| 4 | README & User Documentation | ✅ Done |
| 5 | Project Skeleton | ✅ Done |
| 6 | CI Pipeline (lint, unit tests on commit) | ✅ Done |
| 7 | Execution Pipeline (scheduled & manual) | ✅ Done |
| 8 | Code Generation & Unit Tests | ✅ Done |
| 9 | AI-driven Technical & Security Audit | ✅ Done |
| 10 | Review & Validation (acceptance tests) | ✅ Done |
| 11 | Publication & Open Source Release | ⬜ To do |

---

## Step 1 — Functional Specifications ✅

**Goal:** Define precisely what the tool does, what rules it applies, and how it behaves.

**Output:** [`docs/functional-spec.md`](./functional-spec.md)

**Approach:** Requirements were gathered through a structured conversation, then formalised into a specification document with AI assistance.

---

## Step 2 — Acceptance Tests ✅

**Goal:** Define a set of human-readable test scenarios that describe the expected behaviour of the tool in concrete situations. These scenarios serve as the contract between the specification and the implementation.

**Output:** [`docs/acceptance-tests.md`](./acceptance-tests.md)

**Approach:** Scenarios are derived directly from the functional specification, covering nominal cases, edge cases and error cases. They will later be used to validate the generated code.

---

## Step 3 — Technical Choices & Best Practices ✅

**Goal:** Decide on the technology stack, project structure, dependencies, architecture and coding standards before any code is written.

**Output:** [`docs/technical-choices.md`](./technical-choices.md)

---

## Step 4 — README & User Documentation ✅

**Goal:** Write a clear and welcoming README for the open source community before the code is generated, so it can also serve as context for Claude Code.

**Output:** [`README.md`](../README.md)

---

## Step 5 — Project Skeleton ✅

**Goal:** Initialise the project structure with the chosen stack — source files with function signatures and docstrings, test files, configuration files and dependencies — without any business logic yet.

**Approach:** Generated with Claude Code based on the technical choices defined in Step 3. The skeleton is committed to the repository before any business logic is added.

---

## Step 6 — CI Pipeline (lint, unit tests on commit) ✅

**Goal:** Set up the validation pipeline so that every commit is automatically checked from the very first line of business code.

**Output:** [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)

**Covers:**
- Linting and formatting checks (ruff)
- Unit test execution (pytest + coverage)
- Pipeline triggered on every push and pull request

---

## Step 7 — Execution Pipeline (scheduled & manual) ✅

**Goal:** Configure the pipeline that runs the script on a schedule or on manual trigger, and exposes the generated report as a downloadable artifact.

**Output:** [`.github/workflows/execution.yml`](../.github/workflows/execution.yml)

**Covers:**
- Monthly scheduled run (first day of each month at 08:00 UTC)
- Manual trigger with configurable parameters (MODE, DATE_FROM, DATE_TO, ACTIVITY_TYPES)
- Report exposed as a GitHub Actions artifact (retained 90 days)

---

## Step 8 — Code Generation & Unit Tests ✅

**Goal:** Generate the full business logic and unit tests using Claude Code, based on the functional specifications and acceptance tests.

**Approach:** Claude Code is given the specification, acceptance tests, README and skeleton as context and generates the complete implementation. Each commit triggers the CI pipeline defined in Step 6. No manual coding expected.

---

## Step 9 — AI-driven Technical & Security Audit ✅

**Goal:** Identify weaknesses in the generated codebase — correctness issues, security gaps, robustness problems — before human validation against real data.

**Approach:** Claude Code performed an autonomous audit of the entire application, reviewing each module from an adversarial perspective. Findings were classified by criticality and addressed in the same session: code, tests and documentation were all updated in a single commit.

**Key findings addressed:**
- Exception architecture: `sys.exit()` removed from library modules, replaced by typed exceptions propagating up to `main()`
- HTTP hardening: request timeouts and `requests.Session` reuse
- API response guard: missing `access_token` key now raises a typed error
- Markdown injection: pipe characters in activity names escaped in report tables
- OAuth CSRF: `state` parameter added and verified in `get_refresh_token.py`
- OAuth UX: authorization timeout and port-in-use error handling
- Supply chain: third-party GitHub Action pinned to a commit SHA
- Dependency split: runtime vs. dev dependencies separated

See [`docs/ai-transparency.md`](./ai-transparency.md) for the full write-up.

---

## Step 10 — Review & Validation (acceptance tests) ✅

**Goal:** Review the generated code for correctness, readability and security. Run the acceptance tests against the actual implementation.

**Approach:** Human review of all generated files. Acceptance tests executed manually against a real Strava account. Any issues fed back to Claude Code for correction.

---

## Step 11 — Publication & Open Source Release ⬜

**Goal:** Make the project publicly available and discoverable.

**To be defined:**
- Repository visibility (GitHub public)
- Topics / tags for discoverability
- Initial release / changelog