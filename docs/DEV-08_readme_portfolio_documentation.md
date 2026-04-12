# TCCP Deployment — Development Instructions
## DEV-08: README & Portfolio Documentation

---

## WHAT THIS PHASE COVERS

DEV-08 mengimplementasikan seluruh dokumentasi yang menghadap publik: `README.md` utama di root project sebagai pintu masuk pertama bagi siapapun yang membuka repository, dan `CHANGELOG.md` sebagai bukti project management yang terstruktur. Phase ini tidak mengubah kode apapun — seluruh pekerjaan adalah menulis dokumentasi berkualitas tinggi yang secara aktif mendemonstrasi empat aspek portofolio yang menjadi tujuan project ini.

README yang baik untuk portfolio ML bukan sekadar panduan instalasi. Ia harus menjawab pertanyaan yang ada di kepala interviewer sebelum mereka sempat bertanya: *Mengapa keputusan ini dibuat? Apa trade-off-nya? Bagaimana ini berjalan di production nyata?* Section paling kritis adalah "Scaling to Production" — di sinilah kamu menunjukkan bahwa pilihan infrastruktur saat ini adalah keputusan sadar berdasarkan constraint, bukan keterbatasan pengetahuan.

DEV-08 adalah phase terakhir dan bergantung pada semua phase sebelumnya sudah selesai, karena README mereferensikan URL publik (HF Spaces), badge CI (GitHub Actions), dan mendeskripsikan komponen yang sudah diimplementasikan.

---

## BEFORE YOU START THIS PHASE

Siapkan informasi berikut sebelum mulai menulis — semuanya dibutuhkan untuk mengisi konten yang konkret:

- URL publik Space 1 (API): `https://{username}-tccp-api.hf.space` dari DEV-06
- URL publik Space 2 (UI): `https://{username}-tccp-ui.hf.space` dari DEV-06
- URL repository GitHub project
- Nilai metric evaluasi model final: minimal nilai PR-AUC, ROC-AUC, F1, Precision, Recall dari `reports/evaluation_report.md`
- Nama model final yang terpilih (LightGBM, XGBoost, atau Voting Ensemble) beserta top-3 SHAP features-nya
- Status CI badge URL: format `https://github.com/{username}/{repo}/actions/workflows/ci-cd.yml/badge.svg`

After confirming all information is available, confirm with: "All information ready. Ready to execute DEV-08."
Then wait for user instruction to begin.

---

## EXECUTION RULES FOR THIS PHASE

- Execute one task at a time.
- After completing each task, report what was done and wait for the user to say "next" or give a correction.
- Do not move to the next task unless the user explicitly confirms.
- Semua path file relatif terhadap root project.
- README ditulis dalam bahasa Inggris karena portfolio ini ditujukan untuk audiens yang lebih luas.
- Setiap klaim dalam README harus bisa diverifikasi — jangan tulis angka metric yang belum ada, jangan klaim fitur yang belum diimplementasikan.
- Section "Scaling to Production" harus ditulis dengan nada yang menunjukkan awareness, bukan apologi. Framing yang benar: "Saat ini menggunakan X karena constraint Y — di production, solusinya adalah Z" — bukan "Sayangnya tidak bisa menggunakan Z karena keterbatasan."
- Jangan salin konten dari `churn-doc1-project-overview.md` secara mentah ke README. README adalah dokumen yang berbeda untuk audiens yang berbeda — lebih ringkas, lebih visual, lebih langsung ke intinya.

---

## STEP 1 — Badges dan Header README

### Substep 1.1 — Badges

**Task 1.1.1**
Buka `README.md` di root project. Bagian paling atas README (sebelum judul) harus berisi deretan badge yang memberikan snapshot status project secara visual. Tulis badge-badge berikut menggunakan format markdown standard:

Badge CI/CD status dari GitHub Actions: menggunakan URL format `https://github.com/{username}/{repo}/actions/workflows/ci-cd.yml/badge.svg` dengan link ke halaman Actions.

