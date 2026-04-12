# TCCP Deployment — Development Instructions
## DEV-07: CI/CD Pipeline (GitHub Actions)

---

## WHAT THIS PHASE COVERS

DEV-07 mengimplementasikan pipeline CI/CD menggunakan GitHub Actions. Satu file workflow `ci-cd.yml` mendefinisikan empat job yang berjalan secara berurutan: `lint`, `test`, `build`, dan `deploy`. Job `deploy` mendorong kode terbaru ke kedua Hugging Face Spaces secara otomatis setelah `lint` dan `test` lulus, dan setelah `build` memverifikasi bahwa kedua Docker image dapat dibangun tanpa error.

Setiap push ke branch `main` memicu seluruh pipeline. Pull request ke `main` hanya memicu job `lint` dan `test` — tidak ada deploy ke HF dari PR. Ini adalah perilaku standar CI/CD yang melindungi environment production dari kode yang belum di-review.

DEV-07 bergantung pada DEV-04 (test suite sudah bisa lulus), DEV-05 (Dockerfile sudah terbukti bisa di-build), dan DEV-06 (dua HF Spaces sudah aktif dan URL-nya diketahui). DEV-07 adalah phase terakhir sebelum DEV-08 (README & Portfolio Documentation).

---

## BEFORE YOU START THIS PHASE

Baca dan konfirmasi hal-hal berikut sebelum mengeksekusi task apapun.

**Required reading:**
- `pytest.ini` (hasil DEV-04): catat nama marker `unit` dan `integration` — workflow akan menggunakan marker ini untuk selective test execution.
- `Dockerfile.api` dan `Dockerfile.ui` (hasil DEV-05): catat nama file persis karena workflow memanggil keduanya via flag `-f`.
- `DEPLOYMENT_URLS.md` (hasil DEV-06, file lokal): catat dua HF git remote URL yang akan menjadi target push di job `deploy`.

**Secrets yang harus sudah siap sebelum memulai Task 1.1.1:**
- `HF_TOKEN` — token Hugging Face dengan akses write, dibuat di DEV-06 Task 1.1.1.

After reading, confirm with: "Reference files read. Ready to execute DEV-07."
Then wait for user instruction to begin.

---

## EXECUTION RULES FOR THIS PHASE

- Execute one task at a time.
- After completing each task, report what was done and wait for the user to say "next" or give a correction.
- Do not move to the next task unless the user explicitly confirms.
- Semua path file relatif terhadap root project.
- Tidak ada secret (token, API key) yang boleh ditulis secara langsung di dalam file YAML. Semua secret diakses melalui `${{ secrets.NAMA_SECRET }}`.
- Setiap job dalam workflow mendefinisikan `runs-on: ubuntu-latest` secara eksplisit — jangan gunakan matrix OS untuk kesederhanaan.
- Job `build` di CI tidak melakukan push image ke Docker registry karena proyek ini menggunakan pendekatan source-based deploy ke HF (push source code, HF build sendiri). Docker build di CI berfungsi murni sebagai smoke test untuk memastikan Dockerfile tidak broken.
- Job `deploy` hanya berjalan pada trigger `push` ke `main`, tidak pada `pull_request`. Ini dikonfigurasi dengan kondisi eksplisit di level job, bukan di level workflow.

---

## STEP 1 — GitHub Repository Secrets

### Substep 1.1 — Menambahkan Secrets di GitHub

**Task 1.1.1**
Buka repository GitHub project di browser. Navigasi ke `Settings` → `Secrets and variables` → `Actions` → tab `Secrets`. Klik `New repository secret` dan tambahkan secret berikut satu per satu:

`HF_TOKEN` — nilai: token Hugging Face yang dibuat di DEV-06 Task 1.1.1. Secret ini digunakan oleh job `deploy` untuk autentikasi saat git push ke HF Space remote.

`HF_USERNAME` — nilai: username Hugging Face kamu. Secret ini digunakan untuk membentuk URL HF Space remote secara dinamis di dalam workflow, sehingga URL tidak perlu di-hardcode di YAML.

Report: konfirmasi bahwa kedua secret sudah tersimpan di GitHub. Jangan tulis nilainya di sini.

---

### Substep 1.2 — GitHub Actions Variables (Non-Secret)

**Task 1.2.1**
Masih di halaman `Settings` → `Secrets and variables` → `Actions`, pindah ke tab `Variables`. Tambahkan dua variable berikut (bukan secret, karena nilainya tidak sensitif dan berguna untuk di-log di CI):

