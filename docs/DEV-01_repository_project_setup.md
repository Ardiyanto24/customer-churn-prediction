# TCCP Deployment — Development Instructions
## DEV-01: Repository & Project Setup

---

## WHAT THIS PHASE COVERS

DEV-01 membangun seluruh fondasi repository untuk tahap deployment: inisialisasi struktur folder, pemisahan requirements berdasarkan konteks penggunaan, konfigurasi `.gitignore`, template environment variable, dan implementasi `config/settings.py` sebagai sumber kebenaran tunggal untuk semua konstanta global.

Tidak ada logika ML, API, maupun UI di phase ini. Seluruh pekerjaan adalah konfigurasi dan deklarasi konstanta.

DEV-01 adalah prasyarat untuk seluruh phase berikutnya (DEV-02 hingga DEV-08). Jangan mulai phase lain sebelum DEV-01 selesai dan terverifikasi.

---

## BEFORE YOU START THIS PHASE

Baca file berikut secara penuh sebelum mengeksekusi task apapun di phase ini. Jangan eksekusi task apapun sebelum mengkonfirmasi bahwa kamu sudah membacanya.

**Required reading:**
- `churn-doc1-project-overview.md` — Section 4 (Tech Stack): catat seluruh library beserta versi minimalnya. Section 5 (Struktur Folder): ini adalah sumber kebenaran untuk semua folder dan file yang harus dibuat. Section 9 (Configuration Reference): catat seluruh environment variable dan konstanta global beserta tipe dan nilai defaultnya.

After reading, confirm with: "Reference files read. Ready to execute DEV-01."
Then wait for user instruction to begin.

---

## EXECUTION RULES FOR THIS PHASE

- Execute one task at a time.
- After completing each task, report what was done and wait for the user to say "next" or give a correction.
- Do not move to the next task unless the user explicitly confirms.
- Semua path file relatif terhadap root project `customer-churn-prediction/`.
- Jangan modifikasi file apapun yang sudah ada di `notebooks/` maupun `src/` — scope DEV-01 hanya menyentuh file-file konfigurasi dan struktur folder.
- `data/raw/` adalah immutable — tidak ada kode maupun script yang boleh memodifikasi isinya. Ini harus tercermin di `.gitignore`.

---

## STEP 1 — Inisialisasi Struktur Folder

### Substep 1.1 — Root-level Files

**Task 1.1.1**
Buat file kosong berikut di root project jika belum ada: `README.md`, `.gitignore`, `.env`, `.env.example`. Keempat file ini dibuat kosong terlebih dahulu — kontennya diisi di task-task berikutnya. Jangan isi konten apapun pada task ini.

---

**Task 1.1.2**
Buat folder `config/` di root project. Di dalamnya buat file `__init__.py` kosong dan file `settings.py` kosong. `settings.py` akan diisi di Step 3.

---

### Substep 1.2 — Folder Data

**Task 1.2.1**
Buat struktur folder `data/` berikut jika belum ada: `data/raw/`, `data/processed/`, `data/splits/`. Di dalam setiap subfolder tersebut, buat file `.gitkeep` kosong agar folder ter-track oleh Git meskipun belum ada data di dalamnya. File data aktual (`train.csv`, `test.csv`, dan output split) tidak di-commit ke repository — ini akan dikonfigurasi di `.gitignore` pada Step 2.

---

### Substep 1.3 — Folder Models dan Reports

