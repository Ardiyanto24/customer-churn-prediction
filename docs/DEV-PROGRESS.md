# DEV-PROGRESS.md
# Source of truth for current position across sessions.
# Updated automatically by post-commit-update-progress.sh after each task commit.
# Read this file at the start of every session before executing anything.

---

## CATATAN AWAL

DEV-01 dikerjakan secara manual sebelum Claude Code digunakan.
Tidak ada commit history dari Claude Code untuk DEV-01 — ini wajar dan bukan masalah.
Sebelum memulai DEV-02, verifikasi struktur sudah benar dengan:
  `tree customer-churn-prediction/ -L 2`
  `python -c "from config import settings; print(settings.API_PORT, settings.RANDOM_SEED)"`

---

## STATUS OVERVIEW

| Phase | Steps | Status |
|---|---|---|
| DEV-01 | 4 steps | ✅ Complete (manual) |
| DEV-02 | 4 steps | ✅ Complete (manual) |
| DEV-03 | 5 steps | ⬜ Not started |
| DEV-04 | 5 steps | ⬜ Not started |
| DEV-05 | 3 steps | ⬜ Not started |
| DEV-06 | 5 steps | ⬜ Not started |
| DEV-07 | 3 steps | ⬜ Not started |
| DEV-08 | 9 steps | ⬜ Not started |

---

## DEV-01: Repository & Project Setup
> Dikerjakan secara manual. Semua task selesai.

### Step 1 — Folder Structure Initialization
- [x] Task 1.1.1 — create root-level files (README.md, .gitignore, .env, .env.example)
- [x] Task 1.1.2 — create config/ folder with __init__.py and settings.py (empty)
- [x] Task 1.2.1 — create data/ subfolders with .gitkeep
- [x] Task 1.3.1 — create models/artifacts/ with .gitkeep
- [x] Task 1.3.2 — create reports/xai_report/ with .gitkeep
- [x] Task 1.4.1 — create src/ structure with all module files (empty)
- [x] Task 1.5.1 — create api/ structure with all module files (empty)
- [x] Task 1.5.2 — create app/ structure with all page files (empty)
- [x] Task 1.6.1 — create tests/ structure with all test files (empty)

### Step 2 — .gitignore and .env.example
- [x] Task 2.1.1 — fill .gitignore (env, data, models, reports, IDE, wandb)
- [x] Task 2.2.1 — fill .env.example with all variable templates and comments

### Step 3 — config/settings.py
- [x] Task 3.1.1 — data and column constants (TARGET_COLUMN, NUMERIC_COLS, etc.)
- [x] Task 3.1.2 — split and reproducibility constants (RANDOM_SEED, TEST_SIZE, VAL_SIZE)
- [x] Task 3.2.1 — XAI quality gate constants (EXPECTED_IMPORTANT_FEATURES, XAI_TOP_N, XAI_MIN_OVERLAP)
- [x] Task 3.3.1 — path constants using pathlib (PROJECT_ROOT, DATA_*, MODELS_DIR, MODEL_PATH)
- [x] Task 3.4.1 — WandB artifact constants (WANDB_PROJECT, WANDB_ENTITY, artifact names)
- [x] Task 3.4.2 — API server constants (API_HOST, API_PORT, API_BASE_URL)

### Step 4 — Requirements Files
- [x] Task 4.1.1 — create requirements-base.txt
- [x] Task 4.2.1 — create requirements-api.txt
- [x] Task 4.3.1 — create requirements-ui.txt
- [x] Task 4.4.1 — create requirements-dev.txt
- [x] Task 4.4.2 — create requirements.txt (convenience wrapper)

> Verification tasks (Step 5) are run manually — not tracked here.

---

## DEV-02: FastAPI Service
> Dikerjakan secara manual. Semua task selesai.

### Step 1 — Shared Utilities
- [x] Task 1.1.1 — implement get_logger (StreamHandler + FileHandler, LOG_LEVEL env)
- [x] Task 1.2.1 — implement save_artifact and load_artifact

### Step 2 — Pydantic Schemas
- [x] Task 2.1.1 — CustomerInput schema (20 fields, constraints, example, docstring)
- [x] Task 2.2.1 — PredictionResult schema (churn_prediction, probability, risk_level, shap_values)
- [x] Task 2.2.2 — PredictionResponse, BatchPredictionItem, BatchPredictionResponse
- [x] Task 2.2.3 — HealthResponse schema

