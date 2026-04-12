# TCCP Deployment — Development Instructions
## DEV-02: FastAPI Service

---

## WHAT THIS PHASE COVERS

DEV-02 mengimplementasikan seluruh service FastAPI yang bertanggung jawab atas inference. Phase ini mencakup empat file: `src/utils/logger.py` dan `src/utils/serialization.py` sebagai shared utilities yang juga digunakan komponen lain, `api/schemas.py` sebagai definisi seluruh Pydantic schema, `api/predictor.py` sebagai lapisan inference yang menangani artifact loading dan SHAP computation, dan `api/main.py` sebagai entry point aplikasi yang mendefinisikan seluruh endpoint.

Tidak ada logika training, EDA, maupun UI di phase ini. Semua logika preprocessing harus di-load dari `preprocessor.joblib` — tidak boleh ada preprocessing yang ditulis ulang di file manapun dalam `api/`.

DEV-02 bisa dikerjakan setelah DEV-01 selesai. DEV-02 tidak bergantung pada DEV-03 maupun DEV-04 dan bisa dikerjakan secara paralel dengan keduanya.

---

## BEFORE YOU START THIS PHASE

Baca file berikut secara penuh sebelum mengeksekusi task apapun di phase ini. Jangan eksekusi task apapun sebelum mengkonfirmasi bahwa kamu sudah membacanya.

**Required reading:**
- `churn-doc1-project-overview.md` — Section 6.1 (Raw Data Schema): catat setiap kolom, tipe data, dan seluruh nilai valid yang diizinkan. Ini adalah sumber kebenaran untuk schema validasi Pydantic. Section 8.2 (Training-Serving Parity): pahami mengapa tidak boleh ada preprocessing yang ditulis ulang di `api/predictor.py`. Section 9 (Configuration Reference): catat semua path konstanta yang akan digunakan.
- `config/settings.py` — baca seluruh file untuk memahami konstanta yang tersedia sebelum menulis kode yang mengimpornya.

After reading, confirm with: "Reference files read. Ready to execute DEV-02."
Then wait for user instruction to begin.

---

## EXECUTION RULES FOR THIS PHASE

- Execute one task at a time.
- After completing each task, report what was done and wait for the user to say "next" or give a correction.
- Do not move to the next task unless the user explicitly confirms.
- Semua path file relatif terhadap root project.
- Jangan tulis ulang logika preprocessing di file manapun dalam `api/` — selalu load dari `preprocessor.joblib`.
- Kolom `id` tidak menjadi bagian dari `CustomerInput` schema karena di-drop sebelum preprocessing di pipeline training. Jangan masukkan `id` ke dalam Pydantic model.
- SHAP values hanya dikembalikan untuk endpoint single predict (`POST /predict`), tidak untuk endpoint batch, karena overhead komputasinya signifikan saat input banyak.
- Artifacts (`model_final.joblib` dan `preprocessor.joblib`) harus di-load **satu kali saat startup**, bukan per-request.

---

## STEP 1 — Shared Utilities

### Substep 1.1 — Logger

**Task 1.1.1**
Buka `src/utils/logger.py`. Implementasikan fungsi `get_logger` yang menerima parameter `name` (string) dan mengembalikan objek `logging.Logger` yang sudah dikonfigurasi.

Logger yang dihasilkan harus memiliki dua handler: satu `StreamHandler` yang menulis ke stdout, dan satu `FileHandler` yang menulis ke file `logs/app.log`. Folder `logs/` harus dibuat secara otomatis jika belum ada — gunakan `pathlib.Path.mkdir(parents=True, exist_ok=True)`.

Format log harus mengikuti pola structured logging: setiap baris menyertakan timestamp ISO 8601, level, nama logger, dan pesan. Contoh format: `2024-01-15T10:30:00 | INFO | api.main | message here`.

Level default adalah `INFO`. Jika environment variable `LOG_LEVEL` di-set, gunakan nilainya. Pastikan tidak ada duplikasi handler jika `get_logger` dipanggil lebih dari satu kali dengan nama yang sama — cek apakah logger sudah memiliki handler sebelum menambahkan yang baru.