Badge Python version: menggunakan shields.io dengan label `Python` dan nilai `3.11`.

Badge dua HF Space: satu badge untuk Space API dengan label `API Space` dan link ke Space 1, satu badge untuk Space UI dengan label `UI Space` dan link ke Space 2.

Badge license: sesuai license yang dipilih saat membuat HF Space di DEV-06.

Letakkan semua badge dalam satu baris, rata tengah menggunakan `<div align="center">` agar tampil rapi di GitHub.

---

### Substep 1.2 — Judul dan Tagline

**Task 1.2.1**
Masih di `README.md`. Setelah badges, tulis judul dan tagline:

Judul H1: `Customer Churn Prediction (TCCP)`.

Di bawah judul, tulis dua kalimat tagline yang langsung menyebutkan apa yang dilakukan project ini dan apa yang membuatnya berbeda dari project churn prediction biasa. Poin diferensiasi project ini adalah: XAI digunakan sebagai quality gate (bukan hanya interpretasi di akhir), dan pipeline bersifat end-to-end dari EDA hingga deployed API dengan CI/CD. Kedua poin ini harus ada di tagline.

Setelah tagline, tambahkan dua baris link navigasi singkat yang langsung mengarah ke dua live demo: **Live API** (link ke Swagger UI Space 1) dan **Live Dashboard** (link ke Space 2). Format link ini sebagai tombol atau link yang menonjol — gunakan syntax `[🔮 Try the API →](url)` dan `[📊 Open Dashboard →](url)`.

---

## STEP 2 — Project Overview

### Substep 2.1 — What This Project Demonstrates

**Task 2.1.1**
Masih di `README.md`. Buat section `## What This Project Demonstrates` segera setelah header. Section ini adalah yang pertama dibaca interviewer — harus langsung menjawab "mengapa project ini layak diperhatikan."

Tulis empat bullet point, masing-masing satu paragraf pendek. Setiap bullet menjawab satu dari empat aspek portofolio yang ingin ditunjukkan:

**ML Lifecycle** — jelaskan bahwa project ini mengikuti lifecycle ML yang lengkap dan rigorous: EDA 7 fase yang menghasilkan keputusan terukur (bukan hanya eksplorasi), XAI quality gate yang memvalidasi bahwa model belajar dari fitur yang secara bisnis masuk akal sebelum dilanjutkan ke tuning, hyperparameter tuning dengan Optuna, dan final evaluation yang membandingkan base model vs final model.

**Production-Ready Serving** — jelaskan bahwa model di-serve via FastAPI dengan Pydantic validation, SHAP local explanation per prediksi, batch prediction via JSON dan CSV upload, structured logging, health check endpoint, dan training-serving parity yang dijamin melalui `preprocessor.joblib`.

**Containerization & Deployment** — jelaskan bahwa setiap service berjalan dalam Docker container terpisah (microservice separation), di-deploy ke Hugging Face Spaces dengan arsitektur dua-Space yang mencerminkan API/UI decoupling yang umum di production.

**CI/CD Automation** — jelaskan bahwa setiap push ke `main` memicu pipeline GitHub Actions yang menjalankan linting, testing dengan coverage report, Docker build verification, dan automated deploy ke kedua HF Spaces — tanpa manual intervention.

---

### Substep 2.2 — Problem Statement

**Task 2.2.1**
Masih di `README.md`. Buat section `## Problem Statement` yang singkat dan tajam — maksimal empat kalimat.

Jelaskan konteks bisnis: customer churn di industri telekomunikasi berarti kehilangan recurring revenue yang sudah ada, dan cost akuisisi pelanggan baru jauh lebih tinggi dari cost retensi. Dataset adalah synthetic telco data dari Kaggle Playground Series S6E3 dengan ~26% churn rate (class imbalance moderat).