`HF_SPACE_API_NAME` — nilai: `tccp-api`. Ini adalah nama Space 1 tanpa username prefix.

`HF_SPACE_UI_NAME` — nilai: `tccp-ui`. Ini adalah nama Space 2 tanpa username prefix.

Report: konfirmasi kedua variable sudah tersimpan.

---

## STEP 2 — Workflow File: `ci-cd.yml`

### Substep 2.1 — Header dan Trigger

**Task 2.1.1**
Buat file `.github/workflows/ci-cd.yml` di root project. Tambahkan komentar header singkat di baris pertama yang menjelaskan tujuan workflow ini.

Definisikan nama workflow: `name: CI/CD Pipeline`.

Definisikan trigger `on` dengan dua event:

Pertama, `push` dengan filter `branches: [main]` dan `paths-ignore` yang mengecualikan file-file yang tidak perlu memicu pipeline: `['**.md', 'hf_spaces/**', 'notebooks/**', 'data/**', '.gitignore', 'DEPLOYMENT_URLS.md']`. Filter `paths-ignore` ini mencegah pipeline berjalan sia-sia hanya karena README atau notebook diubah.

Kedua, `pull_request` dengan filter `branches: [main]` dan `paths-ignore` yang identik. Untuk PR, pipeline tetap berjalan agar kode yang akan di-merge sudah terverifikasi — tapi job `deploy` tidak akan berjalan (dikontrol di level job pada task berikutnya).

Tambahkan juga `workflow_dispatch` tanpa parameter — ini memungkinkan pipeline dipicu secara manual dari tab Actions di GitHub, berguna untuk re-deploy tanpa harus melakukan commit baru.

---

### Substep 2.2 — Environment Variables Level Workflow

**Task 2.2.1**
Masih di `ci-cd.yml`. Tambahkan section `env` di level workflow (bukan di level job) untuk mendefinisikan variable yang digunakan di seluruh workflow:

`PYTHON_VERSION` dengan nilai `"3.11"` — digunakan oleh semua job yang membutuhkan Python setup.

`REGISTRY` dengan nilai `ghcr.io` — GitHub Container Registry. Meskipun image tidak di-push ke registry di workflow ini, konstanta ini didefinisikan di sini sebagai dokumentasi dan untuk kemudahan jika di masa depan deployment strategy berubah.

`IMAGE_API` dengan nilai `tccp-api` dan `IMAGE_UI` dengan nilai `tccp-ui` — nama image yang digunakan di job `build`.

---

### Substep 2.3 — Job: lint

**Task 2.3.1**
Masih di `ci-cd.yml`. Definisikan job pertama dengan nama `lint`.

`runs-on: ubuntu-latest`. Tidak ada `needs` karena ini adalah job pertama.

Definisikan steps berikut secara berurutan:

Step `Checkout repository` menggunakan `actions/checkout@v4`.

Step `Set up Python` menggunakan `actions/setup-python@v5` dengan parameter `python-version: ${{ env.PYTHON_VERSION }}`.

Step `Cache pip dependencies` menggunakan `actions/cache@v4`. Cache key menggunakan kombinasi OS, Python version, dan hash dari `requirements-dev.txt` — format: `${{ runner.os }}-pip-${{ env.PYTHON_VERSION }}-${{ hashFiles('requirements-dev.txt') }}`. Restore keys menggunakan prefix `${{ runner.os }}-pip-${{ env.PYTHON_VERSION }}-`. Path yang di-cache adalah output dari `pip cache dir` yang di-evaluasi menggunakan step output — atau gunakan path default `~/.cache/pip`.

Step `Install dev dependencies` menjalankan `pip install -r requirements-dev.txt`.

Step `Run flake8` menjalankan `flake8 src/ api/ app/ config/ --max-line-length=100 --exclude=__pycache__`. Flag `--max-line-length=100` memberikan sedikit kelonggaran dari default 79 yang terlalu ketat untuk kode ML.

Step `Run black check` menjalankan `black --check src/ api/ app/ config/ --line-length=100`. Flag `--check` tidak mengubah file, hanya melaporkan apakah ada yang perlu diformat ulang.

Step `Run isort check` menjalankan `isort --check-only src/ api/ app/ config/ --profile black`. Flag `--profile black` memastikan isort kompatibel dengan black formatting.

---

### Substep 2.4 — Job: test

**Task 2.4.1**
Masih di `ci-cd.yml`. Definisikan job kedua dengan nama `test`.

