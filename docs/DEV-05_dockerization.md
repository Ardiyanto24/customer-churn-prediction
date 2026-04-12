# TCCP Deployment — Development Instructions
## DEV-05: Dockerization

---

## WHAT THIS PHASE COVERS

DEV-05 mengimplementasikan containerization untuk kedua service: `Dockerfile.api` untuk FastAPI dan `Dockerfile.ui` untuk Streamlit. Phase ini juga mencakup `.dockerignore`, verifikasi build lokal untuk kedua image, dan verifikasi end-to-end bahwa kedua container bisa berkomunikasi satu sama lain via Docker network.

Kedua Dockerfile dirancang khusus untuk deployment ke Hugging Face Spaces yang memiliki constraint port tunggal (7860). FastAPI di-expose di port 7860 bukan port default 8000, dan Streamlit di-expose di port 7860 bukan port default 8501. Di masing-masing container, port internal tetap menggunakan default masing-masing, dan hanya port yang di-expose ke luar yang di-map ke 7860.

DEV-05 bergantung pada DEV-02 dan DEV-03 yang sudah selesai. DEV-05 adalah prasyarat untuk DEV-06 (Hugging Face Spaces Setup) dan DEV-07 (CI/CD).

---

## BEFORE YOU START THIS PHASE

Baca file berikut secara penuh sebelum mengeksekusi task apapun di phase ini.

**Required reading:**
- `requirements-api.txt` dan `requirements-ui.txt` (hasil DEV-01): ini adalah daftar dependency yang di-install di masing-masing image. Pahami bahwa keduanya memanggil `-r requirements-base.txt` sehingga `requirements-base.txt` juga harus tersedia saat build.
- `api/main.py` (hasil DEV-02): cek perintah yang digunakan untuk menjalankan uvicorn — `host` dan `port`-nya. Dockerfile harus menggunakan perintah yang sama.
- `app/main.py` (hasil DEV-03): cek nama file entry point Streamlit yang benar, karena `CMD` di Dockerfile harus memanggil file ini secara eksplisit.
- `config/settings.py` (hasil DEV-01): catat bahwa `API_BASE_URL` harus di-set via environment variable — di container Streamlit, variabel ini menunjuk ke URL publik Space 1, bukan `localhost`.

After reading, confirm with: "Reference files read. Ready to execute DEV-05."
Then wait for user instruction to begin.

---

## EXECUTION RULES FOR THIS PHASE

- Execute one task at a time.
- After completing each task, report what was done and wait for the user to say "next" or give a correction.
- Do not move to the next task unless the user explicitly confirms.
- Semua path file relatif terhadap root project.
- Kedua Dockerfile menggunakan base image `python:3.11-slim` — bukan `python:3.11-full` atau image Ubuntu. `slim` dipilih karena lebih kecil dan cukup untuk kebutuhan project ini.
- Tidak ada credential (API key, token) yang boleh di-hardcode di Dockerfile maupun di image layer. Semua secret dilewatkan melalui environment variable saat `docker run`.
- Model artifact (`model_final.joblib` dan `preprocessor.joblib`) di-copy ke dalam image API saat build. Ini adalah keputusan yang disengaja untuk portfolio: artifact di-bundle bersama image sehingga deployment ke HF Spaces tidak membutuhkan volume mount. Di production nyata, artifact akan diambil dari model registry — dan hal ini harus dijelaskan di README (DEV-08).
- Jangan install `pytest`, `flake8`, `black`, atau tools dev lainnya di dalam image production. Gunakan `requirements-api.txt` dan `requirements-ui.txt`, bukan `requirements-dev.txt`.

---

## STEP 1 — `.dockerignore`

### Substep 1.1 — Konfigurasi Docker Build Context

**Task 1.1.1**
Buat file `.dockerignore` di root project. File ini mengecualikan file dan folder yang tidak perlu masuk ke dalam Docker build context — mempercepat `docker build` dan mengurangi ukuran image.

Kategori yang harus dikecualikan:

**Development artifacts:** `.git/`, `.gitignore`, `.env` (file env lokal — secret dilewatkan via `docker run --env`, bukan di-copy ke image), `*.pyc`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `htmlcov/`, `.coverage`.

**Data dan model yang tidak perlu masuk UI image:** `data/raw/`, `data/processed/`, `data/splits/`. Direktori ini tidak dibutuhkan oleh image manapun — data hanya digunakan saat training, bukan inference.

**Notebook dan dokumentasi:** `notebooks/`, `reports/` (kecuali file XAI yang dibutuhkan UI — ini akan dihandle di Dockerfile.ui dengan COPY selektif), `*.md` (kecuali `README.md` — ini opsional, bisa dikecualikan untuk memperkecil image).

**Requirements yang tidak relevan:** `requirements-dev.txt`, `requirements.txt` (convenience file untuk dev lokal — tidak digunakan di Dockerfile).

**Tools dan config lokal:** `pytest.ini`, `wandb/`, `logs/`.

Catatan penting: `.dockerignore` berlaku untuk semua `docker build` di direktori ini — baik untuk `Dockerfile.api` maupun `Dockerfile.ui`. File yang dikecualikan di `.dockerignore` tidak bisa di-COPY di Dockerfile manapun. Pastikan file yang dibutuhkan oleh salah satu image (misal `models/artifacts/`) tidak dikecualikan.

---

## STEP 2 — `Dockerfile.api`

### Substep 2.1 — Base dan Dependencies

**Task 2.1.1**
Buat file `Dockerfile.api` di root project. Tambahkan header komentar singkat yang menjelaskan bahwa ini adalah Dockerfile untuk FastAPI service (Space 1 di Hugging Face).

Tentukan base image: `python:3.11-slim`. Tentukan `WORKDIR /app`.

Set environment variable berikut di layer ini menggunakan `ENV`: `PYTHONDONTWRITEBYTECODE=1` untuk mencegah Python menulis file `.pyc` di dalam container, `PYTHONUNBUFFERED=1` untuk memastikan output log langsung dikirim ke stdout tanpa buffering (penting agar log terlihat di HF Spaces), dan `PYTHONPATH=/app` agar semua module (`config`, `src`, `api`) bisa di-import tanpa prefix path.

---

**Task 2.1.2**
Masih di `Dockerfile.api`. Tambahkan layer instalasi sistem dependency yang dibutuhkan oleh library Python. Beberapa library ML (khususnya LightGBM dan library numerik) membutuhkan shared library sistem. Jalankan `apt-get update` diikuti instalasi package berikut: `libgomp1` (dibutuhkan LightGBM untuk OpenMP), `libglib2.0-0` (dibutuhkan beberapa library numerik), `curl` (dibutuhkan untuk health check di HF Spaces). Jalankan `apt-get clean` dan hapus `/var/lib/apt/lists/*` setelah instalasi untuk menjaga ukuran layer tetap kecil. Seluruh operasi ini dalam satu `RUN` instruction untuk meminimalkan jumlah layer.

---

**Task 2.1.3**
Masih di `Dockerfile.api`. Tambahkan layer instalasi Python dependency. Urutan layer harus dioptimalkan untuk Docker layer caching: copy file requirements terlebih dahulu sebelum meng-copy source code, sehingga layer instalasi tidak perlu di-rebuild setiap kali source code berubah.

COPY file-file berikut ke dalam image terlebih dahulu: `requirements-base.txt` dan `requirements-api.txt`. Kemudian jalankan `pip install --no-cache-dir -r requirements-api.txt`. Flag `--no-cache-dir` mencegah pip menyimpan cache di dalam image sehingga ukuran image lebih kecil.

---

### Substep 2.2 — Source Code dan Artifacts

**Task 2.2.1**
Masih di `Dockerfile.api`. Tambahkan layer untuk meng-copy source code dan konfigurasi. Copy file dan folder berikut secara selektif — jangan COPY seluruh direktori project dengan `COPY . .` karena akan membawa file yang tidak perlu:

- `COPY config/ ./config/` — konstanta global yang dibutuhkan saat startup
- `COPY src/ ./src/` — shared utilities (`logger.py`, `serialization.py`) dan preprocessing code yang mungkin digunakan predictor
- `COPY api/ ./api/` — seluruh FastAPI service

---

**Task 2.2.2**
Masih di `Dockerfile.api`. Tambahkan layer untuk meng-copy model artifacts. Copy direktori `models/artifacts/` ke dalam image:

`COPY models/artifacts/ ./models/artifacts/`

Setelah instruksi COPY ini, tambahkan komentar yang menjelaskan bahwa artifact di-bundle ke dalam image untuk kemudahan deployment ke HF Spaces free tier (yang tidak mendukung volume mount persisten). Di production nyata dengan infrastruktur yang proper, artifact seharusnya di-pull dari model registry (WandB artifact) saat container startup, bukan di-bundle ke dalam image.

Pastikan `models/artifacts/` tidak dikecualikan di `.dockerignore` — jika dikecualikan, layer ini akan gagal.

---

### Substep 2.3 — Port, Healthcheck, dan CMD

**Task 2.3.1**
Masih di `Dockerfile.api`. Tambahkan `EXPOSE 7860`. Meskipun FastAPI secara internal berjalan di port yang dikonfigurasi via `API_PORT`, HF Spaces mengharuskan aplikasi mendengarkan di port 7860. Set environment variable `API_PORT=7860` dan `API_HOST=0.0.0.0` di Dockerfile sehingga `config/settings.py` membaca nilai yang benar saat dijalankan di container.

Tambahkan `HEALTHCHECK` instruction: interval 30 detik, timeout 10 detik, start-period 40 detik (waktu yang cukup untuk artifact loading saat startup), retries 3. Command health check menggunakan `curl --fail http://localhost:7860/health || exit 1`.

---

**Task 2.3.2**
Masih di `Dockerfile.api`. Tambahkan `CMD` di bagian paling bawah. Perintah yang digunakan: `uvicorn api.main:app --host 0.0.0.0 --port 7860 --workers 1`. Flag `--workers 1` digunakan karena HF Spaces free tier memiliki memory terbatas, dan multiple worker akan menggandakan memory yang dibutuhkan untuk load model.

Gunakan format JSON array untuk `CMD` (`CMD ["uvicorn", ...]`), bukan shell form (`CMD uvicorn ...`). Format JSON array lebih tepat untuk production karena sinyal SIGTERM dikirim langsung ke proses uvicorn, bukan ke shell wrapper, sehingga graceful shutdown berfungsi dengan benar.

---

## STEP 3 — `Dockerfile.ui`

### Substep 3.1 — Base dan Dependencies

**Task 3.1.1**
Buat file `Dockerfile.ui` di root project. Tambahkan header komentar yang menjelaskan bahwa ini adalah Dockerfile untuk Streamlit UI service (Space 2 di Hugging Face).

Tentukan base image: `python:3.11-slim`. Tentukan `WORKDIR /app`.

Set environment variable: `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, `PYTHONPATH=/app`. Tambahkan juga `STREAMLIT_SERVER_PORT=7860` dan `STREAMLIT_SERVER_ADDRESS=0.0.0.0` — Streamlit membaca konfigurasi server dari environment variable dengan prefix `STREAMLIT_`, sehingga ini lebih bersih daripada menyertakan flag di CMD.

Tambahkan satu environment variable placeholder: `API_BASE_URL=http://localhost:7860`. Nilai ini akan di-override saat `docker run` di lokal (untuk testing) maupun di HF Spaces Settings (untuk deployment). Nilai default `localhost:7860` hanya relevan jika UI dan API dijalankan dalam satu container — yang bukan kasus deployment kita.

---

**Task 3.1.2**
Masih di `Dockerfile.ui`. Tambahkan layer sistem dependency. UI service tidak membutuhkan LightGBM atau library ML berat (inference dilakukan oleh API service), sehingga `apt-get` install lebih minimal: hanya `libglib2.0-0` dan `curl`. Jalankan `apt-get clean` dan hapus cache di instruksi yang sama.