Jelaskan keputusan pemilihan model: model dipilih setelah EDA selesai, bukan sebelumnya. EDA menunjukkan bahwa data memiliki structural dependency (nilai "No internet service" dan "No phone service" bukan missing value), engineered features seperti `tc_residual` dan `monthly_to_total_ratio` yang divalidasi oleh SHAP, dan karakteristik tabular yang sesuai dengan gradient boosting.

Jelaskan metric utama yang diprioritaskan: PR-AUC diprioritaskan di atas ROC-AUC karena class imbalance, dan recall Churn=Yes diprioritaskan karena false negative (pelanggan yang akan churn tapi tidak terdeteksi) lebih mahal dari false positive.

---

## STEP 3 — Architecture Section

### Substep 3.1 — ML Pipeline Architecture

**Task 3.1.1**
Masih di `README.md`. Buat section `## ML Pipeline` dengan dua sub-section.

Sub-section pertama `### Training Pipeline` mendeskripsikan alur training menggunakan diagram ASCII yang ringkas — bukan salinan diagram panjang dari Dokumen 1. Cukup tampilkan stage-stage utama dengan penanda XAI gate yang jelas:

```
EDA (7 phases) → Preprocessing + Feature Engineering → Base Model Training
    → XAI Gate #1 (SHAP/LIME/Permutation) → [PASS] → Hyperparameter Tuning (Optuna)
    → XAI Gate #2 → [PASS] → Final Evaluation → Model Registry (WandB)
```

Di bawah diagram, tulis satu paragraf yang menjelaskan prinsip XAI sebagai quality gate: model yang metric-nya bagus tapi top SHAP features-nya tidak konsisten dengan domain knowledge churn akan ditolak dan dikembalikan ke tahap sebelumnya. Sebutkan `EXPECTED_IMPORTANT_FEATURES` dan threshold `XAI_MIN_OVERLAP = 0.5` secara eksplisit sebagai bukti bahwa ini bukan keputusan subjektif.

Sub-section kedua `### Inference Pipeline` mendeskripsikan alur inference dengan diagram singkat:

```
JSON Input → Pydantic Validation → preprocessor.joblib (transform only)
    → model_final.joblib → Probability Score + SHAP Values → JSON Response
```

Sertakan catatan eksplisit bahwa `preprocessor.joblib` selalu di-load — tidak ada preprocessing yang ditulis ulang di inference code. Ini adalah training-serving parity guarantee.

---

### Substep 3.2 — Deployment Architecture

**Task 3.2.1**
Masih di `README.md`. Buat section `## Deployment Architecture` yang menjelaskan arsitektur dua-Space.

Tampilkan diagram ASCII yang menunjukkan alur dari GitHub push hingga ke end user:

```
GitHub (push to main)
    → GitHub Actions: lint → test → build (smoke test) → deploy
        ├── HF Space 1 (tccp-api): FastAPI + Docker → port 7860
        │       └── /predict, /predict/batch, /predict/batch-csv, /health, /docs
        └── HF Space 2 (tccp-ui): Streamlit + Docker → port 7860
                └── consumes Space 1 via API_BASE_URL (HTTP)
                        └── Browser (end user)
```

Di bawah diagram, buat tabel dua kolom yang mendeskripsikan masing-masing Space: nama Space, URL publik, teknologi, port internal, dan apa yang di-expose ke user.

Tambahkan catatan tentang cold start: HF Spaces free tier akan sleep setelah inaktif. Request pertama setelah sleep membutuhkan ~30-60 detik startup. Streamlit UI menangani ini dengan graceful — menampilkan status "API Unreachable" saat Space 1 sedang wake up, dan kembali ke "Connected" setelah startup selesai. Framing ini penting: tunjukkan bahwa kamu aware dan sudah handle kondisi ini, bukan mengabaikannya.

---

## STEP 4 — Model Performance Section

### Substep 4.1 — Results

**Task 4.1.1**
Masih di `README.md`. Buat section `## Model Performance` yang menampilkan hasil evaluasi final secara konkret. Isi bagian ini dengan angka aktual dari `reports/evaluation_report.md` — jangan gunakan placeholder.

