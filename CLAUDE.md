# CLAUDE.md — TCCP Customer Churn Prediction
## Deployment Project Context

---

## 1. Project Identity

| Field | Value |
|---|---|
| **Project** | Customer Churn Prediction (TCCP) |
| **Stack** | FastAPI + Streamlit, deployed to Hugging Face Spaces |
| **Language** | Python 3.11 |
| **Experiment Tracking** | Weights & Biases (wandb) |
| **Scope** | Deployment pipeline only (DEV-01 to DEV-08) — ML training already complete |

The ML pipeline (EDA, preprocessing, training, tuning) has been completed in Kaggle notebooks.
This codebase handles **deployment only**: packaging the trained artifacts into a serving API and UI.

---

## 2. Repository Structure

```
customer-churn-prediction/
├── config/settings.py          ← single source of truth for all constants
├── data/raw/                   ← IMMUTABLE — never modify
├── models/artifacts/           ← preprocessor.joblib, model_final.joblib
├── src/                        ← shared ML utilities (preprocessing, XAI, evaluation)
├── api/                        ← FastAPI service (inference only)
├── app/                        ← Streamlit UI (calls API, never loads model directly)
├── tests/                      ← pytest unit + integration tests
├── notebooks/                  ← Kaggle training notebooks — read-only reference
├── reports/xai_report/         ← SHAP plots and evaluation reports
├── docs/                       ← DEV instruction files (DEV-01 to DEV-08)
└── docs/DEV-PROGRESS.md        ← current progress tracker — always up to date
```

---

## 3. Non-Negotiable ML Principles

These apply to every file in this codebase. Violations are bugs, not style choices.

**No Data Leakage**
All fit operations (encoder, scaler, imputer) only on training data.
Validation and test sets are transform-only.

**Training-Serving Parity**
Never rewrite preprocessing logic in `api/`. Always load from `preprocessor.joblib`.
The preprocessor was fit during training — it must be identical at inference time.

**Reproducibility**
All random operations use `RANDOM_SEED = 42` from `config/settings.py`.
Never hardcode `random_state=42` directly — always import from settings.

**Constants from settings.py**
All thresholds, column names, paths, and artifact names come from `config/settings.py`.
Never hardcode values that are defined there.

**data/raw/ is immutable**
No code, script, or Claude Code operation may write to `data/raw/`.
This is enforced by a hook. Any attempt will be blocked.

**Preprocessing stays in api/predictor.py via artifact**
`api/` files may not import from `src/preprocessing/` to re-run logic.
They may only call `preprocessor.transform()` on the loaded artifact.

**Streamlit never loads the model**
`app/` files communicate with FastAPI via HTTP only.
The only exception: `app/pages/analytics.py` reads static image files from `reports/xai_report/`.

---

## 4. DEV Phase Map

| Phase | Description | Depends On | Status |
|---|---|---|---|
| DEV-01 | Repository structure, settings.py, requirements | — | ✅ Done manually |
| DEV-02 | FastAPI service (schemas, predictor, endpoints) | DEV-01 | ⬜ |
| DEV-03 | Streamlit UI (pages, API client, components) | DEV-01 | ⬜ |
| DEV-04 | Testing suite (pytest unit + integration) | DEV-01 | ⬜ |
| DEV-05 | Dockerization (Dockerfile.api, Dockerfile.ui) | DEV-02, DEV-03 | ⬜ |
| DEV-06 | Hugging Face Spaces setup (manual deploy) | DEV-05 | ⬜ |
| DEV-07 | CI/CD pipeline (GitHub Actions) | DEV-04, DEV-05, DEV-06 | ⬜ |
| DEV-08 | README and portfolio documentation | DEV-01 to DEV-07 | ⬜ |

---

## 5. Step Map per DEV Phase

Each DEV phase is divided into steps. One session = one step.
The command to run each step is `/project:devXX-stepY`.

### DEV-01 (4 steps)
- Step 1: Folder structure initialization
- Step 2: .gitignore and .env.example
- Step 3: config/settings.py
- Step 4: Requirements files

### DEV-02 (4 steps)
- Step 1: Shared utilities (logger, serialization)
- Step 2: Pydantic schemas
- Step 3: Predictor (artifact loading, inference, SHAP)
- Step 4: FastAPI application (endpoints)