### Step 3 — Predictor
- [x] Task 3.1.1 — ModelPredictor class with load_artifacts method
- [x] Task 3.1.2 — _prepare_dataframe method
- [x] Task 3.2.1 — predict method (single inference)
- [x] Task 3.2.2 — predict_batch method (batch inference)
- [x] Task 3.3.1 — compute_shap method (with VotingClassifier surrogate handling)
- [x] Task 3.3.2 — predictor singleton instance

### Step 4 — FastAPI Application
- [x] Task 4.1.1 — app initialization, lifespan context manager
- [x] Task 4.1.2 — CORS middleware and global exception handler
- [x] Task 4.2.1 — GET /health endpoint
- [x] Task 4.3.1 — POST /predict endpoint
- [x] Task 4.3.2 — POST /predict/batch endpoint
- [x] Task 4.3.3 — POST /predict/batch-csv endpoint
- [x] Task 4.4.1 — GET / root endpoint
- [x] Task 4.4.2 — uvicorn entrypoint block

> Verification tasks (Step 5) are run manually — not tracked here.

---

## DEV-03: Streamlit UI

### Step 1 — Shared Components
- [ ] Task 1.1.1 — api_client.py: check_health function
- [ ] Task 1.1.2 — api_client.py: predict_single function
- [ ] Task 1.1.3 — api_client.py: predict_batch_json and predict_batch_csv functions
- [x] Task 1.2.1 — result_card.py: render_result_card component
- [x] Task 1.3.1 — shap_chart.py: render_shap_bar_chart component

### Step 2 — Entry Point
- [ ] Task 2.1.1 — app/main.py: st.set_page_config
- [ ] Task 2.1.2 — app/main.py: sidebar with navigation and API status
- [ ] Task 2.1.3 — app/main.py: home page content

### Step 3 — Single Prediction Page
- [ ] Task 3.1.1 — prediction.py: page config and st.form setup
- [ ] Task 3.1.2 — prediction.py: 20 input fields in 3 columns
- [ ] Task 3.2.1 — prediction.py: form submit logic and API call
- [ ] Task 3.2.2 — prediction.py: result rendering (result_card + shap_chart)

### Step 4 — Batch Prediction Page
- [ ] Task 4.1.1 — batch_prediction.py: file uploader
- [ ] Task 4.1.2 — batch_prediction.py: CSV preview and template download
- [ ] Task 4.2.1 — batch_prediction.py: run batch prediction button
- [ ] Task 4.2.2 — batch_prediction.py: results table with color highlight and download

### Step 5 — Analytics Page
- [ ] Task 5.1.1 — analytics.py: model status section
- [ ] Task 5.2.1 — analytics.py: XAI visualizations with tabs (SHAP, Permutation, Built-in)
- [ ] Task 5.2.2 — analytics.py: SHAP force plot expander
- [ ] Task 5.3.1 — analytics.py: batch distribution charts from session state

> Verification tasks (Step 6) are run manually — not tracked here.

---

## DEV-04: Testing Suite

### Step 1 — pytest Config and Shared Fixtures
- [ ] Task 1.1.1 — create pytest.ini with markers and addopts
- [ ] Task 1.2.1 — conftest.py: sample_raw_row fixture
- [ ] Task 1.2.2 — conftest.py: sample_raw_df fixture (20 rows, realistic variation)
- [ ] Task 1.2.3 — conftest.py: dummy_preprocessor fixture (session scope)
- [ ] Task 1.2.4 — conftest.py: dummy_model fixture (LogisticRegression on synthetic data)
- [ ] Task 1.2.5 — conftest.py: api_client fixture (TestClient with injected dummy model)

### Step 2 — Unit Test: Preprocessing
- [ ] Task 2.1.1 — TestStructuralEncoder (no_internet vs no, no_phone vs no, fit-only)
- [ ] Task 2.1.2 — TestFeatureEngineering (tc_residual, monthly_to_total_ratio)
- [ ] Task 2.2.1 — TestPipelineLeakage (fit only on train, transform-only on val/test)

### Step 3 — Unit Test: Metrics
- [ ] Task 3.1.1 — TestMetrics: PR-AUC, ROC-AUC, F1 score calculations
- [ ] Task 3.1.2 — TestMetrics: edge cases (all positive, all negative predictions)