Tampilkan tabel yang membandingkan base model vs final model untuk metric utama: PR-AUC, ROC-AUC, F1 (threshold 0.5), Precision, Recall, dan metric lain yang tersedia. Kolom pertama adalah nama metric, kolom kedua nilai base model, kolom ketiga nilai final model, kolom keempat delta (selisih).

Di bawah tabel, tulis satu paragraf yang menyebutkan: nama model final yang terpilih, tiga SHAP features terpenting, dan penjelasan singkat mengapa peningkatan dari base ke final model terjadi (hasil XAI treatment dan tuning, bukan keberuntungan).

Jika delta kolom menunjukkan peningkatan yang signifikan, highlight dengan kalimat: ini membuktikan bahwa XAI treatment menghasilkan peningkatan nyata, bukan hanya overhead proses.

---

## STEP 5 — Quick Start Section

### Substep 5.1 — Prerequisites dan Setup Lokal

**Task 5.1.1**
Masih di `README.md`. Buat section `## Quick Start` dengan tiga sub-section yang jelas terpisah.

Sub-section `### Prerequisites` menyebutkan: Python 3.11+, Docker Desktop (opsional tapi direkomendasikan), `git-lfs`, dan akun WandB (hanya untuk training ulang — tidak diperlukan untuk menjalankan aplikasi).

Sub-section `### Option A: Run Locally (without Docker)` berisi langkah-langkah berurutan yang ringkas:

Langkah 1: Clone repository dan masuk ke direktori project.

Langkah 2: Buat virtual environment dan aktifkan: `python -m venv .venv` lalu aktivasi sesuai OS.

Langkah 3: Install dependencies: `pip install -r requirements.txt`.

Langkah 4: Salin `.env.example` menjadi `.env` dan isi nilai yang diperlukan — minimal tidak perlu mengisi apapun untuk menjalankan API dan UI secara lokal.

Langkah 5: Jalankan FastAPI: `uvicorn api.main:app --reload --port 8000`. Akses Swagger UI di `http://localhost:8000/docs`.

Langkah 6: Di terminal terpisah, jalankan Streamlit: `streamlit run app/main.py`. Akses di `http://localhost:8501`. Pastikan `API_BASE_URL` di `.env` menunjuk ke `http://localhost:8000`.

---

**Task 5.1.2**
Masih di sub-section Quick Start. Tambahkan sub-section `### Option B: Run with Docker`.

Langkah 1: Build kedua image: `docker build -f Dockerfile.api -t tccp-api .` dan `docker build -f Dockerfile.ui -t tccp-ui .`.

Langkah 2: Buat Docker network: `docker network create tccp-network`.

Langkah 3: Jalankan API container: `docker run -d --network tccp-network --name tccp-api -p 7860:7860 tccp-api`.

Langkah 4: Jalankan UI container: `docker run -d --network tccp-network --name tccp-ui -p 8501:7860 -e API_BASE_URL=http://tccp-api:7860 tccp-ui`.

Langkah 5: Akses UI di `http://localhost:8501` dan API docs di `http://localhost:7860/docs`.

Sertakan perintah cleanup di akhir sub-section: `docker stop tccp-api tccp-ui && docker rm tccp-api tccp-ui && docker network rm tccp-network`.

---

## STEP 6 — API Reference Section

### Substep 6.1 — Endpoint Documentation

**Task 6.1.1**
Masih di `README.md`. Buat section `## API Reference` yang mendeskripsikan setiap endpoint secara ringkas. Format sebagai tabel dengan kolom: Method, Endpoint, Description, Response.

Endpoint yang harus ada dalam tabel: `GET /`, `GET /health`, `POST /predict`, `POST /predict/batch`, `POST /predict/batch-csv`, `GET /docs`.