---

### Substep 1.2 — Serialization

**Task 1.2.1**
Buka `src/utils/serialization.py`. Implementasikan dua fungsi: `save_artifact` dan `load_artifact`.

`save_artifact` menerima `obj` (objek Python apapun), `path` (string atau `pathlib.Path`), dan `logger` (opsional, default `None`). Fungsi ini melakukan `joblib.dump(obj, path)`. Folder parent dari `path` harus dibuat otomatis jika belum ada. Jika `logger` disediakan, log pesan sukses beserta path-nya. Fungsi mengembalikan `True` jika berhasil, raise exception jika gagal.

`load_artifact` menerima `path` (string atau `pathlib.Path`) dan `logger` (opsional, default `None`). Fungsi ini mengecek apakah file ada di `path` — jika tidak ada, raise `FileNotFoundError` dengan pesan yang menyertakan path lengkapnya. Jika ada, jalankan `joblib.load(path)` dan kembalikan hasilnya. Jika `logger` disediakan, log pesan sukses beserta path dan tipe objek yang di-load.

---

## STEP 2 — Pydantic Schemas (`api/schemas.py`)

### Substep 2.1 — CustomerInput Schema

**Task 2.1.1**
Buka `api/schemas.py`. Implementasikan class `CustomerInput` sebagai Pydantic `BaseModel`. Class ini merepresentasikan satu baris data pelanggan yang dikirim sebagai input ke API — identik dengan raw data schema kecuali kolom `id` (di-drop) dan `Churn` (target, tidak ada di inference).

Field dan tipe yang harus ada:

Kelompok demografi: `gender` bertipe `Literal["Male", "Female"]`, `SeniorCitizen` bertipe `int` dengan constraint nilai hanya boleh `0` atau `1` — implementasikan via `Field` dengan `ge=0, le=1`, `Partner` bertipe `Literal["Yes", "No"]`, `Dependents` bertipe `Literal["Yes", "No"]`.

Kelompok layanan: `tenure` bertipe `int` dengan constraint `ge=1, le=72`, `PhoneService` bertipe `Literal["Yes", "No"]`, `MultipleLines` bertipe `Literal["Yes", "No", "No phone service"]`, `InternetService` bertipe `Literal["DSL", "Fiber optic", "No"]`.

Kelompok add-on (semua bertipe `Literal["Yes", "No", "No internet service"]`): `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`.

Kelompok billing: `Contract` bertipe `Literal["Month-to-month", "One year", "Two year"]`, `PaperlessBilling` bertipe `Literal["Yes", "No"]`, `PaymentMethod` bertipe `Literal["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"]`, `MonthlyCharges` bertipe `float` dengan constraint `ge=0.0`, `TotalCharges` bertipe `float` dengan constraint `ge=0.0`.

Tambahkan docstring class yang menjelaskan bahwa schema ini merepresentasikan satu data pelanggan untuk prediksi churn, dan bahwa kolom `id` tidak disertakan karena tidak digunakan sebagai fitur.

Tambahkan satu contoh data di `model_config` menggunakan `json_schema_extra` agar Swagger UI menampilkan example yang bermakna. Gunakan nilai yang secara bisnis masuk akal untuk pelanggan berisiko churn tinggi: kontrak month-to-month, tenure pendek, layanan fiber optic, tagihan bulanan tinggi.

---

### Substep 2.2 — Response Schemas

**Task 2.2.1**
Masih di `api/schemas.py`. Implementasikan class `PredictionResult` sebagai Pydantic `BaseModel`. Class ini merepresentasikan hasil prediksi untuk satu pelanggan.

Field yang harus ada: `churn_prediction` bertipe `bool` — `True` jika diprediksi churn, `False` jika tidak. `churn_probability` bertipe `float` — probabilitas churn antara 0.0 dan 1.0, dibulatkan 4 desimal. `risk_level` bertipe `str` — nilai berupa `"high"`, `"medium"`, atau `"low"` yang ditentukan berdasarkan `churn_probability`: high jika ≥ 0.7, medium jika ≥ 0.4, low jika < 0.4. `shap_values` bertipe `Optional[Dict[str, float]]` dengan default `None` — berisi SHAP value per fitur untuk satu prediksi, hanya diisi pada endpoint single predict.

