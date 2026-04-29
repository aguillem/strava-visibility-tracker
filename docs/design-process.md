# Project Design Process

> 🤖 **AI Transparency Notice:** This document was written with AI assistance (Claude by Anthropic). The decisions, requirements and validations are human-driven; the drafting and structuring were AI-assisted. See [AI Transparency](./ai-transparency.md) for details.

This document describes the step-by-step process followed to design, build and publish this project. It serves as a living record of where we are and what comes next.

---

## Steps Overview

| # | Step | Status |
|---|------|--------|
| 1 | Functional Specifications | ✅ Done |
| 2 | Acceptance Tests | 🔄 In progress |
| 3 | Technical Choices & Best Practices | ⬜ To do |
| 4 | README & User Documentation | ⬜ To do |
| 5 | Project Skeleton | ⬜ To do |
| 6 | CI Pipeline (lint, unit tests on commit) | ⬜ To do |
| 7 | Code Generation & Unit Tests | ⬜ To do |
| 8 | Review & Validation (acceptance tests) | ⬜ To do |
| 9 | Execution Pipeline (scheduled & manual) | ⬜ To do |
| 10 | Publication & Open Source Release | ⬜ To do |

---

## Step 1 — Functional Specifications ✅

**Goal:** Define precisely what the tool does, what rules it applies, and how it behaves.

**Output:** [`docs/functional-spec.md`](./functional-spec.md)

**Approach:** Requirements were gathered through a structured conversation, then formalised into a specification document with AI assistance.

---

## Step 2 — Acceptance Tests 🔄

**Goal:** Define a set of human-readable test scenarios that describe the expected behaviour of the tool in concrete situations. These scenarios serve as the contract between the specification and the implementation.

**Output:** `docs/acceptance-tests.md` *(in progress)*

**Approach:** Scenarios are derived directly from the functional specification, covering nominal cases, edge cases and error cases. They will later be used to validate the generated code.

---

## Step 3 — Technical Choices & Best Practices ⬜

**Goal:** Decide on the technology stack, project structure, dependencies, architecture and coding standards before any code is written.

**To be defined:**
- Runtime and language
- Project structure and naming conventions
- Key dependencies (HTTP client, Strava auth, report generation)
- Coding standards: linting rules, formatting, commit conventions
- Local development setup

---

## Step 4 — README & User Documentation ⬜

**Goal:** Write a clear and welcoming README for the open source community before the code is generated, so it can also serve as context for Claude Code.

**To cover:**
- What the project does (with the Strava context)
- Prerequisites
- One-time OAuth setup (how to get the Strava refresh token)
- How to configure and run locally
- How to set up on GitLab CI/CD
- How to contribute

---

## Step 5 — Project Skeleton ⬜

**Goal:** Initialise the project structure with the chosen stack — empty source files, configuration files, dependencies — without any business logic yet.

**Approach:** Generated with Claude Code based on the technical choices defined in Step 3. The skeleton is committed to the repository before any pipeline or business logic is added.

---

## Step 6 — CI Pipeline (lint, unit tests on commit) ⬜

**Goal:** Set up the validation pipeline so that every commit is automatically checked from the very first line of business code.

**To cover:**
- Linting and formatting checks
- Unit test execution
- Pipeline triggered on every push / merge request

This pipeline is intentionally set up before code generation, so that the generated code is validated automatically from the first commit.

---

## Step 7 — Code Generation & Unit Tests ⬜

**Goal:** Generate the full business logic and unit tests using Claude Code, based on the functional specifications and acceptance tests.

**Approach:** Claude Code is given the specification, acceptance tests and README as context and generates the complete implementation. Each commit triggers the CI pipeline defined in Step 6. No manual coding expected.

---

## Step 8 — Review & Validation (acceptance tests) ⬜

**Goal:** Review the generated code for correctness, readability and security. Run the acceptance tests against the actual implementation.

**Approach:** Human review of all generated files. Acceptance tests executed manually. Any issues fed back to Claude Code for correction.

---

## Step 9 — Execution Pipeline (scheduled & manual) ⬜

**Goal:** Configure the execution pipeline that runs the script on a schedule or on manual trigger, and exposes the generated report as a pipeline artifact.

**To cover:**
- Secret variable configuration (Strava credentials)
- Artifact storage for generated reports
- Default schedule configuration (monthly)
- Manual trigger with configurable parameters

This pipeline is set up after the code is validated, as it depends on a working implementation.

---

## Step 10 — Publication & Open Source Release ⬜

**Goal:** Make the project publicly available and discoverable.

**To be defined:**
- Repository visibility (GitLab + GitHub mirror)
- Licence choice
- Topics / tags for discoverability
- Initial release / changelog