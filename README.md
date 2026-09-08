# User Management API — BDD Test Framework

This repository contains an end-to-end (E2E) testing framework for the User Management API, built using **Python**, **Behave** (BDD), and **Requests**.

This project is based on the official documentation provided in [`contract_api.yml`](./contract_api.yml) and the [`Candidate Brief — User Management API.md`]

The framework is designed to test the application across different environments (`dev` and `prod`) simply by changing the environment tag during execution.

---

## 📋 Prerequisites

Before running the tests, ensure you have the following installed on your machine:

1. **Docker**: Required to run the application locally.
2. **Python 3.11+**: Required to execute the test suite.
3. **Allure CLI**: Required if you want to generate HTML test reports.

---

## 🚀 Setup & Installation

### 1. Install Python Dependencies

Open your terminal in the root of the project and install the required packages:

```bash
python3 -m pip install -r requirements.txt
```

### 2. Start the Application Locally

The application runs inside a Docker container and exposes port `3000`. Start it in detached mode (`-d`) using the following command:

```bash
docker run -d -p 3000:3000 --name sdet-api-challenge ghcr.io/danielsilva-loanpro/sdet-interview-challenge:latest
```

Wait a few seconds for the application to be ready. You can verify it's running by hitting the endpoint:
```bash
curl http://localhost:3000/dev/users
```
*(You should see an empty JSON array `[]` if it just started).*

---

## 🧪 Running the Tests

The framework uses environment configurations and tags to give you absolute control over execution.

**1. `env` Configuration vs `tags` Filtering:**
- `-D env=dev`: Tells the framework **WHERE** to run (Loads the Base URL and Auth Token for the specified environment).
- `--tags=@dev`: Tells the framework **WHAT** to run (Filters the scenarios so only the ones meant for that environment are executed).

### Run the Dev suite against the `dev` environment:
```bash
python3 -m behave -D env=dev --tags=@dev
```

### Run the Prod suite against the `prod` environment:
```bash
python3 -m behave -D env=prod --tags=@prod
```


### Advanced Tag Filtering 
The framework supports granular execution using tags:
- **Security Tests:** Run `python3 -m behave -D env=dev --tags=@security` to execute only the security scripts.
- **Dynamic Environment Skipping:** If a scenario is tagged with `@prod` but you run the tests targeting `-D env=dev`, the framework will automatically intercept and **Skip** the scenario instead of failing it.

---

## 📊 Generating Allure Reports

The framework is configured to output Allure results. To generate and view a rich HTML report, you must first have the Allure CLI installed.

### Install Allure CLI

```bash
# Using Homebrew MAC Local
brew install allure

# OR using NPM
npm install -g allure-commandline --save-dev
```

### Generating the Report

1. Run the tests with the Allure formatter:
   ```bash
   python3 -m behave -D env=dev --tags=@dev --format allure_behave.formatter:AllureFormatter -o reports/allure-results
   ```

2. Generate the HTML report using the Allure CLI:
   ```bash
   allure generate reports/allure-results -o reports/allure-html --clean --single-file
   ```

---

## ⚙️ GitHub Actions (CI/CD)

The project includes a `.github/workflows/tests.yml` pipeline that automates the execution of these tests on every push or pull request to the `main` branch and on demand.

- **Parallel Execution:** The pipeline runs tests for the `dev` and `prod` environments simultaneously in separate isolated VMs using GitHub Actions jobs.
- **Independent Docker Instances:** Each parallel job has a Docker container dedicated to run tests.
- **Secrets Management:** Authentication tokens are NOT hardcoded in the repository. The pipeline securely injects them at runtime using **GitHub Secrets** (e.g., `${{ secrets.DEV_AUTH_TOKEN }}`).
- **Continuous Execution & Reporting:** We use `continue-on-error: false` so that if a test fails due to an application bug, the pipeline accurately reflects a "failed" (red) status. However, a conditional step (`if: always()`) ensures that the Allure HTML reports are still generated and uploaded as downloadable artifacts for debugging, regardless of the test outcomes.

---

## 🐛 Bug Reporting

As part of the testing process, any discrepancies found between the actual API behavior and the Open API specification (`contract_api.yml`) is documented in the [`bugs_report.md`](./bugs_report.md) file.

---


