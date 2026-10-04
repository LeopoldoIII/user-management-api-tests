# User Management API — BDD Test Framework

This repository contains an end-to-end (E2E) testing framework for the User Management API, built using **Python**, **Behave** (BDD), and **Requests**.

This project is based on the official documentation provided in [`contract_api.yml`](./contract_api.yml) and the [`Candidate Brief — User Management API.md`].

The framework is designed to test the application across different environments (`dev` and `prod`) simply by changing the environment tag during execution.

---

## 📋 Prerequisites

Before running the tests, ensure you have the following installed on your machine:

1. **Docker**: Required if you run the application via container.
2. **Python 3.11+**: Required to execute the test suite and backend server.
3. **Allure CLI**: Required if you want to generate HTML test reports.

---

## 🚀 Setup & Local Execution

### Step 1: Environment Variables & Dependencies

1. **Configure Environment Variables:**
   Copy the `.env.template` file to `.env` in the root directory:
   ```bash
   cp .env.template .env
   ```
   Ensure your `.env` contains the expected authentication tokens (the local backend validates against `mysecrettoken`):
   ```env
   DEV_AUTH_TOKEN="mysecrettoken"
   PROD_AUTH_TOKEN="mysecrettoken"
   ```

2. **Install Python Dependencies:**
   Activate your virtual environment (e.g. `source .venv/bin/activate`) and install the requirements:
   ```bash
   # Test suite dependencies (behave, requests, etc.)
   pip install -r requirements.txt

   # (Optional) Backend dependencies if running server without Docker
   pip install -r server/requirements.txt
   ```

---

### Step 2: Start the API Server Locally

The application needs to run on port `3000`. You can choose between two methods:

#### Option A: Running with Docker (Recommended)
Build and run the container locally from the `server/` directory:

```bash
# 1. Build the local image
docker build -t user-api:local ./server

# 2. Run the container in the background
docker run -d --rm -p 3000:3000 --name api-local user-api:local
```

To stop the container when finished:
```bash
docker stop api-local
```

#### Option B: Running Directly with Python
If you prefer running without Docker:
```bash
python3 server/app.py
```
*(Or with Gunicorn: `cd server && gunicorn -b 0.0.0.0:3000 app:app`)*

#### Verify API Health
Check that the API is responding:
```bash
curl http://localhost:3000/dev/users
```
*(You should see an empty JSON array `[]` if freshly started).*

---

## 🧪 Running the Tests

The framework uses environment configurations and tags to give you absolute control over execution:
- `-D env=dev`: Tells the framework **WHERE** to run (loads the Base URL and Auth Token for the specified environment).
- `--tags=@dev`: Tells the framework **WHAT** to run (filters scenarios meant for that environment).

### 1. Dev Suite
Run the Dev suite against the `dev` environment:
```bash
python3 -m behave -D env=dev --tags=@dev
```

### 2. Prod Suite
Run the Prod suite against the `prod` environment:
```bash
python3 -m behave -D env=prod --tags=@prod
```

### 3. Security Tests
Run only the security verification scenarios:
```bash
python3 -m behave -D env=dev --tags=@security
```

### 4. Running a Specific Feature File
You can target a single feature file directly:
```bash
python3 -m behave features/security.feature -D env=dev
```

---

## 📊 Generating Allure Reports

The framework outputs Allure test results in `reports/allure-results`.

### Install Allure CLI
```bash
# Using Homebrew (macOS)
brew install allure

# OR using NPM
npm install -g allure-commandline --save-dev
```

### View Reports
1. **Run tests with Allure formatter:**
   ```bash
   python3 -m behave -D env=dev --tags=@dev --format allure_behave.formatter:AllureFormatter -o reports/allure-results
   ```

2. **Serve the report directly in your browser:**
   ```bash
   allure serve reports/allure-results
   ```

3. **Or generate a static single-file HTML report:**
   ```bash
   allure generate reports/allure-results -o reports/allure-html --clean --single-file
   ```

---

## ⚙️ GitHub Actions (CI/CD)

The project includes a `.github/workflows/tests.yml` pipeline that automates the execution of these tests on every push or pull request to the `main` branch and on demand.

- **Automated Container Build:** Builds the image from `./server` and caches layers in GitHub Container Registry (`ghcr.io`).
- **Parallel Execution:** Runs tests for `dev` and `prod` environments simultaneously in separate isolated jobs.
- **Secrets Management:** Injects tokens at runtime using GitHub Secrets (`DEV_AUTH_TOKEN`, `PROD_AUTH_TOKEN`).
- **Report Artifacts:** Allure HTML reports are uploaded as artifacts on each run regardless of test outcome.

---

## 🐛 Bug Reporting

Any discrepancies found between the actual API behavior and the OpenAPI specification (`contract_api.yml`) are documented in [`bugs_report.md`](./bugs_report.md).