**Task 1.3.1**
Buat struktur folder `models/artifacts/` jika belum ada. Buat file `.gitkeep` di dalam `models/artifacts/`.Folder ini akan menyimpan `preprocessor.joblib`, `base_model.joblib`, dan `model_final`.joblib. Catatan: training menghasilkan `tuned_{key}.joblib` per model dan `tuned_voting_ensemble`.joblib. Sebelum deployment, pilih model terbaik berdasarkan tuning_summary.json, kemudian copy file tersebut ke models/artifacts/model_final.joblib sebagai artifact deployment. joblib` — ketiganya tidak di-commit ke repository karena ukurannya besar, dan akan dikonfigurasi di `.gitignore`.

---

**Task 1.3.2**
Buat struktur folder `reports/xai_report/` jika belum ada. Buat file `.gitkeep` di `reports/` dan `.gitkeep` di `reports/xai_report/`. Output report seperti `eda_report.html`, PNG plot SHAP, dan `evaluation_report.md` tidak di-commit secara default.

---

### Substep 1.4 — Folder Source Code

**Task 1.4.1**
Buat struktur folder `src/` lengkap berikut jika belum ada. Setiap folder harus memiliki file `__init__.py` kosong:
- `src/`
- `src/data/`
- `src/preprocessing/`
- `src/training/`
- `src/xai/`
- `src/evaluation/`
- `src/utils/`

Selain `__init__.py`, buat juga file Python kosong untuk setiap modul berikut:
- `src/data/ingestion.py`, `src/data/validation.py`
- `src/preprocessing/pipeline.py`, `src/preprocessing/encoders.py`, `src/preprocessing/feature_engineering.py`
- `src/training/trainer.py`, `src/training/tuning.py`, `src/training/experiment.py`
- `src/xai/shap_analysis.py`, `src/xai/lime_analysis.py`, `src/xai/permutation_importance.py`, `src/xai/xai_validator.py`
- `src/evaluation/metrics.py`, `src/evaluation/report.py`
- `src/utils/logger.py`, `src/utils/serialization.py`

File-file ini dibuat kosong. Implementasinya dikerjakan di phase lain.

---

### Substep 1.5 — Folder API dan App

**Task 1.5.1**
Buat struktur folder `api/` berikut jika belum ada. Setiap folder yang relevan memiliki `__init__.py` kosong. Buat juga file Python kosong untuk modul berikut:
- `api/__init__.py`
- `api/main.py`
- `api/schemas.py`
- `api/predictor.py`

File-file ini dibuat kosong. Implementasinya dikerjakan di DEV-02.

---

**Task 1.5.2**
Buat struktur folder `app/` berikut jika belum ada:
- `app/main.py`
- `app/pages/prediction.py`
- `app/pages/batch_prediction.py`
- `app/pages/analytics.py`
- `app/components/` (buat folder dengan `.gitkeep`)

File-file ini dibuat kosong. Implementasinya dikerjakan di DEV-03.

---

### Substep 1.6 — Folder Tests

**Task 1.6.1**
Buat struktur folder `tests/` berikut jika belum ada:
- `tests/__init__.py`
- `tests/unit/__init__.py`
- `tests/unit/test_preprocessing.py`
- `tests/unit/test_metrics.py`
- `tests/unit/test_xai_validator.py`
- `tests/integration/__init__.py`
- `tests/integration/test_api.py`

File test dibuat kosong. Implementasinya dikerjakan di DEV-04.

---

## STEP 2 — `.gitignore` dan `.env.example`

### Substep 2.1 — `.gitignore`

**Task 2.1.1**
Isi file `.gitignore` di root project. File ini harus mengecualikan kategori berikut:

**Environment dan secrets:** file `.env` (bukan `.env.example`), folder `.venv/`, `venv/`, `env/`, `__pycache__/`, `*.pyc`, `*.pyo`, `.python-version`.

**Data:** seluruh isi `data/raw/` kecuali `.gitkeep`, seluruh isi `data/processed/` kecuali `.gitkeep`, seluruh isi `data/splits/` kecuali `.gitkeep`. Pola yang digunakan harus mengecualikan file data (`*.csv`) tetapi tetap men-track folder via `.gitkeep`.

**Model artifacts:** seluruh isi `models/artifacts/` kecuali `.gitkeep`. Pola yang digunakan harus mengecualikan file `*.joblib` dan `*.pkl`.

**Reports:** `reports/eda_report.html`, semua file di `reports/xai_report/` kecuali `.gitkeep`, `reports/*.html`.

**IDE dan OS:** `.DS_Store`, `.idea/`, `.vscode/`, `Thumbs.db`, `*.egg-info/`, `dist/`, `build/`, `.pytest_cache/`, `.mypy_cache/`, `htmlcov/`, `.coverage`.

**WandB:** folder `wandb/` yang di-generate secara lokal saat training.

---

### Substep 2.2 — `.env.example`

**Task 2.2.1**
Isi file `.env.example` di root project. File ini adalah template publik — tidak berisi nilai sensitif, hanya nama variable beserta komentar penjelasannya. Variable yang harus ada:

**WandB:** `WANDB_API_KEY` dengan komentar bahwa nilainya diambil dari wandb.ai/settings, `WANDB_PROJECT` dengan nilai default `customer-churn-prediction`, `WANDB_ENTITY` dengan komentar bahwa ini opsional dan berisi username atau nama team.

**Model paths:** `MODEL_PATH` dengan nilai default `models/artifacts/model_final.joblib`, `PREPROCESSOR_PATH` dengan nilai default `models/artifacts/preprocessor.joblib`.

**API server:** `API_HOST` dengan nilai default `0.0.0.0`, `API_PORT` dengan nilai default `8000`.

**Streamlit (untuk deployment):** `API_BASE_URL` dengan komentar bahwa nilainya adalah URL publik Space 1 di Hugging Face, contoh: `https://username-tccp-api.hf.space`. Variable ini hanya digunakan di environment deployment — tidak diperlukan saat run lokal jika API dan UI dijalankan di mesin yang sama.

Sertakan komentar singkat di bagian atas file yang menyatakan bahwa `.env.example` adalah template dan tidak boleh berisi nilai nyata, serta instruksi untuk menyalin file ini menjadi `.env` dan mengisi nilainya sebelum menjalankan aplikasi.

---

## STEP 3 — `config/settings.py`

### Substep 3.1 — Konstanta Data dan Kolom

**Task 3.1.1**
Buka `config/settings.py`. Tambahkan import yang diperlukan: `os`, `pathlib.Path`, dan `python-dotenv` untuk load environment variable dari file `.env`. Panggil `load_dotenv()` di bagian atas file setelah import agar semua variable di `.env` tersedia via `os.getenv()`.

Tambahkan section konstanta data dengan header komentar yang jelas. Konstanta yang harus ada di section ini:

`TARGET_COLUMN` bernilai `"Churn"` — nama kolom target di dataset. `ID_COLUMN` bernilai `"id"` — kolom identifier yang di-drop sebelum training. `CHURN_POSITIVE_LABEL` bernilai `"Yes"` — nilai positif di kolom target. `CHURN_NEGATIVE_LABEL` bernilai `"No"`.

`NUMERIC_COLS_RAW` berisi list kolom numerik dari raw input: `tenure`, `MonthlyCharges`, `TotalCharges`. `NUMERIC_COLS_PROCESSED` berisi list kolom numerik setelah preprocessing: `tenure`, `MonthlyCharges`, `tc_residual`, `monthly_to_total_ratio`. Gunakan `NUMERIC_COLS_RAW` untuk validasi input API, dan `NUMERIC_COLS_PROCESSED` untuk referensi post-preprocessing seperti XAI dan evaluation.

`CATEGORICAL_COLS` berisi list semua kolom kategorikal non-target: `gender`, `SeniorCitizen`, `Partner`, `Dependents`, `PhoneService`, `MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`, `Contract`, `PaperlessBilling`, `PaymentMethod`. Tambahkan komentar inline setelah gender: # di-drop oleh preprocessor, tidak masuk ke model — diterima API untuk kompatibilitas dengan raw data schema

`ADDON_COLS` berisi list enam kolom add-on internet yang memiliki nilai struktural `"No internet service"`: `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`.

`NO_INTERNET_VALUE` bernilai `"No internet service"`. `NO_PHONE_VALUE` bernilai `"No phone service"`. Kedua nilai ini bukan missing value — mereka adalah nilai struktural yang muncul karena dependency antar kolom.

---

**Task 3.1.2**
Masih di `config/settings.py`. Tambahkan section konstanta split dan reproducibility dengan header komentar yang jelas.

`RANDOM_SEED` bernilai `42` — digunakan di semua operasi random untuk reproducibility. `TEST_SIZE` bernilai `0.15` — proporsi data untuk test set. `VAL_SIZE` bernilai `0.15` — proporsi data untuk validation set, dihitung dari training set setelah test split.

---

### Substep 3.2 — Konstanta XAI Quality Gate

**Task 3.2.1**
Masih di `config/settings.py`. Tambahkan section konstanta XAI dengan header komentar yang menjelaskan bahwa konstanta ini mendefinisikan kriteria quality gate untuk memutuskan apakah sebuah model boleh dilanjutkan ke tahap berikutnya.

`EXPECTED_IMPORTANT_FEATURES` berisi list lima fitur yang diharapkan masuk ke top features berdasarkan domain knowledge churn yang telah divalidasi melalui EDA: `Contract`, `tenure`, `MonthlyCharges`, `tc_residual`, `InternetService`. Sertakan komentar yang menjelaskan bahwa list ini berasal dari hasil EDA Fase 6 (EarlyWarningCompiler) dan merupakan fitur dengan bukti kuantitatif terkuat terhadap churn. # TotalCharges digantikan tc_residual (residual dari expected charges) sebagai hasil feature engineering — ini yang dilihat model dan SHAP

`XAI_TOP_N_FEATURES` bernilai `10` — jumlah top features yang dievaluasi dari SHAP feature importance.

`XAI_MIN_OVERLAP` bernilai `0.5` — ambang batas minimal proporsi `EXPECTED_IMPORTANT_FEATURES` yang harus masuk ke `XAI_TOP_N_FEATURES` agar model dinyatakan lulus quality gate. Dengan 5 expected features dan threshold 0.5, minimal 3 dari 5 harus masuk top-10 SHAP.

---

### Substep 3.3 — Konstanta Path dan Artifact

**Task 3.3.1**
Masih di `config/settings.py`. Tambahkan section konstanta path dengan header komentar yang jelas. Gunakan `pathlib.Path` untuk semua path agar portable di berbagai OS.

`PROJECT_ROOT` didefinisikan sebagai path absolut ke root project, dihitung dari lokasi file `settings.py` itu sendiri (dua level naik dari `config/settings.py`).

`DATA_RAW_DIR` menunjuk ke `data/raw/` relatif terhadap `PROJECT_ROOT`. `DATA_PROCESSED_DIR` menunjuk ke `data/processed/`. `DATA_SPLITS_DIR` menunjuk ke `data/splits/`. `MODELS_DIR` menunjuk ke `models/artifacts/`.

`MODEL_PATH` membaca dari environment variable `MODEL_PATH` via `os.getenv()`. Jika tidak ada, gunakan nilai default `MODELS_DIR / "model_final.joblib"`. `PREPROCESSOR_PATH` membaca dari `os.getenv("PREPROCESSOR_PATH")` dengan default `MODELS_DIR / "preprocessor.joblib"`. `BASE_MODEL_PATH` tidak membaca dari env variable — nilainya selalu `MODELS_DIR / "base_model.joblib"` karena ini path internal yang tidak perlu dikonfigurasi dari luar.

---

### Substep 3.4 — Konstanta WandB dan API

**Task 3.4.1**
Masih di `config/settings.py`. Tambahkan section konstanta WandB artifact dengan header komentar.

`WANDB_PROJECT` membaca dari `os.getenv("WANDB_PROJECT")` dengan default `"customer-churn-prediction"`. `WANDB_ENTITY` membaca dari `os.getenv("WANDB_ENTITY")` tanpa default — boleh `None`.

`MODEL_ARTIFACT_NAME` bernilai `"churn-model"`. `BASE_MODEL_ARTIFACT_NAME` bernilai `"churn-base-model"`. `PREPROCESSOR_ARTIFACT_NAME` bernilai `"churn-preprocessor"`. Ketiga nama ini digunakan secara konsisten di seluruh pipeline training untuk meregistrasi artifact ke WandB.

---

**Task 3.4.2**
Masih di `config/settings.py`. Tambahkan section konstanta API server dengan header komentar.

`API_HOST` membaca dari `os.getenv("API_HOST")` dengan default `"0.0.0.0"`. `API_PORT` membaca dari `os.getenv("API_PORT")` dengan default `8000`. Pastikan `API_PORT` di-cast ke `int` karena `os.getenv()` selalu mengembalikan string.

`API_BASE_URL` membaca dari `os.getenv("API_BASE_URL")` dengan default `f"http://{API_HOST}:{API_PORT}"`. Ketika di-deploy ke Hugging Face, variable ini akan di-override dengan URL publik Space 1 sehingga Streamlit tahu ke mana harus mengirim request.

---

## STEP 4 — Requirements Files

### Substep 4.1 — Base Requirements

**Task 4.1.1**
Buat file `requirements-base.txt` di root project. File ini berisi library yang dibutuhkan oleh komponen ML dan shared utilities — digunakan bersama oleh service API maupun proses training. Isi dengan library berikut beserta versi minimalnya: `scikit-learn>=1.3`, `xgboost>=2.0`, `lightgbm>=4.0`, `pandas>=2.0`, `numpy>=1.26`, `shap>=0.44`, `lime>=0.2`, `optuna>=3.0`, `wandb>=0.16`, `joblib>=1.3`, `python-dotenv>=1.0`, `matplotlib`, `seaborn`.

---

### Substep 4.2 — API Requirements

**Task 4.2.1**
Buat file `requirements-api.txt` di root project. File ini berisi library khusus untuk service FastAPI. Baris pertama harus menyertakan base requirements dengan sintaks `-r requirements-base.txt` agar library ML juga tersedia di service API. Tambahkan library berikut: `fastapi>=0.110`, `uvicorn>=0.27`, `pydantic>=2.0`, `httpx>=0.27`.

---

### Substep 4.3 — UI Requirements

**Task 4.3.1**
Buat file `requirements-ui.txt` di root project. File ini berisi library khusus untuk service Streamlit. Baris pertama harus menyertakan `-r requirements-base.txt`. Tambahkan library berikut: `streamlit>=1.32`, `httpx>=0.27`. Catatan: `shap` sudah masuk via `requirements-base.txt` dan akan digunakan di halaman analytics untuk menampilkan visualisasi SHAP lokal.

---

### Substep 4.4 — Dev Requirements

**Task 4.4.1**
Buat file `requirements-dev.txt` di root project. File ini berisi library yang hanya dibutuhkan saat development dan CI — tidak perlu masuk ke Docker image production. Baris pertama menyertakan `-r requirements-base.txt`. Tambahkan library berikut: `pytest>=8.0`, `pytest-cov`, `flake8`, `black`, `isort`, `httpx>=0.27` (dibutuhkan oleh test client FastAPI), `ydata-profiling>=4.0`.

---

**Task 4.4.2**
Buat file `requirements.txt` di root project sebagai convenience file untuk development lokal. Isinya hanya satu baris: `-r requirements-dev.txt`. Ini memungkinkan developer menjalankan `pip install -r requirements.txt` untuk mendapatkan semua dependency sekaligus termasuk dev tools.

---

## STEP 5 — Verifikasi DEV-01

### Substep 5.1 — Verifikasi Struktur Folder

**Task 5.1.1**
Jalankan perintah tree dari root project untuk menampilkan struktur folder dua level ke bawah. Verifikasi bahwa semua folder berikut ada: `config/`, `data/raw/`, `data/processed/`, `data/splits/`, `models/artifacts/`, `notebooks/`, `reports/xai_report/`, `src/data/`, `src/preprocessing/`, `src/training/`, `src/xai/`, `src/evaluation/`, `src/utils/`, `api/`, `app/pages/`, `app/components/`, `tests/unit/`, `tests/integration/`. Report output tree-nya — jika ada folder yang tidak muncul, laporkan sebelum melanjutkan.

---

### Substep 5.2 — Verifikasi settings.py

**Task 5.2.1**
Jalankan Python interpreter dan import `config.settings`. Verifikasi tidak ada error import. Kemudian cetak nilai dari konstanta berikut dan konfirmasi nilainya sesuai spec: `TARGET_COLUMN`, `EXPECTED_IMPORTANT_FEATURES`, `XAI_MIN_OVERLAP`, `MODEL_PATH`, `API_PORT`, `WANDB_PROJECT`. Report output yang muncul — jika ada error atau nilai yang tidak sesuai, laporkan pesan error lengkapnya sebelum melanjutkan.

---

**Task 5.2.2**
Masih di Python interpreter yang sama. Verifikasi bahwa `API_PORT` bertipe `int` (bukan string) dengan memanggil `type(settings.API_PORT)`. Verifikasi bahwa `MODEL_PATH` dan `PREPROCESSOR_PATH` bertipe `pathlib.Path` dengan memanggil `type(settings.MODEL_PATH)`. Report hasilnya.

---

### Substep 5.3 — Verifikasi Requirements

**Task 5.3.1**
Verifikasi bahwa keempat file requirements ada: `requirements.txt`, `requirements-base.txt`, `requirements-api.txt`, `requirements-ui.txt`, `requirements-dev.txt`. Jalankan `pip install --dry-run -r requirements-dev.txt` untuk memastikan tidak ada dependency conflict yang terdeteksi tanpa benar-benar menginstall apapun. Report hasilnya — jika ada conflict, laporkan sebelum melanjutkan.

---

## DEV-01 COMPLETE

Setelah Task 5.3.1 selesai tanpa error, DEV-01 selesai.

Informasikan ke user: "DEV-01 complete. Struktur folder terbentuk, `config/settings.py` terverifikasi, 5 requirements file siap. Repository siap untuk DEV-02 (FastAPI), DEV-03 (Streamlit UI), dan DEV-04 (Testing Suite) yang bisa dikerjakan secara paralel."

---

## RINGKASAN DEV-01

| Step | Substep | Task | File |
|---|---|---|---|
| Step 1 — Struktur Folder | 1.1 | 1.1.1, 1.1.2 | root files, `config/` |
| | 1.2 | 1.2.1 | `data/` |
| | 1.3 | 1.3.1, 1.3.2 | `models/`, `reports/` |
| | 1.4 | 1.4.1 | `src/` (14 file) |
| | 1.5 | 1.5.1, 1.5.2 | `api/`, `app/` |
| | 1.6 | 1.6.1 | `tests/` |
| Step 2 — Git & Env | 2.1 | 2.1.1 | `.gitignore` |
| | 2.2 | 2.2.1 | `.env.example` |
| Step 3 — Settings | 3.1 | 3.1.1, 3.1.2 | `config/settings.py` |
| | 3.2 | 3.2.1 | `config/settings.py` |
| | 3.3 | 3.3.1 | `config/settings.py` |
| | 3.4 | 3.4.1, 3.4.2 | `config/settings.py` |
| Step 4 — Requirements | 4.1 | 4.1.1 | `requirements-base.txt` |
| | 4.2 | 4.2.1 | `requirements-api.txt` |
| | 4.3 | 4.3.1 | `requirements-ui.txt` |
| | 4.4 | 4.4.1, 4.4.2 | `requirements-dev.txt`, `requirements.txt` |
| Step 5 — Verifikasi | 5.1 | 5.1.1 | — |
| | 5.2 | 5.2.1, 5.2.2 | — |
| | 5.3 | 5.3.1 | — |
| **Total** | **19 substep** | **23 task** | **~40 file** |