### DEV-03 (5 steps)
- Step 1: Shared components (api_client, result_card, shap_chart)
- Step 2: Entry point — app/main.py
- Step 3: Single Prediction page
- Step 4: Batch Prediction page
- Step 5: Analytics page

### DEV-04 (5 steps)
- Step 1: pytest config and shared fixtures
- Step 2: Unit test — preprocessing
- Step 3: Unit test — metrics
- Step 4: Unit test — XAI validator
- Step 5: Integration test — API endpoints

### DEV-05 (3 steps)
- Step 1: .dockerignore
- Step 2: Dockerfile.api
- Step 3: Dockerfile.ui

### DEV-06 (5 steps)
- Step 1: HF token and git-lfs setup
- Step 2: Create and deploy Space 1 (API)
- Step 3: Create and deploy Space 2 (UI)
- Step 4: Post-deploy configuration
- Step 5: End-to-end verification on HF

### DEV-07 (3 steps)
- Step 1: GitHub repository secrets and variables
- Step 2: ci-cd.yml workflow file (all 5 jobs)
- Step 3: Pipeline verification (push, PR, paths-ignore, manual trigger)

### DEV-08 (9 steps)
- Step 1: README header and badges
- Step 2: Project overview section
- Step 3: Architecture section
- Step 4: Model performance section
- Step 5: Quick start section
- Step 6: API reference section
- Step 7: Scaling to production section
- Step 8: Repository structure and CHANGELOG
- Step 9: README verification and final commit

---

## 6. Execution Behavior

### Automatic (no confirmation needed)
- Create or edit `.py`, `.md`, `.toml`, `.json`, `.sh`, `.yml`, `.txt`, `.ini` files
- Create directories
- `git add` and `git commit`
- Install packages from requirements files
- Run `black --check` or `flake8` in check mode

### Hard Stop — explicit confirmation required
- `git push` (any push to any remote)
- Overwriting a non-empty existing file that was not created in the current session
- Editing `config/settings.py` (global effect on all constants)
- Any operation touching `models/artifacts/*.joblib`

### Blocked — will not execute
- Any write operation to `data/raw/` (enforced by hook)
- Running `black .` without `--check` flag (use `--check` for verification only)

---

## 7. Per-Task Flow (Automatic Loop)

For each task X.X.X within a step:

```
1. Execute task (generate/edit files per DEV instruction)
2. git add <changed files only>
3. git commit -m "feat(DEV-0X): Task X.X.X — <short description>"
4. Update docs/DEV-PROGRESS.md: mark task [x]
5. git add docs/DEV-PROGRESS.md
6. git commit -m "chore: progress Task X.X.X"
7. Move to next task — no confirmation needed
```

Stop only when:
- A hard stop condition is triggered (see Section 6)
- All tasks in the current step are complete

When all tasks in a step are complete, report:
`"Step X.X complete — N tasks done. Session can be closed. Next: /project:devXX-stepY+1"`

---

## 8. Push Flow (Manual Trigger via /project:push-phase)

Triggered only after all non-verification steps in a DEV phase are complete.

```
1. Run: black --check src/ api/ app/ config/
2. Run: flake8 src/ api/ app/ config/
3. If any errors → STOP, report file and line, do not push
4. If clean → show summary:
   - Which DEV phase
   - Number of commits since last push
   - Files changed
5. Ask for explicit confirmation before git push
6. On confirmation: git push origin main
7. Report: "DEV-0X pushed. Ready for manual verification steps."
```

---

## 9. Commit Message Convention

```
feat(DEV-01): Task 1.1.1 — create root-level files
feat(DEV-02): Task 2.1.1 — implement CustomerInput Pydantic schema
fix(DEV-03): Task 3.1.2 — correct selectbox options for MultipleLines
chore: progress Task 2.2.1
ci: add GitHub Actions CI/CD pipeline
docs: add README and CHANGELOG for portfolio
```

Format: `type(scope): Task X.X.X — short description`
Types: `feat` (new implementation), `fix` (correction), `chore` (housekeeping), `ci`, `docs`

---

## 10. DEV-PROGRESS.md Format

`docs/DEV-PROGRESS.md` is the source of truth for current position across sessions.
Always read this file at the start of any session to orient before executing.

