# TCCP Deployment — Development Instructions
## DEV-06: Hugging Face Spaces Setup

---

## WHAT THIS PHASE COVERS

DEV-06 menyiapkan dua Hugging Face Spaces secara manual sebagai target deployment: `tccp-api` untuk FastAPI service dan `tccp-ui` untuk Streamlit UI. Phase ini mencakup pembuatan kedua Space, konfigurasi `README.md` HF yang berfungsi sebagai metadata Space, penambahan environment variable di HF Settings, penyusunan struktur repository HF yang dibutuhkan, dan verifikasi manual deploy pertama via git push ke HF remote.

Phase ini dikerjakan sepenuhnya melalui Hugging Face web interface dan command line — tidak ada perubahan kode aplikasi. Output utama phase ini adalah dua URL publik yang aktif dan berfungsi, serta dua HF remote URL yang akan digunakan oleh CI/CD di DEV-07.

DEV-06 bergantung pada DEV-05 (image sudah terbukti bisa berjalan lokal). DEV-06 adalah prasyarat untuk DEV-07 (GitHub Actions CI/CD).

---

## BEFORE YOU START THIS PHASE

Pastikan hal-hal berikut sudah siap sebelum memulai:

- Akun Hugging Face sudah aktif di `huggingface.co`. Jika belum ada, buat akun terlebih dahulu.
- `git` sudah ter-install di mesin lokal dan sudah dikonfigurasi dengan user name dan email.
- `git-lfs` (Git Large File Storage) sudah ter-install. HF Spaces menggunakan git-lfs untuk file besar seperti model artifact. Verifikasi dengan menjalankan `git lfs version` — jika belum ada, install dari `git-lfs.com`.
- Hugging Face CLI sudah ter-install dan sudah login: `pip install huggingface_hub` kemudian `huggingface-cli login`. Masukkan HF token yang bisa dibuat di `huggingface.co/settings/tokens`. Token ini juga harus dicatat untuk digunakan di GitHub Secrets pada DEV-07.

After confirming all prerequisites, confirm with: "Prerequisites verified. Ready to execute DEV-06."
Then wait for user instruction to begin.

---

## EXECUTION RULES FOR THIS PHASE

- Execute one task at a time.
- After completing each task, report what was done and wait for the user to say "next" or give a correction.
- Do not move to the next task unless the user explicitly confirms.
- Kedua Space menggunakan SDK type `docker` — bukan `streamlit` atau `gradio`. Ini yang memungkinkan Dockerfile custom digunakan sebagai entry point.
- Nama Space di HF mengikuti format `{username}/{space-name}`. Pilih nama yang deskriptif dan konsisten: `{username}/tccp-api` dan `{username}/tccp-ui`. Nama ini akan menjadi bagian dari URL publik.
- `README.md` yang ada di repository HF Space bukan dokumentasi biasa — ia mengandung YAML frontmatter yang mengkonfigurasi Space (title, SDK, port, dll). Konten YAML frontmatter ini adalah konfigurasi kritis dan harus diisi dengan tepat.
- Jangan push file `.env` atau token apapun ke repository HF Space. Secret hanya dimasukkan melalui HF Space Settings → Variables and Secrets.

---

## STEP 1 — Persiapan HF Token dan Repository Lokal

### Substep 1.1 — Generate dan Catat HF Token

**Task 1.1.1**
Buka `huggingface.co/settings/tokens` di browser. Buat token baru dengan tipe `write` — token dengan akses write diperlukan agar GitHub Actions bisa push ke HF Space pada DEV-07. Beri nama token yang deskriptif, misalnya `tccp-github-actions`.

Salin nilai token dan simpan di dua tempat: pertama di file `.env` lokal dengan key `HF_TOKEN` (file ini sudah ada di `.gitignore` sehingga tidak akan ter-commit), dan kedua di catatan sementara yang aman karena token ini juga akan dimasukkan ke GitHub Secrets di DEV-07. Token hanya ditampilkan sekali oleh HF — jika hilang, harus di-regenerate.

Report: konfirmasi bahwa token sudah dibuat dan disimpan. Jangan tulis nilai token-nya di sini.

---

### Substep 1.2 — Konfigurasi git-lfs untuk Model Artifacts