---

**Task 2.2.2**
Masih di `api/schemas.py`. Implementasikan tiga class response tambahan.

`PredictionResponse` sebagai Pydantic `BaseModel` untuk response endpoint single predict. Field yang harus ada: `status` bertipe `str` dengan default `"success"`, `model_version` bertipe `str`, dan `result` bertipe `PredictionResult`.

`BatchPredictionItem` sebagai Pydantic `BaseModel` yang merepresentasikan satu item dalam hasil batch. Field yang harus ada: `index` bertipe `int` — posisi input dalam list asli, dan `result` bertipe `PredictionResult`.

`BatchPredictionResponse` sebagai Pydantic `BaseModel` untuk response endpoint batch predict. Field yang harus ada: `status` bertipe `str` dengan default `"success"`, `model_version` bertipe `str`, `total_input` bertipe `int`, `total_predicted` bertipe `int`, dan `results` bertipe `List[BatchPredictionItem]`.

---

**Task 2.2.3**
Masih di `api/schemas.py`. Implementasikan class `HealthResponse` sebagai Pydantic `BaseModel` untuk response endpoint `/health`.

Field yang harus ada: `status` bertipe `str` — bernilai `"healthy"` jika model dan preprocessor berhasil di-load, `"degraded"` jika salah satu gagal. `model_loaded` bertipe `bool`. `preprocessor_loaded` bertipe `bool`. `model_version` bertipe `str`. `uptime_seconds` bertipe `float` — berapa detik sejak aplikasi pertama kali start.

---

## STEP 3 — Predictor (`api/predictor.py`)

### Substep 3.1 — Artifact Management

**Task 3.1.1**
Buka `api/predictor.py`. Tambahkan import yang diperlukan dan inisialisasi logger menggunakan `get_logger("api.predictor")` dari `src/utils/logger.py`.

Implementasikan class `ModelPredictor`. Class ini adalah singleton yang menyimpan state model dan preprocessor setelah di-load. Atribut yang harus ada: `_model` (default `None`), `_preprocessor` (default `None`), `_model_version` (string, default `"unknown"`), `_is_ready` (bool, default `False`).

Implementasikan method `load_artifacts` yang menerima `model_path` dan `preprocessor_path` (keduanya `pathlib.Path` atau string). Method ini memanggil `load_artifact` dari `src/utils/serialization.py` untuk me-load keduanya. Jika keduanya berhasil, set `_is_ready = True` dan set `_model_version` dengan format string yang menyertakan nama file model. Jika salah satu gagal, log error-nya tapi jangan crash aplikasi — set `_is_ready = False` dan biarkan aplikasi tetap berjalan sehingga `/health` endpoint bisa melaporkan kondisi degraded. Method mengembalikan `bool` yang menandakan apakah kedua artifact berhasil di-load.

---

**Task 3.1.2**
Masih di `api/predictor.py`. Implementasikan method `_prepare_dataframe` pada class `ModelPredictor`.

Method ini menerima satu `CustomerInput` (atau list-nya untuk batch) dan mengkonversinya menjadi `pd.DataFrame` yang siap dikirim ke preprocessor. Langkah yang harus dilakukan: konversi input ke dict atau list of dict, buat DataFrame dari dict tersebut, pastikan urutan kolom sesuai dengan yang diharapkan pipeline — urutannya mengikuti urutan field di `CustomerInput`. Jangan tambahkan kolom `id` dan jangan tambahkan kolom `Churn`. Method mengembalikan `pd.DataFrame`.

---

### Substep 3.2 — Inference

**Task 3.2.1**
Masih di `api/predictor.py`. Implementasikan method `predict` pada class `ModelPredictor`.

Method ini menerima satu `CustomerInput` dan mengembalikan `PredictionResult`. Jika `_is_ready` adalah `False`, raise `RuntimeError` dengan pesan yang jelas bahwa model belum siap.

