# Strava Activity Visibility Checker — Functional Specifications

> 🤖 **AI Transparency Notice:** This document was written with AI assistance (Claude by Anthropic). The decisions, requirements and validations are human-driven; the drafting and structuring were AI-assisted. See [AI Transparency](./ai-transparency.md) for details.

---

## 1. Purpose

Every athlete faces the same existential dilemma: we cherish our privacy, yet we desperately want the world to witness our greatest achievements. Nobody needs to know about that rainy Tuesday jog at a pace that would embarrass a sleepy tortoise. But that segment PR you smashed after months of training? That deserves a standing ovation from the entire Strava community.

The problem is that managing activity visibility manually is tedious and error-prone. Segments get created after the fact, and suddenly your hard-earned PR activities are buried on private while the world is deprived of your heroics.

This tool analyses a Strava athlete's activities and detects **activities that have a segment personal record (PR) but are not publicly visible**.

The core rule is:
- An activity **should be public** if it contains at least one segment effort ranked as a personal record (`pr_rank = 1`) or a global leaderboard ranking.

Since the Strava API does not allow programmatic update of activity visibility, this tool does **not modify any data**. It produces a **report listing activities with hidden PRs** so the athlete can manually fix them in the Strava app or website.

---

## 2. Visibility Rule

An activity is reported as a **hidden PR** when:

| Current Visibility | PR on a Segment | Expected Action |
|--------------------|-----------------|-----------------|
| `followers_only` or `only_me` | yes (≥ 1 PR) | Should be set to **public** |

> **Note:** An activity with **at least one** segment effort where `pr_rank = 1` or with a global leaderboard achievement (`type_id = 2`) is considered to have a PR, regardless of the number of segments on the activity.

> **Visibility values:** Strava exposes three visibility levels: `everyone`, `followers_only`, and `only_me`. Both `followers_only` and `only_me` are considered inconsistent when a PR is present. Activities that are already `everyone` with a PR are correctly public and not reported.

---

## 3. Input Parameters

All parameters are passed as environment variables or CLI arguments.

### 3.1 Scan Mode

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `MODE` | `full` \| `partial` | yes | `full` scans all activities ever recorded. `partial` scans activities within a date range. |
| `DATE_FROM` | ISO 8601 date (`YYYY-MM-DD`) | only if `MODE=partial` | Start of the date range (inclusive). |
| `DATE_TO` | ISO 8601 date (`YYYY-MM-DD`) | no | End of the date range (inclusive). Defaults to **current date** if not provided. |

### 3.2 Filters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ACTIVITY_TYPES` | comma-separated strings | no | Filter activities by type. Accepts one or more Strava activity types (e.g. `Run`, `Ride`, `TrailRun`). If not provided, **all activity types** are included. |

### 3.3 Strava Authentication

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `STRAVA_CLIENT_ID` | string | yes | OAuth2 client ID from Strava API settings. |
| `STRAVA_CLIENT_SECRET` | string | yes | OAuth2 client secret from Strava API settings. |
| `STRAVA_REFRESH_TOKEN` | string | yes | OAuth2 refresh token with `activity:read_all` scope. |

---

## 4. Authentication

The tool uses the **Strava OAuth 2.0** flow.

- Authentication is performed via the **refresh token grant**: on each run, a new access token is obtained using the stored refresh token.
- The required OAuth scope is **`activity:read_all`** (mandatory to access segment efforts and `pr_rank`).
- Credentials are stored as **GitHub Actions secrets** and never committed to the repository.
- The tool does not handle the initial OAuth authorization flow (obtaining the first refresh token). This is a one-time manual step documented in the README.

---

## 5. Processing Logic

```
1. Authenticate → obtain a fresh access token
2. Fetch activities list (paginated) filtered by date range if MODE=partial
3. Apply ACTIVITY_TYPES filter if provided
4. For each activity:
   a. Fetch segment efforts for the activity
   b. Check if at least one effort has pr_rank = 1 or a global leaderboard achievement
   c. If the activity has a PR and is not public → add to report
5. Generate and output the report
```

