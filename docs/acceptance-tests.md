# Acceptance Tests

> 🤖 **AI Transparency Notice:** This document was written with AI assistance (Claude by Anthropic). The decisions, requirements and validations are human-driven; the drafting and structuring were AI-assisted. See [AI Transparency](./ai-transparency.md) for details.

This document defines the acceptance test scenarios for the Strava Activity Visibility Checker. Each scenario describes a concrete situation, the inputs provided, and the exact expected behaviour. These scenarios serve as the contract between the functional specification and the implementation.

---

## How to read these tests

Each test follows this structure:

- **Given** — the initial state (activities in Strava, parameters provided)
- **When** — the script is executed
- **Then** — the expected output and behaviour

---

## AT-01 — Visibility rules

### AT-01-1 — Activity with PR and followers_only visibility is reported as Case A

**Given** an activity with:
- visibility: `followers_only`
- at least one segment effort with `pr_rank = 1`

**When** the script runs

**Then** the activity appears in the report under **Case A — Should be PUBLIC**

---

### AT-01-2 — Activity with PR and only_me visibility is reported as Case A

**Given** an activity with:
- visibility: `only_me`
- at least one segment effort with `pr_rank = 1`

**When** the script runs

**Then** the activity appears in the report under **Case A — Should be PUBLIC**

---

### AT-01-3 — Activity with no PR and public visibility is reported as Case B

**Given** an activity with:
- visibility: `everyone`
- no segment effort with `pr_rank = 1`

**When** the script runs

**Then** the activity appears in the report under **Case B — Should be FOLLOWERS ONLY**

---

### AT-01-4 — Activity with PR and public visibility is not reported

**Given** an activity with:
- visibility: `everyone`
- at least one segment effort with `pr_rank = 1`

**When** the script runs

**Then** the activity does **not** appear in the report

---

### AT-01-5 — Activity with no PR and followers_only visibility is not reported

**Given** an activity with:
- visibility: `followers_only`
- no segment effort with `pr_rank = 1`

**When** the script runs

**Then** the activity does **not** appear in the report

---

### AT-01-6 — Activity with no PR and only_me visibility is not reported

**Given** an activity with:
- visibility: `only_me`
- no segment effort with `pr_rank = 1`

**When** the script runs

**Then** the activity does **not** appear in the report

---

### AT-01-7 — Activity with multiple segments, only one is a PR

**Given** an activity with:
- visibility: `followers_only`
- three segment efforts, of which only one has `pr_rank = 1`

**When** the script runs

**Then** the activity appears in the report under **Case A — Should be PUBLIC**

---

### AT-01-8 — Activity with no segment efforts and public visibility is reported as Case B

**Given** an activity with:
- visibility: `everyone`
- no segment efforts at all

**When** the script runs

**Then** the activity appears in the report under **Case B — Should be FOLLOWERS ONLY**

---

### AT-01-9 — Activity with no segment efforts and followers_only visibility is not reported

**Given** an activity with:
- visibility: `followers_only`
- no segment efforts at all

**When** the script runs

**Then** the activity does **not** appear in the report

---

## AT-02 — Scan mode

### AT-02-1 — Full mode scans all activities

**Given** `MODE=full` and the athlete has activities spread over several years

**When** the script runs

**Then** all activities are scanned regardless of their date

---

### AT-02-2 — Partial mode with DATE_FROM and DATE_TO scans only the date range

**Given** `MODE=partial`, `DATE_FROM=2024-01-01`, `DATE_TO=2024-03-31`

**When** the script runs

**Then** only activities with a start date between 2024-01-01 and 2024-03-31 (inclusive) are scanned

---

### AT-02-3 — Partial mode with DATE_FROM only uses current date as DATE_TO

**Given** `MODE=partial`, `DATE_FROM=2024-01-01`, no `DATE_TO`

**When** the script runs on 2024-06-15

**Then** activities from 2024-01-01 to 2024-06-15 (inclusive) are scanned

---

### AT-02-4 — Default mode scans the last 30 days

**Given** no parameters provided

**When** the script runs on 2024-06-15

**Then** activities from 2024-05-16 to 2024-06-15 are scanned

---

### AT-02-7 — DATE_FROM without MODE is respected