Alur inference yang harus diikuti: panggil `_prepare_dataframe` untuk mengkonversi input ke DataFrame, jalankan `self._preprocessor.transform(df)` untuk mentransformasi data — **tidak boleh** menggunakan `fit_transform`, hanya `transform`, kemudian jalankan `self._model.predict_proba(X_transformed)` untuk mendapatkan probabilitas, ambil probabilitas untuk kelas positif (churn = 1) dari kolom index 1, tentukan `churn_prediction` dengan membandingkan probabilitas terhadap threshold 0.5, tentukan `risk_level` berdasarkan aturan yang didefinisikan di Task 2.2.1, set `shap_values` ke `None` (SHAP dihitung terpisah di method lain), kembalikan `PredictionResult` yang sudah diisi.

Log setiap prediksi dengan level INFO. Pesan log harus menyertakan `churn_probability` dan `risk_level` tapi jangan log data input pelanggan secara lengkap karena bisa berisi data sensitif.

---

**Task 3.2.2**
Masih di `api/predictor.py`. Implementasikan method `predict_batch` pada class `ModelPredictor`.

Method ini menerima `List[CustomerInput]` dan mengembalikan `List[PredictionResult]`. Alurnya sama dengan `predict` tapi dioptimalkan untuk batch: semua input di-convert ke satu DataFrame sekaligus, satu kali `transform`, satu kali `predict_proba`, kemudian iterasi hasilnya untuk membentuk list `PredictionResult`. Semua `shap_values` di-set ke `None`. Log ringkasan di akhir: jumlah input, jumlah yang diprediksi churn, dan waktu eksekusi total dalam milidetik.

---

### Substep 3.3 — SHAP Computation

**Task 3.3.1**
Masih di `api/predictor.py`. Implementasikan method `compute_shap` pada class `ModelPredictor`.

Method ini menerima satu `CustomerInput` dan mengembalikan `Dict[str, float]` berisi SHAP value per nama fitur asli (sebelum encoding), atau `None` jika SHAP gagal dihitung.

Alur yang harus diikuti: panggil `_prepare_dataframe` untuk mendapatkan DataFrame input, jalankan `self._preprocessor.transform(df)` untuk mendapatkan data yang sudah ditransformasi, buat `shap.Explainer` menggunakan `self._model` — gunakan `shap.Explainer(self._model)` yang bisa auto-detect tipe model (tree-based atau linear), jalankan explainer pada satu baris data yang sudah ditransformasi, ambil SHAP values untuk kelas positif.

Nama fitur yang digunakan sebagai key dict adalah nama fitur **sebelum** encoding — yaitu nama kolom dari `CustomerInput`. Ini dilakukan dengan cara mengambil nama kolom dari DataFrame sebelum transform, kemudian memetakan SHAP values yang jumlahnya bisa berbeda (karena encoding mengubah jumlah kolom) kembali ke fitur original. Cara pemetaannya: gunakan `preprocessor.get_feature_names_out()` untuk mendapatkan nama fitur setelah encoding, lalu kelompokkan SHAP values berdasarkan prefix nama fitur asalnya, jumlahkan absolute SHAP values per fitur asal sebagai agregasi. Kembalikan dict yang sudah diurutkan berdasarkan absolute SHAP value secara descending.

Seluruh komputasi SHAP dibungkus dalam `try/except` — jika gagal karena alasan apapun, log warning dan kembalikan `None` agar prediksi utama tidak terganggu.

---

**Task 3.3.2**
Masih di `api/predictor.py`. Di bawah class `ModelPredictor`, buat satu instance singleton dengan nama `predictor = ModelPredictor()`. Instance ini yang akan di-import oleh `api/main.py`. Pastikan tidak ada artifact yang di-load pada saat module di-import — loading hanya terjadi saat `predictor.load_artifacts()` dipanggil secara eksplisit.

---

## STEP 4 — FastAPI Application (`api/main.py`)

### Substep 4.1 — App Initialization dan Lifespan