`runs-on: ubuntu-latest`. `needs: lint` — job ini hanya berjalan jika `lint` lulus.

Definisikan steps berikut:

Step `Checkout repository` menggunakan `actions/checkout@v4`.

Step `Set up Python` menggunakan `actions/setup-python@v5` dengan `python-version: ${{ env.PYTHON_VERSION }}`.

Step `Cache pip dependencies` — identik dengan yang ada di job `lint`, menggunakan cache key yang sama agar cache bisa dibagi antar job.

Step `Install dev dependencies` menjalankan `pip install -r requirements-dev.txt`.

---

**Task 2.4.2**
Masih di job `test`. Tambahkan dua step test:

Step `Run unit tests` menjalankan `pytest tests/unit/ -m unit -v --tb=short`. Unit test dijalankan terpisah dari integration test karena lebih cepat dan tidak bergantung pada artifact model.

Step `Run integration tests` menjalankan `pytest tests/integration/ -m integration -v --tb=short`. Tambahkan environment variable untuk step ini: `PYTHONPATH: ${{ github.workspace }}`. Tanpa `PYTHONPATH` yang benar, import dari `api.main` akan gagal di CI environment.

Tambahkan step `Generate coverage report` yang menjalankan `pytest tests/ --cov=src --cov=api --cov-report=xml --cov-report=term-missing`. Output XML dibutuhkan jika ingin upload ke Codecov di masa depan.

Tambahkan step `Upload coverage report` menggunakan `actions/upload-artifact@v4` dengan `name: coverage-report` dan `path: coverage.xml`. Artifact ini tersedia untuk di-download di tab Actions setelah pipeline selesai — berguna untuk portfolio review.

---

### Substep 2.5 — Job: build

**Task 2.5.1**
Masih di `ci-cd.yml`. Definisikan job ketiga dengan nama `build`.

`runs-on: ubuntu-latest`. `needs: test` — job ini hanya berjalan jika `test` lulus.

Definisikan steps berikut:

Step `Checkout repository` menggunakan `actions/checkout@v4`.

Step `Set up Docker Buildx` menggunakan `docker/setup-buildx-action@v3`. Buildx diperlukan untuk build yang lebih efisien dan mendukung multi-platform jika diperlukan di masa depan.

---

**Task 2.5.2**
Masih di job `build`. Tambahkan dua step build untuk masing-masing image.

Step `Build API Docker image` menjalankan:
`docker build -f Dockerfile.api -t ${{ env.IMAGE_API }}:${{ github.sha }} . --no-cache`

Flag `--no-cache` digunakan di CI untuk memastikan build bersih setiap kali. Flag `${{ github.sha }}` sebagai tag memastikan setiap build dapat diidentifikasi secara unik berdasarkan commit yang memicunya.

Step `Build UI Docker image` menjalankan:
`docker build -f Dockerfile.ui -t ${{ env.IMAGE_UI }}:${{ github.sha }} . --no-cache`

Catatan penting: kedua step ini hanya melakukan `docker build`, tidak ada `docker push` ke registry manapun. Image hanya ada di runner CI dan akan dihapus setelah job selesai. Tujuan job `build` adalah semata-mata memverifikasi bahwa kedua Dockerfile tidak broken dan semua dependency bisa di-install dengan benar.

---

**Task 2.5.3**
Masih di job `build`. Tambahkan step `Verify API image health` yang menjalankan container API secara singkat untuk memverifikasi bahwa aplikasi bisa startup tanpa crash.

Step ini menjalankan serangkaian perintah shell dalam satu `run` block (gunakan `|` untuk multi-line):

Pertama, jalankan container API di background: `docker run -d --name api-smoke-test -p 7860:7860 ${{ env.IMAGE_API }}:${{ github.sha }}`.

Kedua, tunggu beberapa detik untuk startup: `sleep 45` — waktu ini dibutuhkan karena model artifact loading saat startup.

Ketiga, kirim request health check: `curl --fail --retry 3 --retry-delay 5 http://localhost:7860/health`.

Keempat, hentikan dan hapus container: `docker stop api-smoke-test && docker rm api-smoke-test`.

Jika langkah curl gagal (exit code non-zero), step ini akan gagal dan seluruh job `build` dianggap gagal — deploy tidak akan berjalan.

---

### Substep 2.6 — Job: deploy

**Task 2.6.1**
Masih di `ci-cd.yml`. Definisikan job keempat dengan nama `deploy`.