---

**Task 3.1.3**
Masih di `Dockerfile.ui`. Tambahkan layer instalasi Python dependency. Copy `requirements-base.txt` dan `requirements-ui.txt` terlebih dahulu sebelum source code, kemudian jalankan `pip install --no-cache-dir -r requirements-ui.txt`.

Catatan: `requirements-ui.txt` memanggil `-r requirements-base.txt` yang menyertakan `shap`, `scikit-learn`, dan library ML lainnya. Ini memang dibutuhkan karena halaman analytics menampilkan SHAP visualizations — meskipun tidak melakukan inference. Jika di masa depan halaman analytics hanya menampilkan gambar statis, `requirements-base.txt` bisa dihapus dari `requirements-ui.txt` untuk memperkecil image UI secara signifikan.

---

### Substep 3.2 — Source Code dan Konfigurasi Streamlit

**Task 3.2.1**
Masih di `Dockerfile.ui`. Tambahkan layer untuk meng-copy source code:

- `COPY config/ ./config/` — dibutuhkan untuk membaca `API_BASE_URL` dari settings
- `COPY src/utils/ ./src/utils/` — hanya utilities yang dibutuhkan (`logger.py`), bukan seluruh `src/`
- `COPY app/ ./app/` — seluruh Streamlit application

Copy juga folder `reports/xai_report/` jika ada, karena halaman analytics menampilkan file dari direktori ini: `COPY reports/xai_report/ ./reports/xai_report/`. Jika direktori ini belum ada saat build, gunakan pendekatan yang graceful: buat direktori kosong terlebih dahulu dengan `RUN mkdir -p reports/xai_report`, kemudian lakukan COPY conditional. Cara yang paling sederhana: selalu lakukan `RUN mkdir -p reports/xai_report` sebelum instruksi COPY, sehingga direktori selalu ada bahkan jika COPY tidak membawa file apapun.

---

**Task 3.2.2**
Masih di `Dockerfile.ui`. Buat file konfigurasi Streamlit yang akan di-copy ke dalam image. Streamlit membaca konfigurasi dari `.streamlit/config.toml` jika file tersebut ada.

Buat file `.streamlit/config.toml` di root project (bukan di dalam Docker, tapi sebagai file di repository). Isi dengan konfigurasi berikut:

Section `[server]`: `headless = true` (wajib untuk deployment — mencegah Streamlit membuka browser), `enableCORS = false` (karena API dan UI berada di domain berbeda di HF, CORS dihandle di sisi FastAPI), `enableXsrfProtection = false` (dinonaktifkan untuk kompatibilitas dengan HF Spaces iframe).

Section `[browser]`: `gatherUsageStats = false` (untuk privacy dan performa startup).

Section `[theme]` (opsional): bisa dikosongkan atau diisi dengan preferensi warna dasar.

Setelah file ini dibuat, tambahkan instruksi `COPY .streamlit/ ./.streamlit/` di `Dockerfile.ui` sebelum CMD.

---

### Substep 3.3 — Port dan CMD

**Task 3.3.1**
Masih di `Dockerfile.ui`. Tambahkan `EXPOSE 7860`.

Tambahkan `HEALTHCHECK`: interval 30 detik, timeout 10 detik, start-period 30 detik, retries 3. Command: `curl --fail http://localhost:7860/_stcore/health || exit 1`. Streamlit menyediakan endpoint `/_stcore/health` secara built-in yang mengembalikan status `ok` saat aplikasi siap.

Tambahkan `CMD` di bagian paling bawah menggunakan format JSON array: jalankan `streamlit run app/main.py`. Karena konfigurasi server sudah diset via environment variable (`STREAMLIT_SERVER_PORT`, `STREAMLIT_SERVER_ADDRESS`) dan file `config.toml`, tidak perlu flag tambahan di CMD.

---