**Task 1.2.1**
Di repository lokal project, jalankan `git lfs install` untuk mengaktifkan git-lfs di repository ini jika belum aktif. Kemudian daftarkan file artifact untuk di-track oleh git-lfs: jalankan `git lfs track "models/artifacts/*.joblib"`. Perintah ini akan membuat atau memperbarui file `.gitattributes` di root project dengan entri untuk file `.joblib`.

Verifikasi bahwa `.gitattributes` sekarang berisi baris yang menandai `models/artifacts/*.joblib` sebagai file lfs. Commit perubahan `.gitattributes` ini ke repository GitHub utama. Report output perintah dan konfirmasi commit berhasil.

Catatan penting: git-lfs tracking berlaku untuk repository HF Space, bukan GitHub repository utama. Di GitHub, file artifact dikecualikan via `.gitignore`. Di HF Space repository yang akan dibuat di Step berikutnya, git-lfs akan mengelola artifact secara otomatis berdasarkan `.gitattributes` ini.

---

## STEP 2 — Membuat Space 1: tccp-api

### Substep 2.1 — Buat Space di HF

**Task 2.1.1**
Buka `huggingface.co/new-space` di browser. Isi form pembuatan Space dengan konfigurasi berikut:

`Space name`: `tccp-api`. `License`: pilih `MIT` atau `Apache 2.0` — keduanya sesuai untuk portfolio. `SDK`: pilih `Docker` (bukan Streamlit, bukan Gradio). `Hardware`: pilih `CPU Basic` (free tier). Visibility: pilih `Public` agar bisa diakses tanpa login oleh siapapun yang melihat portfolio.

Klik "Create Space". HF akan membuat repository git baru yang bisa diakses di URL `https://huggingface.co/spaces/{username}/tccp-api`. Repository ini juga memiliki remote git URL: `https://huggingface.co/spaces/{username}/tccp-api`.

Report: URL publik Space yang baru dibuat.

---

### Substep 2.2 — README.md untuk Space 1

**Task 2.2.1**
Buat file `hf_spaces/tccp-api/README.md` di repository lokal project. Folder `hf_spaces/` adalah folder staging — kontennya yang akan dipush ke masing-masing HF Space repository, bukan ke GitHub utama. Tambahkan `hf_spaces/` ke `.gitignore` agar folder ini tidak ikut ter-push ke GitHub.

Isi file ini dengan YAML frontmatter yang wajib dikenali oleh HF Spaces, diikuti dokumentasi singkat:

YAML frontmatter (diapit oleh `---`) harus berisi field berikut: `title` dengan nilai `TCCP Churn Prediction API`, `emoji` dengan nilai emoji yang relevan (misalnya `🔮`), `colorFrom` dan `colorTo` dengan warna pilihan bebas, `sdk` dengan nilai `docker`, `app_port` dengan nilai `7860`, `tags` berupa list yang berisi `fastapi`, `machine-learning`, `churn-prediction`, dan `nlp`.

Di bawah frontmatter, tulis dokumentasi singkat dalam markdown yang menjelaskan: apa yang dilakukan API ini, link ke Space UI (`tccp-ui`), daftar endpoint tersedia (`/health`, `/predict`, `/predict/batch`, `/predict/batch-csv`, `/docs`), dan catatan bahwa ini adalah portfolio project.

---

### Substep 2.3 — Struktur Repository Space 1

**Task 2.3.1**
Di dalam folder `hf_spaces/tccp-api/`, susun struktur file yang akan di-push ke HF Space. File yang diperlukan di repository HF Space adalah: `README.md` (sudah dibuat di Task 2.2.1), `Dockerfile` (bukan `Dockerfile.api` — HF Spaces mencari file bernama `Dockerfile` secara eksplisit), seluruh source code yang dibutuhkan oleh image, dan model artifacts.

Buat file `hf_spaces/tccp-api/Dockerfile` sebagai salinan dari `Dockerfile.api` di root project — isinya identik, hanya namanya yang berubah menjadi `Dockerfile` agar HF Spaces dapat mengenalinya secara otomatis.

Salin juga file dan folder berikut ke `hf_spaces/tccp-api/`: `requirements-base.txt`, `requirements-api.txt`, `config/`, `src/`, `api/`, dan `models/artifacts/` (berisi file `.joblib`).

Jangan salin file yang tidak dibutuhkan: `app/`, `tests/`, `notebooks/`, `data/`, `.env`, `pytest.ini`.

---

### Substep 2.4 — Push ke HF Space 1