**Task 4.1.1**
Buka `api/main.py`. Tambahkan seluruh import yang diperlukan. Inisialisasi logger menggunakan `get_logger("api.main")`. Buat variabel `_start_time` yang di-set ke `time.time()` pada saat module di-load — ini digunakan untuk menghitung `uptime_seconds` di endpoint `/health`.

Implementasikan `lifespan` sebagai async context manager menggunakan `@asynccontextmanager` dari `contextlib`. Di bagian sebelum `yield`, panggil `predictor.load_artifacts(settings.MODEL_PATH, settings.PREPROCESSOR_PATH)` dan log hasilnya — sukses atau gagal. Di bagian setelah `yield`, log bahwa aplikasi sedang shutdown.

Buat instance aplikasi FastAPI dengan parameter berikut: `title="TCCP Churn Prediction API"`, `description` berisi kalimat singkat yang menjelaskan bahwa ini adalah REST API untuk prediksi churn pelanggan telekomunikasi, menggunakan model yang dilatih dengan pipeline end-to-end mencakup EDA, XAI quality gate, dan hyperparameter tuning, `version="1.0.0"`, dan `lifespan=lifespan`.

---

**Task 4.1.2**
Masih di `api/main.py`. Tambahkan middleware CORS menggunakan `CORSMiddleware` dari `fastapi.middleware.cors`. Konfigurasi `allow_origins` dengan nilai `["*"]` untuk development — ini aman karena API ini adalah read-only inference service, `allow_methods` dengan `["GET", "POST"]`, dan `allow_headers` dengan `["*"]`.

Tambahkan juga exception handler untuk `Exception` umum menggunakan `@app.exception_handler(Exception)`. Handler ini mengembalikan `JSONResponse` dengan status code 500 dan body `{"status": "error", "message": "Internal server error"}`. Log exception yang terjadi dengan level ERROR sebelum mengembalikan response.

---

### Substep 4.2 — Health Endpoint

**Task 4.2.1**
Masih di `api/main.py`. Implementasikan endpoint `GET /health`.

Endpoint ini tidak menerima parameter apapun. Endpoint mengembalikan `HealthResponse` yang diisi dengan nilai aktual: `status` bernilai `"healthy"` jika `predictor._is_ready` adalah `True`, `"degraded"` jika `False`. `model_loaded` dan `preprocessor_loaded` diisi dari state predictor. `model_version` diambil dari `predictor._model_version`. `uptime_seconds` dihitung dari `time.time() - _start_time`.

Response status HTTP harus `200` baik dalam kondisi healthy maupun degraded — status HTTP non-200 tidak tepat di sini karena aplikasi sedang berjalan, hanya modelnya yang belum siap. Kondisi degraded dikomunikasikan melalui body response.

---

### Substep 4.3 — Predict Endpoint

**Task 4.3.1**
Masih di `api/main.py`. Implementasikan endpoint `POST /predict`.

Endpoint ini menerima satu `CustomerInput` sebagai request body. Jika `predictor._is_ready` adalah `False`, kembalikan `JSONResponse` dengan status code 503 dan pesan yang menyatakan model belum siap menerima request.

Alur happy path: hitung SHAP values terlebih dahulu via `predictor.compute_shap(input)`, kemudian jalankan `predictor.predict(input)`, set field `shap_values` pada `PredictionResult` dengan hasil SHAP, kembalikan `PredictionResponse` dengan `model_version` dari predictor dan `result` berisi `PredictionResult`. Tangkap semua exception dengan `try/except`, log error-nya, dan kembalikan `JSONResponse` dengan status code 500.

Tambahkan tag `["Prediction"]` dan `summary="Predict churn for a single customer"` pada decorator endpoint.

---

**Task 4.3.2**
Masih di `api/main.py`. Implementasikan endpoint `POST /predict/batch`.

Endpoint ini menerima `List[CustomerInput]` sebagai request body. Validasi ukuran batch — jika panjang list melebihi 1000, kembalikan `JSONResponse` dengan status code 422 dan pesan yang menyatakan batas maksimum adalah 1000 pelanggan per request. Jika list kosong, kembalikan `JSONResponse` dengan status code 422 dan pesan yang sesuai.

