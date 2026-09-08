# Candidate Brief — User Management API
v1.0

## Project Overview

The User Management API is a RESTful service for managing users across isolated environments. Each environment maintains its own separate database.


The application exposes CRUD endpoints for user management, scoped by environment. All requests are prefixed with the environment name (e.g., `/dev/users` or `/prod/users`).

---

## Setup Instructions

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running

## Auth Token
Some endpoints are protected by an authorization token. The token for `dev` and `prod` is `mysecrettoken`

### Run the Container

```bash
docker run -p 3000:3000 ghcr.io/danielsilva-loanpro/sdet-interview-challenge:latest
```

The application will be available at `http://localhost:3000`.

### Verify the Application Is Running

```bash
curl http://localhost:3000/dev/users
```

You should receive a JSON array response (empty if no users have been created yet).

---

## API Documentation

The complete API endpoint documentation is provided in the **OpenAPI specification file** located at:

[sdet_challenge_api.yml](https://gist.github.com/danielsilva-loanpro/f72a5821113a53043967b373df3e9aef)

You can view the OpenAPI spec with [this viewer](https://editor.swagger.io/)

This file is the **authoritative source** for all endpoint details, including:

- Available endpoints and HTTP methods
- Request body schemas and required fields
- Response formats and status codes
- Error conditions and their corresponding HTTP status codes
- Valid environment values (`dev` and `prod`)

Use this specification as your reference when writing tests and identifying expected behavior.

---

## Tasks

You are expected to complete the following three tasks as part of this take-home challenge.

### Task 1: Create Test Suites

Write all the test suites that you consider necessary to exercise the API endpoints documented in `sdet_challenge_api.yml`.

| Requirement | Details |
|-------------|---------|
| Language | Any programming language of your choice |
| Target | The application deployed locally via Docker |
| Scope | All endpoints and environments documented in `sdet_challenge_api.yml` |

Your tests should run against the application served at `http://localhost:3000` (or the equivalent host when running inside a CI pipeline).

NOTE: At LoanPro, we use python and TS for testing. You are not required to use those technologies, but it is encouraged.

### Task 2: Set Up a GitHub Actions Pipeline

Configure a GitHub Actions workflow that automates your test suite execution.

| Requirement | Details |
|-------------|---------|
| Dev Stage | A dedicated testing stage that runs the E2E test suite against the `dev` environment |
| Prod Stage | A dedicated testing stage that runs the E2E test suite against the `prod` environment |

Because of exiting bugs, some tests may fail. Because of this, make sure that you run the prod and dev stages in parallel, so that neither environment is blocked because of tests failing.

### Task 3: Identify Bugs

As you develop your test suite, you may discover that the application's behavior does not always match the specification in `sdet_challenge_api.yml`. When you find discrepancies:

1. Write tests that expose the incorrect behavior
2. Write a Markdown file describing the failures

---

## Deliverable Requirements

Your submission must be a **GitHub repository** accessible to the interviewer, containing:

| Deliverable | Description |
|-------------|-------------|
| E2E Test Suite | Source code for your end-to-end test suite |
| GitHub Actions Pipeline | A working `.github/workflows/` configuration |
| Bugs Report | File with the bugs discovered |
| Testing report | Reports created by your testing tool |w

### Evaluation Criteria

| Criteria | What We Look For |
|----------|-----------------|
| Test Coverage | Tests cover all endpoints and both environments |
| Test Quality | Tests are well-structured, readable, and use meaningful assertions |
| Pipeline Correctness | Pipeline runs successfully with separate `dev` and `prod` stages |
| Bug Identification | File with the bugs discovered |

> **⚠️ Important:** Candidates whose tests are not running in the GitHub Actions pipeline will not be considered.

---

## Important Notes

- Please keep your development environment set up and ready to run during the live interview.
- At the end of the live interview, you will be asked to review and debug a piece of code written in Python. If you are not familiar with Python, we encourage you to gain at least some basic experience with the language beforehand.