**Given** `DATE_FROM=2024-01-01` and no `MODE`

**When** the script runs

**Then**:
- the mode is `partial`
- activities from 2024-01-01 to today (inclusive) are scanned

---

### AT-02-8 — DATE_FROM and DATE_TO without MODE are both respected

**Given** `DATE_FROM=2024-01-01`, `DATE_TO=2024-03-31`, and no `MODE`

**When** the script runs

**Then**:
- the mode is `partial`
- only activities between 2024-01-01 and 2024-03-31 (inclusive) are scanned

---

### AT-02-5 — DATE_FROM is inclusive

**Given** `MODE=partial`, `DATE_FROM=2024-03-01`, `DATE_TO=2024-03-31`
and an activity starting exactly on 2024-03-01

**When** the script runs

**Then** the activity on 2024-03-01 is included in the scan

---

### AT-02-6 — DATE_TO is inclusive

**Given** `MODE=partial`, `DATE_FROM=2024-03-01`, `DATE_TO=2024-03-31`
and an activity starting exactly on 2024-03-31

**When** the script runs

**Then** the activity on 2024-03-31 is included in the scan

---

## AT-03 — Activity type filter

### AT-03-1 — Single activity type filter

**Given** `ACTIVITY_TYPES=Run` and the athlete has both Run and Ride activities in the date range

**When** the script runs

**Then** only Run activities are scanned; Ride activities are ignored

---

### AT-03-2 — Multiple activity type filter

**Given** `ACTIVITY_TYPES=Run,TrailRun` and the athlete has Run, TrailRun and Ride activities

**When** the script runs

**Then** only Run and TrailRun activities are scanned; Ride activities are ignored

---

### AT-03-3 — No activity type filter includes all types

**Given** no `ACTIVITY_TYPES` parameter and the athlete has Run, Ride and Swim activities

**When** the script runs

**Then** all activity types are scanned

---

### AT-03-4 — Unknown activity type triggers a warning but does not stop execution

**Given** `ACTIVITY_TYPES=Run,UnknownType`

**When** the script runs

**Then**:
- a warning is logged indicating `UnknownType` is not a recognised activity type
- Run activities are still scanned normally
- the script does not exit with an error

---

## AT-04 — Report content

### AT-04-1 — Report contains correct header metadata

**Given** `MODE=partial`, `DATE_FROM=2024-01-01`, `DATE_TO=2024-03-31`, `ACTIVITY_TYPES=Run`
and 10 activities scanned with 3 inconsistencies

**When** the script runs

**Then** the report header contains:
- the generation datetime in ISO 8601 format
- `Mode: partial`
- `Date range: 2024-01-01 → 2024-03-31`
- `Activity types filter: Run`
- `Activities scanned: 10`
- `Inconsistencies found: 3`

---

### AT-04-2 — Report contains correct activity details

**Given** an inconsistent activity with:
- name: `Morning Run`
- date: `2024-02-14`
- type: `Run`
- Strava ID: `123456789`

**When** the script runs

**Then** the report row for this activity contains:
- name: `Morning Run`
- date: `2024-02-14`
- type: `Run`
- link: `https://www.strava.com/activities/123456789`

---

### AT-04-3 — Full mode report shows "All time" as date range

**Given** `MODE=full`

**When** the script runs

**Then** the report header displays `All time` as the date range (instead of a specific date interval)

---

### AT-04-4 — Report shows "no inconsistencies" message when all activities are consistent

**Given** all scanned activities have consistent visibility

**When** the script runs

**Then** the report displays `_No inconsistencies found._` and both Case A and Case B sections are empty

---

### AT-04-5 — Report is generated even when no activities match the filters

**Given** `ACTIVITY_TYPES=Swim` and the athlete has no Swim activities in the date range

**When** the script runs

**Then**:
- the script exits without error
- the report is generated with `Activities scanned: 0` and `Inconsistencies found: 0`

---

### AT-04-6 — Report filename includes run timestamp

**When** the script runs at 2024-06-15 08:30:00 UTC

**Then** the generated report file is named `strava-visibility-report-20240615-083000.md`

---

### AT-04-7 — Console output displays a summary

**When** the script runs and finds 2 Case A and 1 Case B inconsistencies across 15 scanned activities