Alur happy path: jalankan `predictor.predict_batch(inputs)`, bentuk list `BatchPredictionItem` dengan menyertakan index dari enumerate, kembalikan `BatchPredictionResponse`. Tangkap exception dan kembalikan 500 jika terjadi error.

Tambahkan tag `["Prediction"]` dan `summary="Predict churn for multiple customers (JSON)"`.

---

**Task 4.3.3**
Masih di `api/main.py`. Implementasikan endpoint `POST /predict/batch-csv`.

Endpoint ini menerima `UploadFile` dari FastAPI. Validasi bahwa file yang diupload memiliki extension `.csv` — jika tidak, kembalikan 422 dengan pesan yang sesuai.

Alur: baca konten file menggunakan `await file.read()`, decode ke string menggunakan UTF-8, parse menjadi DataFrame menggunakan `pd.read_csv(io.StringIO(content))`. Validasi bahwa semua kolom yang dibutuhkan (`CustomerInput` fields) ada di DataFrame — jika ada kolom yang kurang, kembalikan 422 dengan daftar kolom yang hilang. Jika ada kolom `id` atau `Churn` di CSV, drop keduanya sebelum diproses.

Konversi setiap baris DataFrame menjadi `CustomerInput` — jika ada baris yang gagal validasi Pydantic, skip baris tersebut dan catat index-nya. Jalankan batch prediction hanya untuk baris yang valid. Kembalikan `BatchPredictionResponse` dan sertakan informasi di `status` field jika ada baris yang diskip.

Tambahkan tag `["Prediction"]` dan `summary="Predict churn from CSV file upload"`.

---

### Substep 4.4 — Root Endpoint dan Entrypoint

**Task 4.4.1**
Masih di `api/main.py`. Implementasikan endpoint `GET /` sebagai welcome endpoint.

Endpoint ini mengembalikan `JSONResponse` sederhana berisi: `name` dengan nilai nama aplikasi, `version`, `docs` dengan nilai `"/docs"`, `health` dengan nilai `"/health"`, dan pesan singkat yang menjelaskan tujuan API ini. Tidak ada logika bisnis di endpoint ini — hanya navigasi.

---

**Task 4.4.2**
Masih di `api/main.py`. Di bagian paling bawah file, tambahkan blok `if __name__ == "__main__"` yang menjalankan aplikasi menggunakan `uvicorn.run`. Konfigurasi: `app="api.main:app"`, `host` dari `settings.API_HOST`, `port` dari `settings.API_PORT`, `reload=False`. Sertakan komentar yang menyatakan bahwa untuk development dengan hot reload, gunakan perintah `uvicorn api.main:app --reload` dari command line.

---

## STEP 5 — Verifikasi DEV-02

### Substep 5.1 — Verifikasi Startup

**Task 5.1.1**
Pastikan `models/artifacts/model_final.joblib` dan `models/artifacts/preprocessor.joblib` sudah ada. Jalankan aplikasi dengan perintah `uvicorn api.main:app --host 0.0.0.0 --port 8000` dari root project. Verifikasi bahwa tidak ada error saat startup. Verifikasi bahwa log startup menampilkan pesan sukses atau gagal untuk loading artifacts — bukan diam saja. Report output log startup lengkapnya.

---

**Task 5.1.2**
Dengan aplikasi yang sedang berjalan, akses `http://localhost:8000/health` via browser atau curl. Verifikasi response body berformat JSON sesuai `HealthResponse` schema. Verifikasi bahwa `status` bernilai `"healthy"` jika artifacts berhasil di-load. Report response body lengkapnya — jika `model_loaded` atau `preprocessor_loaded` bernilai `false`, laporkan error dari log startup sebelum melanjutkan.

---

### Substep 5.2 — Verifikasi Endpoints