```markdown
## DEV-02: FastAPI Service

### Step 1 — Shared Utilities
- [x] Task 1.1.1 — implement get_logger
- [x] Task 1.2.1 — implement save_artifact and load_artifact

### Step 2 — Pydantic Schemas
- [x] Task 2.1.1 — CustomerInput schema
- [ ] Task 2.2.1 — PredictionResult schema   ← RESUME HERE
- [ ] Task 2.2.2 — batch response schemas
- [ ] Task 2.2.3 — HealthResponse schema
```

The hook `post-commit-update-progress.sh` updates this file automatically after each task commit.
If the hook fails, update manually before closing the session.

---

## 11. Key Constants Reference

These are the most frequently referenced constants from `config/settings.py`.
Do not hardcode these values anywhere — always import from settings.

| Constant | Value | Used In |
|---|---|---|
| `RANDOM_SEED` | `42` | All random operations |
| `TARGET_COLUMN` | `"Churn"` | Preprocessing, training |
| `ID_COLUMN` | `"id"` | Ingestion (dropped before training) |
| `CHURN_POSITIVE_LABEL` | `"Yes"` | Target encoding |
| `NO_INTERNET_VALUE` | `"No internet service"` | Structural encoder |
| `NO_PHONE_VALUE` | `"No phone service"` | Structural encoder |
| `EXPECTED_IMPORTANT_FEATURES` | `["Contract", "tenure", "MonthlyCharges", "tc_residual", "InternetService"]` | XAI validator |
| `XAI_TOP_N_FEATURES` | `10` | XAI validator |
| `XAI_MIN_OVERLAP` | `0.5` | XAI gate threshold |
| `MODEL_PATH` | from env or `models/artifacts/model_final.joblib` | api/predictor.py |
| `PREPROCESSOR_PATH` | from env or `models/artifacts/preprocessor.joblib` | api/predictor.py |
| `API_HOST` | from env or `"0.0.0.0"` | api/main.py |
| `API_PORT` | from env or `8000` (int) | api/main.py |
| `API_BASE_URL` | from env or `f"http://{API_HOST}:{API_PORT}"` | app/components/api_client.py |

---

## 12. Known Decisions and Constraints

**model_final.joblib must be prepared manually before DEV-02 verification**
Training produces `tuned_{key}.joblib` files. Before running the API, identify the best model
from `tuning_summary.json` (highest `val_pr_auc`) and copy it to `models/artifacts/model_final.joblib`.

**gender field is accepted but dropped by preprocessor**
`CustomerInput` schema includes `gender` for raw data schema compatibility.
The preprocessor drops it internally. Document this in the schema docstring.

**VotingClassifier requires SHAP surrogate**
`shap.Explainer` does not support VotingClassifier directly.
Use `model.estimators_[0]` as surrogate and log that surrogate is being used.

**TotalCharges is used to compute tc_residual, then dropped**
`TotalCharges` must remain in `CustomerInput` — the preprocessor needs it to derive `tc_residual`.
After feature engineering, `TotalCharges` itself is not passed to the model.

**Docker images bundle model artifacts**
This is a deliberate decision for HF Spaces free tier (no persistent volume mounts).
In production, artifacts would be pulled from WandB registry at container startup.
Document this clearly in DEV-08 README under "Scaling to Production".

**HF Spaces uses port 7860**
Both Dockerfile.api and Dockerfile.ui expose port 7860 (not 8000 or 8501).
Environment variables `API_PORT=7860` and `STREAMLIT_SERVER_PORT=7860` must be set in Dockerfiles.

---

## 13. DEV Instruction Files

Full task instructions for each phase are in:

```
docs/DEV-01_repository_project_setup.md
docs/DEV-02_fastapi_service.md
docs/DEV-03_streamlit_ui.md
docs/DEV-04_testing_suite.md
docs/DEV-05_dockerization.md
docs/DEV-06_huggingface_spaces_setup.md
docs/DEV-07_cicd_pipeline.md
docs/DEV-08_readme_portfolio_documentation.md
```

When executing a step command (e.g. `/project:dev02-step2`), read only the relevant
step section from the DEV file — not the entire file. Use bash to extract the section:

```bash
sed -n '/^## STEP 2/,/^## STEP 3/p' docs/DEV-02_fastapi_service.md
```

This keeps context window usage minimal across sessions.