**Then** the console output (stdout) includes:
- total activities scanned: 15
- Case A inconsistencies: 2
- Case B inconsistencies: 1

---

### AT-04-8 — Partial report contains a warning banner

**Given** the Strava API rate limit was hit during fetching

**When** the report is generated

**Then** the report contains a visible warning banner near the top indicating that the report is partial and that not all activities could be fetched

---

### AT-04-9 — Complete report does not contain a partial warning

**Given** all activities were successfully fetched without hitting the rate limit

**When** the report is generated

**Then** the report does **not** contain any partial report warning

---

## AT-05 — Error handling

### AT-05-1 — Invalid MODE value exits with error

**Given** `MODE=weekly`

**When** the script runs

**Then**:
- the script exits with a non-zero exit code
- an error message clearly states that `weekly` is not a valid value for `MODE`
- no report is generated

---

### AT-05-2 — Missing DATE_FROM in partial mode defaults to last 30 days

**Given** `MODE=partial` and no `DATE_FROM`

**When** the script runs

**Then** the script behaves identically to the default mode: activities from the last 30 days are scanned

---

### AT-05-3 — DATE_FROM after DATE_TO exits with error

**Given** `MODE=partial`, `DATE_FROM=2024-06-01`, `DATE_TO=2024-01-01`

**When** the script runs

**Then**:
- the script exits with a non-zero exit code
- an error message states that `DATE_FROM` must be before or equal to `DATE_TO`
- no report is generated

---

### AT-05-4 — Invalid date format exits with error

**Given** `MODE=partial` and a date parameter (`DATE_FROM` or `DATE_TO`) is set to a value that is not a valid `YYYY-MM-DD` date (e.g. `DATE_FROM=not-a-date` or `DATE_TO=not-a-date`)

**When** the script runs

**Then**:
- the script exits with a non-zero exit code
- an error message clearly states which parameter has an invalid format and that the expected format is `YYYY-MM-DD`
- no report is generated

---

### AT-05-5 — Authentication failure exits with error

**Given** an invalid `STRAVA_REFRESH_TOKEN`

**When** the script runs

**Then**:
- the script exits with a non-zero exit code
- an error message indicates that authentication with the Strava API failed
- no report is generated

---

### AT-05-6 — Rate limit hit generates a partial report

**Given** the Strava API returns a `429 Too Many Requests` response during processing (either on the activity list or on a detail request), and some activities have already been fetched before the limit was hit

**When** the script runs

**Then**:
- the script does **not** exit with an error
- a warning is logged indicating how many activities were fetched before the limit was hit
- a report is generated covering only the activities fetched so far
- the report contains a visible warning banner indicating it is a **partial report** and that the rate limit was reached before all activities could be fetched
- the console summary reflects the number of activities actually scanned

---

### AT-05-6b — Rate limit hit with no activities fetched yet generates an empty partial report

**Given** the Strava API returns a `429 Too Many Requests` response on the very first activity list request (before any activity has been fetched)

**When** the script runs

**Then**:
- the script does **not** exit with an error
- a partial report is generated with `Activities scanned: 0`
- the report contains the partial warning banner

---

### AT-05-7 — Strava API returns an unexpected HTTP error code

**Given** the Strava API returns an unexpected non-success HTTP status code (e.g. `403 Forbidden` or `404 Not Found`) on any request

**When** the script runs

**Then**:
- the script exits with a non-zero exit code
- an error message includes the HTTP status code received
- no report is generated

---

### AT-05-8 — Strava API 5xx error retries once then exits

**Given** the Strava API returns a `500` error on a request

**When** the script runs

**Then**:
- the script retries the request exactly once
- if the retry also fails, the script exits with a non-zero exit code and a descriptive error message
- if the retry succeeds, processing continues normally

---

## AT-06 — Authentication

### AT-06-1 — A fresh access token is obtained on every run

**Given** valid `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET` and `STRAVA_REFRESH_TOKEN`

**When** the script runs

**Then** a token refresh request is made to `https://www.strava.com/oauth/token` before any activity data is fetched

---

### AT-06-2 — Credentials are not present in any generated output

**When** the script runs successfully

**Then** neither the report file nor the console output contains the values of `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET` or `STRAVA_REFRESH_TOKEN`