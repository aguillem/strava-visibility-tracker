# 🚴 Strava Visibility Checker

![CI](https://github.com/aguillem/strava-visibility-tracker/actions/workflows/ci.yml/badge.svg)

We all face the same eternal struggle: we want to protect our privacy, yet we desperately need the world to witness our greatest athletic achievements. Nobody needs to know about that rainy Wednesday jog where you were overtaken by a dog. But that segment PR you've been chasing for months? The entire Strava community deserves to celebrate it with you.

The problem is that managing activity visibility manually is tedious and error-prone. Segments get created after the fact, PRs get beaten, and suddenly your old heroic activities are buried on private while your mediocre ones are proudly displayed to the public.

**Strava Visibility Checker** scans your activities, detects visibility inconsistencies based on your segment personal records, and tells you exactly what to fix.

> ⚠️ The Strava API does not allow programmatic updates to activity visibility. This tool produces a report — the final click is yours.

---

## How it works

The rule is simple:

- 🏆 Activity with a **segment PR** → should be **public**
- 🙈 Activity with **no segment PR** → should be **followers only**

The tool detects two types of inconsistencies:

| Case | Situation | What to do |
|------|-----------|------------|
| A | Activity is `followers only` or `only me`, but has a PR | Set it to **public** |
| B | Activity is `public`, but has no PR | Set it to **followers only** |

---

## Prerequisites

- Python 3.13+
- A Strava account with API access enabled
- A GitHub account (for automated scheduling)

---

## Installation

```bash
# Clone the repository
git clone https://github.com/aguillem/strava-visibility-tracker.git
cd strava-visibility-tracker

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Configuration

### Step 1 — Create a Strava API application

1. Go to [strava.com/settings/api](https://www.strava.com/settings/api)
2. Create a new application (name and website can be anything)
3. Note your **Client ID** and **Client Secret**

### Step 2 — Generate your refresh token

This is a one-time manual step. You need a refresh token with the `activity:read_all` scope.

**1. Open the following URL in your browser** (replace `YOUR_CLIENT_ID`):

```
https://www.strava.com/oauth/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=http://localhost&approval_prompt=force&scope=activity:read_all
```

**2. Authorise the application.** You will be redirected to a URL like:

```
http://localhost/?state=&code=AUTHORIZATION_CODE&scope=...
```

Copy the `AUTHORIZATION_CODE` from the URL.

**3. Exchange the code for a refresh token** (replace the placeholders):

```bash
curl -X POST https://www.strava.com/oauth/token \
  -d client_id=YOUR_CLIENT_ID \
  -d client_secret=YOUR_CLIENT_SECRET \
  -d code=AUTHORIZATION_CODE \
  -d grant_type=authorization_code
```

The response contains your `refresh_token`. Copy it.

### Step 3 — Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:

```
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_REFRESH_TOKEN=your_refresh_token
```

---

## Usage

### Run with default settings (last 30 days, all activity types)

```bash
python src/main.py
```

### Scan all activities (full mode)

```bash
MODE=full python src/main.py
```

### Scan a specific date range

```bash
DATE_FROM=2024-01-01 DATE_TO=2024-03-31 python src/main.py
```

`MODE=partial` is the default and can be omitted. `DATE_TO` defaults to today if not specified.

### Filter by activity type

```bash
ACTIVITY_TYPES=Run,TrailRun python src/main.py
```

### Combine options

```bash
DATE_FROM=2024-01-01 ACTIVITY_TYPES=Run,Ride python src/main.py
```

The report is generated as a Markdown file in the `reports/` subfolder:
```
reports/strava-visibility-report-20240615-083000.md
```

A summary is also printed to the console:
```
Activities scanned: 42
Case A (should be public): 3
Case B (should be followers only): 1

Report written to: reports/strava-visibility-report-20240615-083000.md
```

### Rate limit handling

The Strava API allows up to 100 read requests per 15 minutes and 1,000 per day. If the limit is reached mid-run, the script does not stop with an error — it generates a **partial report** covering only the activities fetched so far. The report will contain a visible warning banner to indicate that the results are incomplete.

---

## GitHub Actions — Automated scheduling

### Step 1 — Fork the repository

Fork this repository to your own GitHub account.

### Step 2 — Add your secrets

Go to your fork → **Settings** → **Secrets and variables** → **Actions** → **Secrets** and add:

| Secret | Value |
|--------|-------|
| `STRAVA_CLIENT_ID` | Your Strava client ID |
| `STRAVA_CLIENT_SECRET` | Your Strava client secret |
| `STRAVA_REFRESH_TOKEN` | Your Strava refresh token |

### Step 3 — Set your personal defaults (optional)

Go to **Settings** → **Secrets and variables** → **Actions** → **Variables** to define default values for the scheduled run. These take precedence over the script defaults and can be overridden at any time via manual trigger.

| Variable | Example value | Description |
|----------|---------------|-------------|
| `MODE` | `full` | Scan mode (`full` or `partial`) |
| `DATE_FROM` | `2023-01-01` | Start date (partial mode only) |
| `DATE_TO` | `2024-12-31` | End date (partial mode only) |
| `ACTIVITY_TYPES` | `Run,TrailRun` | Activity types to scan |

### Step 4 — Enable email notifications (optional)

To receive the report by email after each run, add the following in **Settings** → **Secrets and variables** → **Actions**:

**Secrets tab:**

| Secret | Value |
|--------|-------|
| `MAIL_USERNAME` | Your Gmail address |
| `MAIL_PASSWORD` | A Gmail [App Password](https://myaccount.google.com/apppasswords) ¹ |

**Variables tab:**

| Variable | Value |
|----------|-------|
| `MAIL_TO` | Recipient email address |

> ¹ An App Password is a 16-character code generated in your Google account. It requires 2-Step Verification to be enabled. Go to **Google Account → Security → 2-Step Verification → App passwords**.

The email is skipped silently if `MAIL_TO` is not set.

### Step 5 — Enable Actions

Go to the **Actions** tab of your fork and enable GitHub Actions if prompted.

The pipeline runs automatically on the **first day of each month**. The generated report is displayed directly in the Actions run summary and available as a downloadable artifact.

### Trigger a manual run

1. Go to **Actions** → **Strava Visibility Execution**
2. Click **Run workflow**
3. Fill in the optional parameters (leave empty to use your repository variables) and click **Run workflow**

### Change the schedule

Edit `.github/workflows/execution.yml` and update the cron expression:

```yaml
schedule:
  - cron: '0 8 1 * *'  # Every first day of the month at 08:00 UTC
```

---

## Contributing

Contributions are welcome!

### Run the tests

```bash
pytest --cov=src tests/
```

### Run the linter

```bash
ruff check src/ tests/
ruff format src/ tests/
```

All pull requests must pass the CI pipeline (lint + tests) before being merged.

---

## AI Transparency

This project was built with AI assistance. See [docs/ai-transparency.md](docs/ai-transparency.md) for a full explanation of what was AI-assisted, what was AI-generated, and what remained entirely human-driven.

---

## Licence

MIT — see [LICENSE](LICENSE)