**Task 2.4.1**
Inisialisasi repository git di dalam folder `hf_spaces/tccp-api/`. Tambahkan HF Space sebagai remote: `git remote add origin https://huggingface.co/spaces/{username}/tccp-api`. Aktifkan git-lfs di repository ini: `git lfs install`. Track file artifact: `git lfs track "models/artifacts/*.joblib"`. Tambahkan `.gitattributes` ke staging.

Stage semua file, buat commit dengan pesan `"Initial deployment: FastAPI service"`, dan push ke branch `main` dari HF Space: `git push origin main`. Saat diminta credentials, gunakan username HF dan `HF_TOKEN` sebagai password.

Push pertama bisa memakan waktu lama karena file `.joblib` dikirim via git-lfs. Report: estimasi waktu upload dan konfirmasi push berhasil.

---

**Task 2.4.2**
Setelah push selesai, buka halaman Space di `https://huggingface.co/spaces/{username}/tccp-api`. Perhatikan tab "Logs" — HF akan otomatis melakukan `docker build` menggunakan `Dockerfile` yang di-push. Build ini bisa memakan waktu 5–15 menit tergantung ukuran image dan kepadatan server HF.

Pantau log build di tab "Logs". Verifikasi bahwa tidak ada error saat build. Setelah build selesai, Space akan berstatus "Running". Buka URL publik Space dan akses endpoint `/health` — tambahkan `/health` di akhir URL Space. Verifikasi response `status: "healthy"`. Report URL lengkap Space 1 dan response health check.

---

## STEP 3 — Membuat Space 2: tccp-ui

### Substep 3.1 — Buat Space di HF

**Task 3.1.1**
Buka `huggingface.co/new-space` di browser. Isi form dengan konfigurasi berikut:

`Space name`: `tccp-ui`. `License`: sama dengan Space 1. `SDK`: pilih `Docker`. `Hardware`: `CPU Basic` (free tier). Visibility: `Public`.

Klik "Create Space". Report URL publik Space 2.

---

### Substep 3.2 — Set Environment Variable di Space 2

**Task 3.2.1**
Sebelum membuat README dan push source code, set environment variable `API_BASE_URL` terlebih dahulu di Space 2. Ini harus dilakukan sebelum container pertama kali build agar nilai langsung tersedia saat startup.

Buka `https://huggingface.co/spaces/{username}/tccp-ui` → klik tab "Settings" → scroll ke section "Variables and Secrets". Tambahkan variable baru:

`Name`: `API_BASE_URL`. `Value`: URL publik Space 1 dari Task 2.4.2 — formatnya adalah `https://{username}-tccp-api.hf.space`. Perhatikan format URL HF: titik dalam nama Space diganti dengan tanda hubung di subdomain.

Set sebagai `Variable` (bukan `Secret`) karena nilai ini tidak sensitif dan bisa dilihat di logs. Klik "Save". Report konfirmasi bahwa variable sudah tersimpan.

---

### Substep 3.3 — README.md untuk Space 2

**Task 3.3.1**
Buat file `hf_spaces/tccp-ui/README.md`. Isi YAML frontmatter: `title` dengan nilai `TCCP Churn Prediction Dashboard`, `emoji` dengan nilai `📊`, `sdk` dengan nilai `docker`, `app_port` dengan nilai `7860`, `tags` berupa list yang berisi `streamlit`, `machine-learning`, `churn-prediction`, `dashboard`.

Di bawah frontmatter, tulis dokumentasi yang menjelaskan: tujuan dashboard, link ke Space API (`tccp-api`) untuk informasi endpoint, tiga halaman yang tersedia (Single Prediction, Batch Prediction, Analytics), dan cara menggunakan template CSV untuk batch prediction.

---

### Substep 3.4 — Struktur Repository Space 2

**Task 3.4.1**
Di dalam folder `hf_spaces/tccp-ui/`, susun struktur file berikut: `README.md` (sudah dibuat), `Dockerfile` (salinan dari `Dockerfile.ui` di root project — namanya harus `Dockerfile`), `requirements-base.txt`, `requirements-ui.txt`, `config/`, `src/utils/` (hanya subfolder utils, bukan seluruh `src/`), `app/`, `.streamlit/`.

Salin juga `reports/xai_report/` jika direktori tersebut sudah ada dan berisi file. Jika direktori kosong atau belum ada, buat placeholder: buat file `reports/xai_report/.gitkeep` agar direktori ter-track oleh git dan Dockerfile tidak gagal saat mencoba meng-copy ke dalam image.