Di bawah tabel, tambahkan contoh request dan response untuk `POST /predict` menggunakan markdown code block dengan label `json`. Request adalah contoh customer data yang valid (profil berisiko tinggi: month-to-month, fiber optic, tenure pendek). Response menunjukkan `churn_probability`, `risk_level`, dan beberapa entry `shap_values`. Nilai-nilai ini tidak perlu dari prediksi nyata — bisa representatif — tapi harus format yang konsisten dengan `PredictionResponse` schema.

---

## STEP 7 — Scaling to Production Section

### Substep 7.1 — Current Constraints dan Production Path

**Task 7.1.1**
Masih di `README.md`. Buat section `## Scaling to Production`. Ini adalah section yang paling menentukan kesan interviewer tentang production awareness. Tulis dengan nada engineering yang mature: akui constraint saat ini, jelaskan alasannya, dan berikan jalur konkret menuju arsitektur production yang lebih proper.

Buat sub-section `### Current Architecture (Portfolio Deployment)` yang menjelaskan trade-off yang sudah dibuat secara sadar:

**Model artifact bundling**: artifact di-bundle ke dalam Docker image untuk kemudahan deployment ke HF free tier yang tidak mendukung persistent storage. Di production, artifact harus di-pull dari model registry (WandB atau MLflow) saat container startup, sehingga image bisa di-reuse untuk berbagai versi model tanpa rebuild.

**Single worker**: uvicorn berjalan dengan `--workers 1` karena memory constraint HF free tier. Di production, gunakan multiple workers (atau Gunicorn sebagai process manager) dengan horizontal pod autoscaling di Kubernetes berdasarkan CPU/memory utilization.

**No model monitoring**: tidak ada mekanisme untuk mendeteksi data drift atau prediction distribution shift. Di production, setiap request di-log ke data warehouse, dan pipeline monitoring (misal Evidently AI atau WhyLabs) menjalankan drift detection secara periodik — alert jika distribusi input bergeser dari training distribution.

**Cold start latency**: HF free tier mematikan container setelah idle. Di production (AWS ECS, GCP Cloud Run, atau on-prem Kubernetes), minimum replicas dijaga agar tidak ada cold start, dan health check endpoint digunakan oleh load balancer untuk routing.

**No automated retraining**: retraining dilakukan manual. Di production, drift detection yang terdeteksi men-trigger retraining pipeline otomatis, model baru divalidasi via XAI gate yang sama, dan di-deploy hanya jika metricnya meningkat — semua terotomasi via Airflow atau Prefect.

---

**Task 7.1.2**
Masih di section `## Scaling to Production`. Tambahkan sub-section `### Production Target Architecture` yang mendeskripsikan arsitektur target jika project ini dipindahkan ke enterprise environment.

Tulis dalam format ringkas — bukan prose panjang, tapi cukup detail untuk menunjukkan bahwa kamu memahami landscape tooling:

**Serving**: Replace HF Spaces dengan container orchestration — AWS ECS Fargate atau GCP Cloud Run untuk serverless, atau Kubernetes untuk full control. Load balancer di depan multiple API replicas.

**Model Registry**: WandB sudah digunakan untuk experiment tracking. Di production, tambahkan version tagging yang lebih formal dan model approval workflow sebelum model bisa di-promote ke production.

**Data & Feature Store**: untuk dataset yang lebih besar atau high-frequency prediction, pertimbangkan feature store (Feast atau Tecton) untuk serving pre-computed features, mengurangi latency dan menghindari train-serve skew.

**Monitoring**: Evidently AI atau WhyLabs untuk data drift detection. Prometheus + Grafana untuk API latency, error rate, dan throughput monitoring. Alert ke PagerDuty atau Slack jika metric melewati threshold.

**Retraining pipeline**: Airflow DAG atau GitHub Actions scheduled workflow yang menjalankan seluruh training pipeline — dari data ingestion hingga model validation via XAI gate — dan auto-deploy jika model baru lulus semua kriteria.

---

## STEP 8 — Repository Structure dan CHANGELOG

### Substep 8.1 — Repository Structure