## STEP 4 — Verifikasi Build Lokal

### Substep 4.1 — Build Image API

**Task 4.1.1**
Pastikan `models/artifacts/model_final.joblib` dan `models/artifacts/preprocessor.joblib` sudah ada sebelum menjalankan build. Jika belum ada, build akan gagal di layer COPY artifacts — ini adalah perilaku yang diharapkan dan harus dilaporkan dengan jelas, bukan di-workaround.

Jalankan perintah build: `docker build -f Dockerfile.api -t tccp-api:latest .` dari root project. Tambahkan flag `--progress=plain` untuk melihat output setiap layer secara detail: `docker build -f Dockerfile.api -t tccp-api:latest . --progress=plain`.

Verifikasi bahwa build selesai tanpa error. Report berapa lama build berlangsung dan total ukuran image yang dihasilkan (gunakan `docker images tccp-api`). Jika build gagal, laporkan layer mana yang gagal dan pesan error lengkapnya sebelum melanjutkan.

---

**Task 4.1.2**
Jalankan container API untuk verifikasi: `docker run --rm -p 7860:7860 --name tccp-api-test tccp-api:latest`.

Setelah container berjalan, buka `http://localhost:7860/health` dan verifikasi response JSON menunjukkan `status: "healthy"`. Buka `http://localhost:7860/docs` dan verifikasi Swagger UI tampil dengan benar. Kirim satu request ke `POST http://localhost:7860/predict` dan verifikasi response berhasil.

Report: apakah ketiga verifikasi ini berhasil. Jika ada yang gagal, laporkan pesan error dari log container (gunakan `docker logs tccp-api-test` di terminal lain) sebelum melanjutkan.

Setelah verifikasi selesai, hentikan container dengan `docker stop tccp-api-test` atau Ctrl+C.

---

### Substep 4.2 — Build Image UI

**Task 4.2.1**
Jalankan perintah build: `docker build -f Dockerfile.ui -t tccp-ui:latest . --progress=plain`.

Verifikasi bahwa build selesai tanpa error. Report ukuran image `tccp-ui` (gunakan `docker images tccp-ui`). Bandingkan ukurannya dengan `tccp-api` — UI image seharusnya lebih kecil karena tidak menyertakan model artifacts. Jika ukurannya jauh lebih besar dari yang diharapkan, periksa apakah ada file besar yang tidak sengaja ter-copy karena konfigurasi `.dockerignore` yang kurang tepat.

---

**Task 4.2.2**
Jalankan container UI dengan environment variable `API_BASE_URL` yang menunjuk ke container API yang sudah berjalan. Pertama, jalankan kembali container API: `docker run -d -p 7860:7860 --name tccp-api tccp-api:latest`. Kemudian jalankan container UI: `docker run --rm -p 8501:7860 -e API_BASE_URL=http://host.docker.internal:7860 --name tccp-ui-test tccp-ui:latest`.

Catatan: `host.docker.internal` adalah hostname khusus Docker Desktop (Mac dan Windows) untuk mengakses host machine dari dalam container. Di Linux, gunakan `--add-host=host.docker.internal:host-gateway` sebagai flag tambahan.

Buka `http://localhost:8501` dan verifikasi Streamlit tampil. Verifikasi sidebar menampilkan status API "🟢 API Connected". Report hasilnya.

---

### Substep 4.3 — Verifikasi End-to-End via Docker Network

**Task 4.3.1**
Hentikan semua container yang sedang berjalan. Buat Docker network khusus untuk komunikasi antar container: `docker network create tccp-network`.

Jalankan container API di network tersebut: `docker run -d --network tccp-network --name tccp-api -p 7860:7860 tccp-api:latest`.

Jalankan container UI di network yang sama, dengan `API_BASE_URL` menunjuk ke nama container API (bukan `localhost` atau `host.docker.internal`): `docker run -d --network tccp-network --name tccp-ui -p 8501:7860 -e API_BASE_URL=http://tccp-api:7860 tccp-ui:latest`.