Jangan salin `models/artifacts/` ke repository Space 2 — UI tidak membutuhkan artifact model karena inference dilakukan oleh Space 1.

---

**Task 3.4.2**
Periksa `Dockerfile` yang di-copy ke `hf_spaces/tccp-ui/`. Pastikan tidak ada instruksi `COPY models/` di dalamnya — jika ada (karena di-copy dari `Dockerfile.ui` yang mungkin berisi instruksi tersebut untuk keperluan lain), hapus instruksi tersebut. UI image tidak membutuhkan artifact model.

Verifikasi juga bahwa `COPY reports/xai_report/ ./reports/xai_report/` ada di Dockerfile — ini yang memungkinkan halaman analytics menampilkan gambar XAI. Jika direktori tersebut kosong (hanya ada `.gitkeep`), instruksi COPY tetap boleh ada — Streamlit akan menampilkan pesan "file not found" yang graceful, bukan crash.

---

### Substep 3.5 — Push ke HF Space 2

**Task 3.5.1**
Inisialisasi repository git di dalam folder `hf_spaces/tccp-ui/`. Tambahkan remote: `git remote add origin https://huggingface.co/spaces/{username}/tccp-ui`. Jalankan `git lfs install` — meskipun UI tidak punya artifact besar, git-lfs tetap diaktifkan untuk konsistensi (HF merekomendasikan ini untuk semua Space).

Stage semua file, buat commit dengan pesan `"Initial deployment: Streamlit UI"`, dan push ke branch `main`. Report konfirmasi push berhasil.

---

**Task 3.5.2**
Pantau log build Space 2 di tab "Logs". Verifikasi build selesai tanpa error. Setelah Space berstatus "Running", buka URL publik Space 2. Verifikasi halaman home Streamlit tampil. Verifikasi sidebar menampilkan status API "🟢 API Connected" dengan model version dari Space 1. Navigasi ke halaman Single Prediction, submit form dengan data dummy, dan verifikasi hasil prediksi muncul.

Report: URL lengkap Space 2, status API yang ditampilkan di sidebar, dan apakah prediksi berhasil dieksekusi.

---

## STEP 4 — Konfigurasi Lanjutan Space 1

### Substep 4.1 — Cold Start Awareness

**Task 4.1.1**
HF Spaces free tier akan "sleep" (mematikan container) jika tidak ada traffic selama beberapa menit. Saat Space di-wake up oleh request pertama, container perlu waktu startup (~30–60 detik untuk load model). Ini akan menyebabkan request pertama timeout dari Streamlit jika timeout-nya terlalu pendek.

Buka `app/components/api_client.py` (hasil DEV-03). Verifikasi bahwa timeout untuk `check_health` adalah 5 detik dan timeout untuk `predict_single` adalah 30 detik. Jika Space sedang sleep, request health check akan gagal dan sidebar akan menampilkan "🔴 API Unreachable" — ini adalah perilaku yang benar dan expected, bukan bug.

Tambahkan komentar di `api_client.py` yang menjelaskan cold start behavior ini. Komentar ini penting untuk portfolio: menunjukkan bahwa kamu aware tentang constraint infrastruktur dan sudah mendokumentasikannya, bukan mengabaikannya.

Jika ada perubahan pada `api_client.py`, commit perubahan ini ke repository GitHub utama (bukan ke `hf_spaces/`). Perubahan di `hf_spaces/` akan di-sync otomatis oleh CI/CD di DEV-07.

---

## STEP 5 — Verifikasi End-to-End di HF

### Substep 5.1 — Test Fungsional Penuh

**Task 5.1.1**
Dengan kedua Space berstatus "Running", jalankan serangkaian test manual berikut secara berurutan. Report hasil setiap test.

Test 1 — Health check Space 1: akses `https://{username}-tccp-api.hf.space/health`. Verifikasi response `status: "healthy"`, `model_loaded: true`, dan `model_version` terisi.

Test 2 — Swagger UI Space 1: akses `https://{username}-tccp-api.hf.space/docs`. Verifikasi semua endpoint tampil di Swagger UI. Gunakan Swagger UI untuk mengirim request ke `POST /predict` dengan data contoh. Verifikasi response berhasil.