### Step 4 — Unit Test: XAI Validator
- [ ] Task 4.1.1 — TestXAIValidator: passes when expected features in top-N
- [ ] Task 4.1.2 — TestXAIValidator: fails when overlap below XAI_MIN_OVERLAP
- [ ] Task 4.1.3 — TestXAIValidator: prefix matching for OHE features (Contract_*)
- [ ] Task 4.1.4 — TestXAIValidator: uses constants from config/settings.py

### Step 5 — Integration Test: API
- [ ] Task 5.1.1 — conftest integration: api_client fixture setup and teardown
- [ ] Task 5.1.2 — conftest integration: degraded_api_client fixture
- [ ] Task 5.2.1 — TestPredictEndpoint: 200 valid input, schema validation, shap_values present
- [ ] Task 5.2.2 — TestPredictWhenModelNotReady: 503 when model not loaded
- [ ] Task 5.3.1 — TestBatchPredictEndpoint: correct count, empty list 422, over limit 422
- [ ] Task 5.3.2 — TestBatchCsvEndpoint: valid CSV 200, non-csv 422, missing column 422, drops id/Churn

> Verification tasks (Step 6) are run manually — not tracked here.

---

## DEV-05: Dockerization

### Step 1 — .dockerignore
- [ ] Task 1.1.1 — create .dockerignore (dev artifacts, data, notebooks, dev requirements)

### Step 2 — Dockerfile.api
- [ ] Task 2.1.1 — base image, WORKDIR, ENV (PYTHONDONTWRITEBYTECODE, PYTHONUNBUFFERED, PYTHONPATH)
- [ ] Task 2.1.2 — system dependencies (libgomp1, libglib2.0-0, curl)
- [ ] Task 2.1.3 — Python dependencies layer (requirements-base + requirements-api)
- [ ] Task 2.2.1 — source code COPY (config/, src/, api/)
- [ ] Task 2.2.2 — model artifacts COPY (models/artifacts/)
- [ ] Task 2.3.1 — EXPOSE 7860, HEALTHCHECK, ENV API_PORT=7860
- [ ] Task 2.3.2 — CMD (uvicorn entrypoint)

### Step 3 — Dockerfile.ui
- [ ] Task 3.1.1 — base image, WORKDIR, ENV
- [ ] Task 3.1.2 — system dependencies
- [ ] Task 3.1.3 — Python dependencies layer (requirements-base + requirements-ui)
- [ ] Task 3.2.1 — source code COPY (config/, src/utils/, app/, reports/xai_report/)
- [ ] Task 3.2.2 — .streamlit/config.toml for server port and address
- [ ] Task 3.3.1 — EXPOSE 7860, HEALTHCHECK, CMD (streamlit run)

> Verification tasks (Step 4, Step 5) are run manually — not tracked here.

---

## DEV-06: Hugging Face Spaces Setup