Di dalam Docker network, container bisa berkomunikasi menggunakan nama container sebagai hostname. Ini adalah cara yang lebih bersih dan portabel dibanding `host.docker.internal`, dan ini meniru bagaimana dua HF Spaces berkomunikasi via URL publik masing-masing.

Buka `http://localhost:8501`, navigasi ke halaman Single Prediction, submit form, dan verifikasi bahwa prediksi berhasil diterima dari API container. Report hasilnya.

---

**Task 4.3.2**
Setelah verifikasi selesai, cleanup semua resource Docker yang dibuat selama phase ini: hentikan dan hapus semua container (`docker stop tccp-api tccp-ui && docker rm tccp-api tccp-ui`), hapus network (`docker network rm tccp-network`). Jangan hapus images `tccp-api:latest` dan `tccp-ui:latest` — keduanya akan digunakan sebagai referensi saat DEV-06 dan DEV-07.

Report perintah yang dijalankan dan konfirmasi semua resource sudah di-cleanup.

---

## STEP 5 — Verifikasi Ukuran dan Efisiensi Image

### Substep 5.1 — Analisis Layer

**Task 5.1.1**
Gunakan perintah `docker history tccp-api:latest --no-trunc` untuk melihat ukuran setiap layer. Identifikasi layer terbesar — biasanya layer instalasi Python packages atau layer COPY artifacts. Report tiga layer terbesar beserta ukurannya.

Jika layer artifacts (`models/artifacts/`) lebih dari 500MB, ini menandakan model artifact terlalu besar untuk di-bundle ke image dan perlu dipertimbangkan alternatif (misalnya lazy loading dari WandB saat container startup). Catat temuan ini — relevan untuk section "how to scale to production" di DEV-08.

---

**Task 5.1.2**
Verifikasi bahwa tidak ada file sensitif yang masuk ke dalam image. Jalankan container API dalam mode interaktif: `docker run --rm -it tccp-api:latest sh`. Di dalam container, verifikasi bahwa file `.env` tidak ada (`ls -la /app/.env` harus mengembalikan "No such file or directory"). Verifikasi bahwa `requirements-dev.txt` tidak ada di dalam container. Verifikasi bahwa `notebooks/` tidak ada. Exit dari container dan report hasilnya.

---

## DEV-05 COMPLETE

Setelah Task 5.1.2 selesai tanpa temuan yang tidak terduga, DEV-05 selesai.

Informasikan ke user: "DEV-05 complete. Dua Docker image berhasil di-build dan diverifikasi: `tccp-api:latest` ([ukuran]) dan `tccp-ui:latest` ([ukuran]). End-to-end communication via Docker network terkonfirmasi. Tidak ada file sensitif di dalam image. Siap untuk DEV-06 (Hugging Face Spaces Setup)."

---

## RINGKASAN DEV-05

| Step | Substep | Task | File |
|---|---|---|---|
| Step 1 — Dockerignore | 1.1 | 1.1.1 | `.dockerignore` |
| Step 2 — Dockerfile API | 2.1 | 2.1.1, 2.1.2, 2.1.3 | `Dockerfile.api` |
| | 2.2 | 2.2.1, 2.2.2 | `Dockerfile.api` |
| | 2.3 | 2.3.1, 2.3.2 | `Dockerfile.api` |
| Step 3 — Dockerfile UI | 3.1 | 3.1.1, 3.1.2, 3.1.3 | `Dockerfile.ui` |
| | 3.2 | 3.2.1, 3.2.2 | `Dockerfile.ui`, `.streamlit/config.toml` |
| | 3.3 | 3.3.1 | `Dockerfile.ui` |
| Step 4 — Verifikasi Build | 4.1 | 4.1.1, 4.1.2 | — |
| | 4.2 | 4.2.1, 4.2.2 | — |
| | 4.3 | 4.3.1, 4.3.2 | — |
| Step 5 — Analisis Image | 5.1 | 5.1.1, 5.1.2 | — |
| **Total** | **11 substep** | **18 task** | **4 file baru** |