`runs-on: ubuntu-latest`. `needs: build` — job ini hanya berjalan jika `build` lulus.

Tambahkan kondisi `if` di level job untuk memastikan deploy hanya terjadi pada push ke `main`, bukan pada PR: `if: github.event_name == 'push' && github.ref == 'refs/heads/main'`

Kondisi ini adalah pengaman kritis — tanpa ini, setiap PR yang di-merge akan men-trigger deploy, tapi PR dari fork atau branch lain juga akan mencoba deploy menggunakan secrets yang mungkin tidak tersedia untuk mereka.

---

**Task 2.6.2**
Masih di job `deploy`. Definisikan steps berikut:

Step `Checkout repository` menggunakan `actions/checkout@v4` dengan parameter tambahan `fetch-depth: 0` — ini memastikan seluruh git history tersedia, dibutuhkan untuk git operations di steps berikutnya.

Step `Configure git identity` menjalankan dua perintah git config:
`git config --global user.email "github-actions[bot]@users.noreply.github.com"`
`git config --global user.name "github-actions[bot]"`

Identity ini diperlukan karena job `deploy` akan melakukan git commit di repository HF Space.

Step `Install git-lfs` menjalankan `git lfs install` — dibutuhkan karena artifact model dikelola oleh git-lfs di HF Space repository.

---

**Task 2.6.3**
Masih di job `deploy`. Tambahkan step `Deploy API to HF Space` yang mendorong source code ke Space 1. Step ini adalah inti dari mekanisme deploy dan menggunakan pendekatan sparse checkout untuk efisiensi.

Step ini menjalankan serangkaian perintah dalam satu `run` block:

Definisikan variable lokal untuk URL HF Space API: `HF_API_URL=https://${{ secrets.HF_USERNAME }}:${{ secrets.HF_TOKEN }}@huggingface.co/spaces/${{ secrets.HF_USERNAME }}/${{ vars.HF_SPACE_API_NAME }}`

Clone repository HF Space API ke direktori sementara: `git clone $HF_API_URL hf_deploy_api`

Masuk ke direktori clone: `cd hf_deploy_api`

Aktifkan git-lfs di repository yang di-clone: `git lfs install`

Hapus semua file di repository HF kecuali `.git/` dan `.gitattributes`: `find . -not -path './.git*' -not -name '.gitattributes' -delete 2>/dev/null || true`

Salin file-file yang diperlukan dari repository GitHub ke direktori clone. Salin dengan perintah terpisah untuk setiap komponen: `cp $GITHUB_WORKSPACE/Dockerfile.api ./Dockerfile`, `cp $GITHUB_WORKSPACE/requirements-base.txt .`, `cp $GITHUB_WORKSPACE/requirements-api.txt .`, `cp -r $GITHUB_WORKSPACE/config .`, `cp -r $GITHUB_WORKSPACE/src .`, `cp -r $GITHUB_WORKSPACE/api .`, `cp -r $GITHUB_WORKSPACE/models .`

Track artifact dengan git-lfs: `git lfs track "models/artifacts/*.joblib"`

Stage semua perubahan, buat commit dengan pesan yang menyertakan commit SHA dari GitHub: `git add -A && git commit -m "Deploy from GitHub: $GITHUB_SHA" --allow-empty`

Push ke HF Space: `git push origin main`

---

**Task 2.6.4**
Masih di job `deploy`. Tambahkan step `Deploy UI to HF Space` menggunakan pola yang identik dengan Task 2.6.3, tapi untuk Space 2.

Perbedaan dari step API: URL menggunakan `${{ vars.HF_SPACE_UI_NAME }}`, direktori clone adalah `hf_deploy_ui`, perintah salin tidak menyertakan `models/` (UI tidak butuh artifact), dan menyertakan komponen yang berbeda: `cp -r $GITHUB_WORKSPACE/app .`, `cp -r $GITHUB_WORKSPACE/.streamlit .`, `cp $GITHUB_WORKSPACE/requirements-ui.txt .`, `cp -r $GITHUB_WORKSPACE/src/utils ./src/utils` (hanya subfolder utils, bukan seluruh `src/`).

Jika `reports/xai_report/` ada dan berisi file, salin juga: `[ -d "$GITHUB_WORKSPACE/reports/xai_report" ] && cp -r $GITHUB_WORKSPACE/reports/xai_report ./reports/xai_report || mkdir -p reports/xai_report`. Ini menggunakan shell conditional agar step tidak gagal jika direktori belum ada.