**Task 8.1.1**
Masih di `README.md`. Buat section `## Repository Structure` yang menampilkan struktur folder project menggunakan tree format. Struktur ini harus menampilkan dua level pertama saja dengan komentar singkat di setiap folder menjelaskan perannya. Jangan tampilkan semua file individual — cukup folder dan file-file paling signifikan.

Setelah tree, tambahkan satu catatan yang menegaskan perbedaan antara `notebooks/` (eksplorasi) dan `src/` (production code): tidak ada kode production yang diimport dari notebook, dan seluruh logic yang sudah matang sudah di-refactor ke `src/`.

---

### Substep 8.2 — CI/CD Pipeline Overview di README

**Task 8.2.1**
Masih di `README.md`. Buat section `## CI/CD Pipeline` yang ringkas. Tampilkan diagram ASCII alur pipeline:

```
push to main
    → [lint] flake8 + black + isort
        → [test] pytest unit + integration + coverage report
            → [build] docker build (API + UI) + smoke test
                → [deploy] git push to HF Space 1 + HF Space 2
                    → [notify] pipeline summary to GitHub Actions UI

pull_request to main
    → [lint] + [test] only (no deploy)
```

Di bawah diagram, tambahkan catatan: setiap job hanya berjalan jika job sebelumnya lulus. Perubahan pada file markdown dan notebook tidak memicu pipeline (`paths-ignore`). Pipeline bisa dipicu secara manual via `workflow_dispatch`.

---

### Substep 8.3 — CHANGELOG.md

**Task 8.3.1**
Buat file `CHANGELOG.md` di root project. File ini mengikuti format Keep a Changelog (keepachangelog.com) yang merupakan standar yang diakui secara luas.

Baris pertama adalah link ke standar Keep a Changelog dan Semantic Versioning. Kemudian tulis entry untuk setiap milestone besar project sebagai versi:

`[1.0.0] - {tanggal deployment pertama ke HF}` — tulis under subsection `Added`: initial deployment kedua HF Spaces, GitHub Actions CI/CD pipeline, FastAPI dengan semua endpoint, Streamlit UI dengan tiga halaman, Docker containerization, automated testing suite.

`[0.5.0] - {tanggal Notebook 05 selesai}` — tulis under `Added`: hyperparameter tuning dengan Optuna (Jalur 1, 100 trials), Voting Ensemble dari top-3 model, XAI Gate #2 untuk semua kandidat post-tuning.

`[0.4.0] - {tanggal Notebook 04 selesai}` — tulis under `Added`: XAI analysis untuk 6 kandidat model (SHAP, LIME, Permutation Importance), XAI Gate #1 dengan kriteria formal (XAI_MIN_OVERLAP = 0.5), keputusan eksklusi Random Forest (recall di bawah threshold).

`[0.3.0] - {tanggal EDA selesai}` — tulis under `Added`: EDA 7 fase (598 baris kode analisis), custom encoder untuk structural dependency, feature engineering 5 fitur baru yang divalidasi SHAP, keputusan arsitektur model berbasis EDA.

`[0.1.0] - {tanggal project dimulai}` — tulis under `Added`: inisialisasi project structure, Dokumen 1 (Project & Data Overview), dataset schema definition.

---

## STEP 9 — Verifikasi README

### Substep 9.1 — Review Konten

**Task 9.1.1**
Baca seluruh README dari atas ke bawah sebagai seorang interviewer yang baru pertama kali melihat repository ini. Verifikasi hal-hal berikut dan report hasilnya:

Apakah dua live demo links (API dan Dashboard) berfungsi dan mengarah ke halaman yang benar? Klik keduanya dan verifikasi.

Apakah badge CI menampilkan status yang benar (passing/failing sesuai kondisi aktual pipeline)?

Apakah angka metric di section Model Performance konsisten dengan apa yang ada di `reports/evaluation_report.md`?

Apakah perintah-perintah di Quick Start bisa dieksekusi tanpa error? Jalankan minimal Option A (tanpa Docker) dari awal hingga aplikasi bisa diakses di browser.