### Step 1 — HF Token and git-lfs Setup
- [ ] Task 1.1.1 — generate HF write token, save to .env as HF_TOKEN
- [ ] Task 1.2.1 — git lfs install, track models/artifacts/*.joblib, commit .gitattributes

### Step 2 — Create and Deploy Space 1 (API)
- [ ] Task 2.1.1 — create tccp-api Space on HF (Docker SDK, CPU Basic, Public)
- [ ] Task 2.2.1 — create hf_spaces/tccp-api/README.md with YAML frontmatter
- [ ] Task 2.3.1 — build hf_spaces/tccp-api/ folder structure
- [ ] Task 2.4.1 — init git repo, push to HF Space 1
- [ ] Task 2.4.2 — verify Space 1 build succeeds and status is Running

### Step 3 — Create and Deploy Space 2 (UI)
- [ ] Task 3.1.1 — create tccp-ui Space on HF (Docker SDK, CPU Basic, Public)
- [ ] Task 3.2.1 — set API_BASE_URL in HF Space 2 Settings
- [ ] Task 3.3.1 — create hf_spaces/tccp-ui/README.md with YAML frontmatter
- [ ] Task 3.4.1 — build hf_spaces/tccp-ui/ folder structure
- [ ] Task 3.4.2 — verify no models/ in Dockerfile.ui copy
- [ ] Task 3.5.1 — init git repo, push to HF Space 2
- [ ] Task 3.5.2 — verify Space 2 build succeeds and API status shows Connected

### Step 4 — Post-Deploy Configuration
- [ ] Task 4.1.1 — add cold start comment to api_client.py, commit to GitHub

### Step 5 — End-to-End Verification on HF
- [ ] Task 5.1.1 — run 5 manual tests (health, swagger, single predict, batch, analytics)
- [ ] Task 5.1.2 — record Space URLs and git remote URLs to DEPLOYMENT_URLS.md
- [ ] Task 5.2.1 — verify cold start graceful behavior

> All DEV-06 tasks involve manual browser and CLI actions.

---

## DEV-07: CI/CD Pipeline (GitHub Actions)

### Step 1 — GitHub Repository Secrets and Variables
- [ ] Task 1.1.1 — add HF_TOKEN and HF_USERNAME to GitHub Secrets
- [ ] Task 1.2.1 — add HF_SPACE_API_NAME and HF_SPACE_UI_NAME to GitHub Variables

### Step 2 — ci-cd.yml Workflow File
- [ ] Task 2.1.1 — header, triggers (push, pull_request, workflow_dispatch), paths-ignore
- [ ] Task 2.2.1 — workflow-level env vars (PYTHON_VERSION, IMAGE_API, IMAGE_UI)
- [ ] Task 2.3.1 — job: lint (flake8, black --check, isort --check-only)
- [ ] Task 2.4.1 — job: test (pytest unit + integration)
- [ ] Task 2.4.2 — job: test (coverage report artifact upload)
- [ ] Task 2.5.1 — job: build (docker build API)
- [ ] Task 2.5.2 — job: build (docker build UI)
- [ ] Task 2.5.3 — job: build (smoke test health check)
- [ ] Task 2.6.1 — job: deploy (condition: push to main only)
- [ ] Task 2.6.2 — job: deploy (git config for HF push)
- [ ] Task 2.6.3 — job: deploy (push to HF Space 1 API)
- [ ] Task 2.6.4 — job: deploy (push to HF Space 2 UI)
- [ ] Task 2.7.1 — job: notify (pipeline summary to GITHUB_STEP_SUMMARY)

### Step 3 — Pipeline Verification
- [ ] Task 3.1.1 — commit ci-cd.yml, verify pipeline triggers
- [ ] Task 3.1.2 — verify lint job passes
- [ ] Task 3.1.3 — verify test job passes with coverage artifact
- [ ] Task 3.1.4 — verify build job passes
- [ ] Task 3.1.5 — verify deploy job pushes to both HF Spaces
- [ ] Task 3.2.1 — create test PR, verify deploy does not run on PR
- [ ] Task 3.2.2 — merge PR, verify full pipeline runs on merge
- [ ] Task 3.3.1 — push README change, verify pipeline not triggered
- [ ] Task 3.4.1 — trigger pipeline manually via workflow_dispatch

---

## DEV-08: README & Portfolio Documentation

### Step 1 — README Header and Badges
- [ ] Task 1.1.1 — CI badge, Python badge, HF Space badges, license badge
- [ ] Task 1.2.1 — H1 title, tagline, live demo links

### Step 2 — Project Overview
- [ ] Task 2.1.1 — section "What This Project Demonstrates" (4 bullet points)
- [ ] Task 2.2.1 — section "Problem Statement"

### Step 3 — Architecture Section
- [ ] Task 3.1.1 — section "ML Pipeline" with ASCII diagrams and XAI gate explanation
- [ ] Task 3.2.1 — section "Deployment Architecture" with two-Space diagram

### Step 4 — Model Performance
- [ ] Task 4.1.1 — section "Model Performance" with actual metric values

### Step 5 — Quick Start
- [ ] Task 5.1.1 — Quick Start Option A (local without Docker)
- [ ] Task 5.1.2 — Quick Start Option B (Docker)

### Step 6 — API Reference
- [ ] Task 6.1.1 — section "API Reference" with endpoint table and curl examples

### Step 7 — Scaling to Production
- [ ] Task 7.1.1 — current infrastructure decisions and constraints
- [ ] Task 7.1.2 — production-ready alternatives (model registry, k8s, monitoring)

### Step 8 — Repository Structure and CHANGELOG
- [ ] Task 8.1.1 — section "Repository Structure" (two-level tree with annotations)
- [ ] Task 8.2.1 — section "CI/CD Pipeline Overview" with ASCII diagram
- [ ] Task 8.3.1 — create CHANGELOG.md with 5 version milestones

### Step 9 — Verification and Final Commit
- [ ] Task 9.1.1 — read README as interviewer, verify all links and metrics
- [ ] Task 9.1.2 — verify GitHub rendering (badges, code blocks, anchor links)
- [ ] Task 9.2.1 — final commit and push README + CHANGELOG