### 5.1 Strava API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `POST https://www.strava.com/oauth/token` | Refresh access token |
| `GET /athlete/activities` | List activities (paginated, 200 per page max) |
| `GET /activities/{id}` | Fetch full activity details including `visibility` and segment efforts |
| `GET /athlete/activities` with `after`/`before` params | Date range filtering |

> **Note on segment efforts:** Segment efforts including `pr_rank` are returned within the detailed activity object (`GET /activities/{id}`). A separate segment efforts endpoint is not required.

### 5.2 Rate Limiting

The Strava API enforces rate limits (100 requests per 15 minutes, 1000 per day by default). The tool must:
- Implement a **delay between requests** to avoid hitting the 15-minute limit.
- Log a clear error and exit gracefully if a `429 Too Many Requests` response is received.
- Display an estimated request count before starting a `full` scan when the activity count is known.

---

## 6. Output / Report

The report is the **only output** of the tool. It is generated regardless of whether any hidden PRs are found.

### 6.1 Format

The report is a **Markdown file** (`.md`) generated at the end of each run.

### 6.2 Report Structure

```
# Strava Visibility Report
Generated: <ISO 8601 datetime>
Mode: <full | partial>
Date range: <DATE_FROM> → <DATE_TO> (only if MODE=partial)
Activity types filter: <list | none>
Activities scanned: <N>
Hidden PRs found: <N>

---

## Hidden PRs — Should be PUBLIC

Activities that have a segment PR but are not visible to everyone.

| Activity | Date | Type | Strava Link |
|----------|------|------|-------------|
| <name>   | <date> | <type> | [View](<url>) |

---
_No hidden PRs found._ (displayed if no hidden PRs)
```

### 6.3 Strava Activity Link Format

Each activity links to its public Strava page:
```
https://www.strava.com/activities/{activity_id}
```

### 6.4 Report Delivery

- In **GitHub Actions**, the report is exposed as a **workflow artifact** (downloadable from the Actions UI) and displayed in the run summary.
- The report filename includes the run timestamp: `strava-visibility-report-<YYYYMMDD-HHmmss>.md`.
- Console output (stdout) displays a summary (number of activities scanned, number of hidden PRs).

---

## 7. Scheduling & Execution

### 7.1 Scheduled Run (GitHub Actions)

- The pipeline runs automatically on a **configurable cron schedule**.
- The **default schedule is monthly** (`0 8 1 * *` — first day of each month at 08:00 UTC).

### 7.2 Manual Trigger

- The pipeline can be **triggered manually** from the GitHub Actions UI.
- When triggered manually, all input parameters (`MODE`, `DATE_FROM`, `DATE_TO`, `ACTIVITY_TYPES`) can be passed as inputs.

### 7.3 Default Behaviour (no parameters provided)

| Parameter | Default value |
|-----------|---------------|
| `MODE` | `partial` |
| `DATE_FROM` | current date minus 30 days |
| `DATE_TO` | current date |
| `ACTIVITY_TYPES` | all types |

---

## 8. Error Handling

| Situation | Expected Behaviour |
|-----------|--------------------|
| Invalid `MODE` value | Exit with error and descriptive message |
| `DATE_FROM` missing when `MODE=partial` | Default to last 30 days |
| `DATE_FROM` after `DATE_TO` | Exit with error |
| Invalid `ACTIVITY_TYPES` value | Log a warning, skip unknown types, continue |
| Strava API authentication failure | Exit with error |
| Strava API rate limit hit (429) | Generate partial report with warning banner |
| Strava API unexpected error (5xx) | Retry once, then exit with error |
| Activity with no segment efforts | Treated as "no PR" — not reported |
| Empty result (no activities match filters) | Generate report with 0 hidden PRs, no error |

---

## 9. Out of Scope

- Automatic update of activity visibility (not supported by the Strava API).
- Management of the initial OAuth authorization flow (first refresh token generation).
- Support for multiple athletes.
- Web UI or graphical interface.
- Storing historical report data.
- Notifications (email, Slack, etc.).
