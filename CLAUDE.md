# PR Summary & Risk Generator — CLAUDE.md

## Project Overview

An automated pull request analysis system that triggers on code diffs, invokes **Claude Sonnet** via the **Anthropic API** (API key only — no AWS credentials), and generates structured AI insights (summary, risk notes, one-line tag, test checklist). Integrates with both **GitHub Actions** and **GitLab CI** pipelines to automatically post analysis as comments on every PR/MR.

---

## Technical Stack

| Layer       | Technology                                        |
|-------------|---------------------------------------------------|
| Runtime     | Python 3.12                                       |
| AI Model    | Anthropic API — `claude-sonnet-4-6`               |
| SDK         | `anthropic` Python SDK                            |
| Auth        | `ANTHROPIC_API_KEY` (API key only)                |
| Secrets     | GitHub Secrets / GitLab CI Variables              |
| CI/CD       | GitHub Actions / GitLab CI                        |

---

## System Flow

1. Git diff is generated when a PR/MR is opened or updated.
2. CI/CD pipeline (GitHub Actions or GitLab CI) is triggered automatically.
3. **Diff Collector** validates and sanitizes the diff payload.
4. **Prompt Builder** formats the diff into the Anthropic messages format.
5. **Inference Wrapper** calls Claude Sonnet (`claude-sonnet-4-6`) via the Anthropic API using `ANTHROPIC_API_KEY`.
6. **Response Parser** validates and extracts structured JSON from the model response.
7. Analysis is posted as a PR/MR comment directly from the CI pipeline.

---

## Module Descriptions

| File | Responsibility |
|------|----------------|
| `main.py` | CLI entry point. Orchestrates the full pipeline — reads diff, builds prompt, calls Anthropic API, parses and prints result. |
| `diff_collector.py` | Validates the incoming diff payload, scrubs secrets/tokens via regex, enforces 50,000 char limit. |
| `prompt_builder.py` | Combines system prompt and user template into Anthropic messages format. |
| `system_prompt.py` | Defines the AI role and strict JSON output schema for Claude Sonnet. |
| `user_template.py` | Builds the user message by injecting diff, PR title, and description into a structured template. |
| `inference_wrapper.py` | Calls Claude Sonnet (`claude-sonnet-4-6`) via `anthropic.Anthropic` client with exponential backoff on `RateLimitError`. |
| `response_parser.py` | Parses and validates JSON response from Claude Sonnet, strips markdown fences, returns a typed Pydantic model. |

---

## Anthropic API Configuration

```python
import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    system=SYSTEM_PROMPT,
    messages=[
        {"role": "user", "content": user_message}
    ],
)
```

| Parameter     | Value                    |
|---------------|--------------------------|
| Model ID      | `claude-sonnet-4-6`      |
| Max Tokens    | `2048`                   |
| Client        | `anthropic.Anthropic`    |
| Auth          | `ANTHROPIC_API_KEY` env var |

**No AWS credentials or IAM permissions required.**

---

## CI/CD Setup

### GitHub Actions
- **Workflow file:** `.github/workflows/pr-analysis.yml` at repo root
- **Triggers:** `pull_request` events — `opened`, `synchronize`, `reopened`
- **Diff command:** `git diff origin/$base_ref...HEAD`
- Runs `main.py` directly with the diff as input → posts analysis as PR comment via `github-script`
- **Required secret:** `ANTHROPIC_API_KEY` in GitHub repo Settings > Secrets

### GitLab CI
- **Workflow file:** `.gitlab-ci.yml` at repo root
- **Triggers:** `merge_request_event` only
- **Docker image:** `python:3.12-slim`
- Installs `curl`, `jq`, `git` in `before_script`
- Runs `analyze.sh` for diff generation, calls `main.py` directly, and posts MR comment
- **Required variables:** `ANTHROPIC_API_KEY` and `GITLAB_TOKEN` (Settings > CI/CD > Variables, Protected **OFF**)

---

## Secret Management

| Secret            | Store / Key                                                  |
|-------------------|--------------------------------------------------------------|
| Anthropic API Key | GitHub Secret / GitLab CI Variable (masked): `ANTHROPIC_API_KEY` |
| GitLab Token      | GitLab CI Variable (masked): `GITLAB_TOKEN`                  |

---

## Cost Optimisation

- **Diff size cap:** Truncate diffs > 50,000 chars before inference
- **Max tokens:** `max_tokens=2048` to control output cost
- **Model selection:** `claude-sonnet-4-6` balances quality and cost for diff analysis

---

## Known Issues & Fixes

| Issue | Symptom | Fix |
|-------|---------|-----|
| GitLab remote URL had placeholder | `git push` failed: repository not found | Updated remote URL: `git remote set-url gitlab https://gitlab.com/GuruVithiya/PR-Summary.git` |
| Files not uploaded to GitLab | Repository was empty after push | Files were staged but never committed. Run `git commit` before pushing. |
| `.gitlab-ci.yml` not at repo root | Pipeline showed 0 jobs | Copy `.gitlab-ci.yml` from `pr-summary/` subfolder to repo root. |
| YAML validation error | `jobs:pr-analysis:script config should be a string or nested array` | Move complex shell logic into `analyze.sh`; keep `.gitlab-ci.yml` simple. |
| Custom CI path pointing to old file | Pipeline kept failing after fixing root file | Reset CI/CD config path in GitLab Settings > CI/CD > General pipelines to default `.gitlab-ci.yml`. |
| `git` not found in CI container | `analyze.sh: line 5: git: command not found` | Add `git` to `apt-get install` in `before_script`. |
| Shallow clone — `origin/main` not available | `fatal: ambiguous argument origin/main...HEAD` | Add `git fetch origin $CI_MERGE_REQUEST_TARGET_BRANCH_NAME` before `git diff` in `analyze.sh`. |
| `GITLAB_TOKEN` unauthorized | `{"message":"401 Unauthorized"}` when posting MR comment | Create new GitLab PAT with `api` scope and update `GITLAB_TOKEN` variable. |
| Empty diff on MR with no code changes | Script raised `Missing required field: diff` | Add empty diff check in `analyze.sh` and GitHub Actions: if diff is empty, skip and `exit 0`. |
| GitHub Actions workflow not at repo root | No jobs triggered | Copy workflow file to `.github/workflows/pr-analysis.yml` at repo root. |
| `ANTHROPIC_API_KEY` not set in CI | `anthropic.AuthenticationError: No API key provided` | Set `ANTHROPIC_API_KEY` in GitHub Secrets or GitLab CI Variables (masked, Protected **OFF**). |
| Merge conflicts during rebase | `CONFLICT (add/add)` in `.gitlab-ci.yml` | Abort rebase, resolve conflict manually by keeping working version, then commit. |

---

## Current Status

Both **GitHub Actions** and **GitLab CI** pipelines are fully operational. Every Pull Request on GitHub and every Merge Request on GitLab automatically triggers the AI analysis pipeline using **Claude Sonnet (`claude-sonnet-4-6`) via the Anthropic API** (API key only), posting a structured comment with:
- Modification tag
- Summary
- Risk notes
- Test checklist