---

### Substep 2.7 — Notifikasi Status Workflow

**Task 2.7.1**
Masih di `ci-cd.yml`. Tambahkan job kelima dan terakhir dengan nama `notify`.

`runs-on: ubuntu-latest`. `needs: [lint, test, build, deploy]`. `if: always()` — job ini selalu berjalan terlepas dari hasil job sebelumnya, sehingga notifikasi dikirim baik saat pipeline sukses maupun gagal.

Job ini tidak melakukan deploy atau test. Tujuannya adalah mengumpulkan hasil semua job dan mencetaknya ke log CI sebagai ringkasan yang mudah dibaca. Ini berguna untuk portfolio: reviewer yang melihat workflow run bisa langsung melihat ringkasan di satu tempat.

Step `Summary` menjalankan perintah yang menulis ke `$GITHUB_STEP_SUMMARY` — ini adalah built-in GitHub Actions variable yang menerima markdown dan menampilkannya di halaman summary run di GitHub UI:

```
echo "## Pipeline Summary" >> $GITHUB_STEP_SUMMARY
echo "| Job | Status |" >> $GITHUB_STEP_SUMMARY
echo "|-----|--------|" >> $GITHUB_STEP_SUMMARY
echo "| Lint | ${{ needs.lint.result }} |" >> $GITHUB_STEP_SUMMARY
echo "| Test | ${{ needs.test.result }} |" >> $GITHUB_STEP_SUMMARY
echo "| Build | ${{ needs.build.result }} |" >> $GITHUB_STEP_SUMMARY
echo "| Deploy | ${{ needs.deploy.result }} |" >> $GITHUB_STEP_SUMMARY
echo "" >> $GITHUB_STEP_SUMMARY
echo "**Commit:** ${{ github.sha }}" >> $GITHUB_STEP_SUMMARY
echo "**Triggered by:** ${{ github.event_name }}" >> $GITHUB_STEP_SUMMARY
```

---

## STEP 3 — Verifikasi Pipeline

### Substep 3.1 — Trigger Pipeline Pertama Kali

**Task 3.1.1**
Commit file `ci-cd.yml` ke branch `main` dan push ke GitHub. Pastikan commit message deskriptif: `"ci: add GitHub Actions CI/CD pipeline"`.

Buka tab `Actions` di repository GitHub. Verifikasi bahwa workflow run baru muncul dengan nama `CI/CD Pipeline`. Klik pada run tersebut dan pantau progress setiap job secara real-time. Report: apakah semua job berjalan dalam urutan yang benar (`lint` → `test` → `build` → `deploy`).

---

**Task 3.1.2**
Pantau job `lint` hingga selesai. Verifikasi bahwa semua tiga linter (`flake8`, `black --check`, `isort --check-only`) lulus tanpa error. Jika ada linting error, laporkan nama file dan baris yang bermasalah — perbaiki di codebase, commit, dan biarkan pipeline berjalan ulang secara otomatis. Jangan lanjut ke task berikutnya sampai `lint` lulus.

---

**Task 3.1.3**
Pantau job `test` hingga selesai. Verifikasi bahwa semua unit test dan integration test lulus. Verifikasi bahwa artifact `coverage-report` muncul di halaman summary run dan bisa di-download. Jika ada test yang gagal, laporkan nama test dan pesan error dari log CI. Perbaiki di codebase, commit, dan biarkan pipeline berjalan ulang.

---

**Task 3.1.4**
Pantau job `build` hingga selesai. Verifikasi bahwa kedua Docker build berhasil tanpa error. Verifikasi bahwa smoke test health check di step `Verify API image health` menghasilkan response yang valid. Jika build gagal, laporkan log build layer mana yang error dan pesan lengkapnya.

---

**Task 3.1.5**
Pantau job `deploy` hingga selesai. Verifikasi bahwa kedua step deploy (API dan UI) berhasil push ke HF Space masing-masing tanpa error. Buka kedua HF Space di browser setelah deploy selesai dan verifikasi bahwa versi terbaru sudah aktif — cek di tab "Logs" HF Space bahwa build dipicu oleh commit SHA yang sesuai dengan commit dari GitHub. Report status kedua Space.

---

### Substep 3.2 — Test Pipeline pada Pull Request

**Task 3.2.1**
Buat branch baru dari `main`: `git checkout -b test/ci-pr-validation`. Buat perubahan kecil yang tidak berbahaya — misalnya tambahkan satu baris komentar di `config/settings.py`. Commit dan push branch tersebut ke GitHub: `git push origin test/ci-pr-validation`.