**Task 5.2.1**
Akses `http://localhost:8000/docs`. Verifikasi bahwa Swagger UI tampil dengan benar dan semua endpoint terdaftar: `GET /`, `GET /health`, `POST /predict`, `POST /predict/batch`, `POST /predict/batch-csv`. Verifikasi bahwa setiap endpoint memiliki tag, summary, dan schema yang benar. Report apakah semua endpoint tampil dengan benar.

---

**Task 5.2.2**
Gunakan Swagger UI atau curl untuk mengirim request ke `POST /predict` dengan data contoh dari `CustomerInput.model_config`. Verifikasi bahwa response berformat sesuai `PredictionResponse` schema dengan status 200. Verifikasi bahwa `churn_probability` adalah nilai float antara 0 dan 1. Verifikasi bahwa `shap_values` bukan `null` dan berisi dict dengan key berupa nama fitur. Verifikasi bahwa `risk_level` adalah salah satu dari `"high"`, `"medium"`, atau `"low"`. Report response body lengkapnya.

---

**Task 5.2.3**
Kirim request ke `POST /predict/batch` dengan list berisi 3 customer input. Verifikasi bahwa response berformat `BatchPredictionResponse` dengan `total_input` bernilai 3 dan `results` berisi 3 item. Verifikasi bahwa setiap item dalam `results` memiliki `index` yang benar (0, 1, 2) dan `shap_values` adalah `null` untuk semua item. Report response body.

---

**Task 5.2.4**
Buat file CSV kecil dengan 5 baris data customer yang valid (gunakan kolom sesuai `CustomerInput` fields). Upload file tersebut ke `POST /predict/batch-csv`. Verifikasi response berformat `BatchPredictionResponse` dengan `total_input` bernilai 5. Kemudian uji edge case: upload CSV yang tidak memiliki salah satu kolom wajib dan verifikasi bahwa API mengembalikan status 422 dengan pesan yang menyebutkan kolom yang hilang. Report kedua response.

---

**Task 5.2.5**
Uji kondisi error: kirim request ke `POST /predict` dengan data yang tidak valid — misalnya `tenure` bernilai 100 (di luar range 1–72) atau `Contract` bernilai `"Weekly"` (bukan nilai yang diizinkan). Verifikasi bahwa FastAPI mengembalikan status 422 secara otomatis melalui Pydantic validation, dan response body menyertakan detail field mana yang gagal validasi. Report response body.

---

## DEV-02 COMPLETE

Setelah Task 5.2.5 selesai tanpa temuan yang tidak terduga, DEV-02 selesai.

Informasikan ke user: "DEV-02 complete. FastAPI service berjalan di port 8000 dengan 5 endpoint terverifikasi. SHAP values tersedia di single predict. Batch prediction mendukung JSON dan CSV upload. Siap untuk DEV-03 (Streamlit UI) dan DEV-04 (Testing Suite)."

---

## RINGKASAN DEV-02

| Step | Substep | Task | File |
|---|---|---|---|
| Step 1 — Shared Utilities | 1.1 | 1.1.1 | `src/utils/logger.py` |
| | 1.2 | 1.2.1 | `src/utils/serialization.py` |
| Step 2 — Schemas | 2.1 | 2.1.1 | `api/schemas.py` |
| | 2.2 | 2.2.1, 2.2.2, 2.2.3 | `api/schemas.py` |
| Step 3 — Predictor | 3.1 | 3.1.1, 3.1.2 | `api/predictor.py` |
| | 3.2 | 3.2.1, 3.2.2 | `api/predictor.py` |
| | 3.3 | 3.3.1, 3.3.2 | `api/predictor.py` |
| Step 4 — FastAPI App | 4.1 | 4.1.1, 4.1.2 | `api/main.py` |
| | 4.2 | 4.2.1 | `api/main.py` |
| | 4.3 | 4.3.1, 4.3.2, 4.3.3 | `api/main.py` |
| | 4.4 | 4.4.1, 4.4.2 | `api/main.py` |
| Step 5 — Verifikasi | 5.1 | 5.1.1, 5.1.2 | — |
| | 5.2 | 5.2.1, 5.2.2, 5.2.3, 5.2.4, 5.2.5 | — |
| **Total** | **13 substep** | **21 task** | **4 file** |