Test 3 — Halaman Single Prediction Space 2: buka Space 2, navigasi ke Single Prediction, isi form, klik Submit. Verifikasi hasil prediksi muncul beserta SHAP chart.

Test 4 — Halaman Batch Prediction Space 2: upload CSV template yang sudah diisi dengan beberapa baris, klik Run, verifikasi tabel hasil muncul. Download hasil CSV dan verifikasi konten file.

Test 5 — Halaman Analytics Space 2: navigasi ke Analytics. Verifikasi section Model Status menampilkan model version. Verifikasi gambar XAI tampil jika file ada, atau pesan info yang sesuai jika tidak ada.

---

**Task 5.1.2**
Catat dua URL publik berikut karena akan dibutuhkan di DEV-07 dan DEV-08:

- Space 1 (API): `https://{username}-tccp-api.hf.space`
- Space 2 (UI): `https://{username}-tccp-ui.hf.space`

Catat juga dua URL HF git remote berikut untuk digunakan di GitHub Actions:

- Space 1 git remote: `https://huggingface.co/spaces/{username}/tccp-api`
- Space 2 git remote: `https://huggingface.co/spaces/{username}/tccp-ui`

Simpan keempat URL ini — tulis di file `DEPLOYMENT_URLS.md` di root project (file ini tidak perlu di-commit, hanya sebagai referensi lokal). Report keempat URL tersebut.

---

### Substep 5.2 — Verifikasi Skenario Cold Start

**Task 5.2.1**
Biarkan kedua Space idle selama 5 menit hingga HF mematikan container (Space akan berubah status dari "Running" ke "Sleeping"). Kemudian buka Space 2 di browser.

Amati: sidebar kemungkinan akan menampilkan "🔴 API Unreachable" saat Space 1 sedang wake up. Tunggu 30–60 detik. Kemudian refresh halaman — sidebar seharusnya beralih ke "🟢 API Connected" setelah Space 1 selesai startup.

Verifikasi bahwa aplikasi Streamlit tidak crash atau menampilkan error Python saat Space 1 sedang sleep. Hanya status di sidebar yang berubah — seluruh UI tetap bisa di-navigasi. Report observasi dari skenario ini.

---

## DEV-06 COMPLETE

Setelah Task 5.2.1 selesai dan cold start behavior terkonfirmasi bekerja dengan graceful, DEV-06 selesai.

Informasikan ke user: "DEV-06 complete. Dua HF Spaces aktif dan terverifikasi:
- API: https://{username}-tccp-api.hf.space
- UI: https://{username}-tccp-ui.hf.space

Manual deploy pertama berhasil. Cold start behavior graceful. HF token sudah dicatat untuk digunakan di DEV-07 GitHub Actions secrets. Siap untuk DEV-07 (CI/CD Pipeline)."

---

## RINGKASAN DEV-06

| Step | Substep | Task | Output |
|---|---|---|---|
| Step 1 — Persiapan | 1.1 | 1.1.1 | HF token tersimpan di `.env` lokal |
| | 1.2 | 1.2.1 | `.gitattributes` dikonfigurasi untuk git-lfs |
| Step 2 — Space 1 (API) | 2.1 | 2.1.1 | Space `tccp-api` dibuat di HF |
| | 2.2 | 2.2.1 | `hf_spaces/tccp-api/README.md` |
| | 2.3 | 2.3.1 | Struktur `hf_spaces/tccp-api/` lengkap |
| | 2.4 | 2.4.1, 2.4.2 | Push berhasil, Space berstatus Running |
| Step 3 — Space 2 (UI) | 3.1 | 3.1.1 | Space `tccp-ui` dibuat di HF |
| | 3.2 | 3.2.1 | `API_BASE_URL` di-set di HF Settings |
| | 3.3 | 3.3.1 | `hf_spaces/tccp-ui/README.md` |
| | 3.4 | 3.4.1, 3.4.2 | Struktur `hf_spaces/tccp-ui/` lengkap |
| | 3.5 | 3.5.1, 3.5.2 | Push berhasil, Space berstatus Running |
| Step 4 — Konfigurasi | 4.1 | 4.1.1 | Cold start didokumentasikan di kode |
| Step 5 — Verifikasi | 5.1 | 5.1.1, 5.1.2 | 5 test manual lulus, URL dicatat |
| | 5.2 | 5.2.1 | Cold start behavior terkonfirmasi graceful |
| **Total** | **14 substep** | **17 task** | **2 HF Spaces aktif** |