Buat Pull Request dari branch tersebut ke `main` melalui GitHub UI. Verifikasi bahwa pipeline berjalan pada PR ini. Verifikasi bahwa job `lint` dan `test` berjalan, tapi job `deploy` tidak berjalan (karena kondisi `if: github.event_name == 'push'` tidak terpenuhi untuk PR). Report hasil verifikasi ini — ini membuktikan bahwa mekanisme proteksi deploy berfungsi.

---

**Task 3.2.2**
Merge PR tersebut ke `main` melalui GitHub UI. Verifikasi bahwa merge memicu pipeline baru di `main`. Verifikasi bahwa kali ini seluruh pipeline berjalan termasuk job `deploy`. Ini mengkonfirmasi bahwa trigger push-to-main dan kondisi deploy berfungsi dengan benar secara end-to-end. Report hasil.

Setelah verifikasi selesai, hapus branch `test/ci-pr-validation`: `git push origin --delete test/ci-pr-validation`.

---

### Substep 3.3 — Test Pipeline pada Perubahan yang Dikecualikan

**Task 3.3.1**
Edit file `README.md` di root project (konten bebas — ini hanya untuk test). Commit dan push ke `main` langsung. Buka tab `Actions` di GitHub dan verifikasi bahwa tidak ada workflow run baru yang dipicu oleh push ini. Ini membuktikan bahwa filter `paths-ignore` berfungsi dan pipeline tidak berjalan sia-sia untuk perubahan dokumentasi. Report hasil.

---

### Substep 3.4 — Verifikasi Manual Trigger

**Task 3.4.1**
Buka tab `Actions` di GitHub. Pilih workflow `CI/CD Pipeline`. Klik tombol `Run workflow` → pilih branch `main` → klik `Run workflow`. Verifikasi bahwa pipeline berjalan secara manual via `workflow_dispatch` tanpa perlu melakukan commit baru. Report apakah seluruh pipeline termasuk `deploy` berjalan dengan benar.

---

## DEV-07 COMPLETE

Setelah Task 3.4.1 selesai dan semua verifikasi lulus, DEV-07 selesai.

Informasikan ke user: "DEV-07 complete. CI/CD pipeline aktif dengan 4 job: lint → test → build → deploy. Pipeline terkonfirmasi:
- Berjalan pada push ke main (dengan deploy)
- Berjalan pada PR ke main (tanpa deploy)
- Tidak berjalan pada perubahan file yang dikecualikan (markdown, notebooks)
- Bisa dipicu secara manual via workflow_dispatch

Kedua HF Spaces ter-update otomatis setelah setiap push ke main yang melewati seluruh pipeline. Siap untuk DEV-08 (README & Portfolio Documentation)."

---

## RINGKASAN DEV-07

| Step | Substep | Task | File / Output |
|---|---|---|---|
| Step 1 — Secrets | 1.1 | 1.1.1 | `HF_TOKEN`, `HF_USERNAME` di GitHub Secrets |
| | 1.2 | 1.2.1 | `HF_SPACE_API_NAME`, `HF_SPACE_UI_NAME` di GitHub Variables |
| Step 2 — Workflow | 2.1 | 2.1.1 | `.github/workflows/ci-cd.yml` — header & trigger |
| | 2.2 | 2.2.1 | `.github/workflows/ci-cd.yml` — env vars |
| | 2.3 | 2.3.1 | `.github/workflows/ci-cd.yml` — job lint |
| | 2.4 | 2.4.1, 2.4.2 | `.github/workflows/ci-cd.yml` — job test |
| | 2.5 | 2.5.1, 2.5.2, 2.5.3 | `.github/workflows/ci-cd.yml` — job build |
| | 2.6 | 2.6.1, 2.6.2, 2.6.3, 2.6.4 | `.github/workflows/ci-cd.yml` — job deploy |
| | 2.7 | 2.7.1 | `.github/workflows/ci-cd.yml` — job notify |
| Step 3 — Verifikasi | 3.1 | 3.1.1 – 3.1.5 | Pipeline run pertama end-to-end |
| | 3.2 | 3.2.1, 3.2.2 | PR flow terkonfirmasi |
| | 3.3 | 3.3.1 | paths-ignore terkonfirmasi |
| | 3.4 | 3.4.1 | Manual trigger terkonfirmasi |
| **Total** | **13 substep** | **19 task** | **1 file YAML** |