Apakah section "Scaling to Production" terasa seperti ditulis oleh seseorang yang memahami production ML, atau terasa seperti daftar kata kunci tanpa substansi? Ini adalah penilaian subjektif — baca ulang dan revisi jika perlu.

---

**Task 9.1.2**
Verifikasi bahwa README dapat di-render dengan benar di GitHub. Buka URL repository GitHub di browser. Verifikasi bahwa badges tampil (bukan broken image). Verifikasi bahwa semua code blocks memiliki syntax highlighting yang benar. Verifikasi bahwa semua link internal (anchor links ke section) berfungsi. Verifikasi bahwa diagram ASCII tidak rusak karena perbedaan font rendering.

Report temuan dan perbaiki yang perlu sebelum melanjutkan.

---

### Substep 9.2 — Final Commit

**Task 9.2.1**
Commit semua file dokumentasi yang dibuat di phase ini: `README.md` dan `CHANGELOG.md`. Gunakan commit message: `"docs: add README and CHANGELOG for portfolio"`

Push ke `main`. Verifikasi bahwa push ini tidak memicu pipeline CI/CD karena `README.md` dan `CHANGELOG.md` masuk dalam `paths-ignore` di workflow YAML. Jika pipeline tetap terpicu, periksa konfigurasi `paths-ignore` di `ci-cd.yml` dan tambahkan `CHANGELOG.md` jika belum ada.

Report: konfirmasi file berhasil di-push dan pipeline tidak terpicu secara tidak perlu.

---

## DEV-08 COMPLETE

Setelah Task 9.2.1 selesai dan README terkonfirmasi tampil dengan benar di GitHub, DEV-08 selesai.

Informasikan ke user: "DEV-08 complete. README dan CHANGELOG sudah live di repository GitHub. Seluruh 8 phase DEV-01 hingga DEV-08 selesai.

Ringkasan deliverable yang sudah selesai:
- Repository GitHub dengan struktur lengkap dan CI/CD aktif
- FastAPI service live di: https://{username}-tccp-api.hf.space
- Streamlit UI live di: https://{username}-tccp-ui.hf.space
- Pipeline CI/CD: lint → test → build → deploy otomatis pada setiap push ke main
- README yang mendemonstrasikan ML lifecycle, deployment architecture, CI/CD, dan production awareness
- CHANGELOG yang menunjukkan project management terstruktur"

---

## RINGKASAN DEV-08

| Step | Substep | Task | Output |
|---|---|---|---|
| Step 1 — Header | 1.1 | 1.1.1 | Badges di README |
| | 1.2 | 1.2.1 | Judul, tagline, live demo links |
| Step 2 — Overview | 2.1 | 2.1.1 | Section "What This Demonstrates" (4 aspek) |
| | 2.2 | 2.2.1 | Section "Problem Statement" |
| Step 3 — Architecture | 3.1 | 3.1.1 | Section "ML Pipeline" dengan diagram |
| | 3.2 | 3.2.1 | Section "Deployment Architecture" dengan diagram |
| Step 4 — Performance | 4.1 | 4.1.1 | Section "Model Performance" dengan angka aktual |
| Step 5 — Quick Start | 5.1 | 5.1.1, 5.1.2 | Section "Quick Start" — lokal dan Docker |
| Step 6 — API Ref | 6.1 | 6.1.1 | Section "API Reference" — tabel + contoh |
| Step 7 — Production | 7.1 | 7.1.1, 7.1.2 | Section "Scaling to Production" — current + target |
| Step 8 — Structure | 8.1 | 8.1.1 | Section "Repository Structure" |
| | 8.2 | 8.2.1 | Section "CI/CD Pipeline Overview" |
| | 8.3 | 8.3.1 | `CHANGELOG.md` — 5 versi milestone |
| Step 9 — Verifikasi | 9.1 | 9.1.1, 9.1.2 | Content review + GitHub rendering |
| | 9.2 | 9.2.1 | Final commit dan push |
| **Total** | **15 substep** | **17 task** | **2 file** |
