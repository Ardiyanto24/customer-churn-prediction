# TCCP Deployment — Development Instructions
## DEV-03: Streamlit UI

---

## WHAT THIS PHASE COVERS

DEV-03 mengimplementasikan seluruh aplikasi Streamlit yang berfungsi sebagai antarmuka pengguna. Phase ini mencakup satu file shared component (`app/components/api_client.py`) yang menangani semua komunikasi ke FastAPI, satu file component untuk tampilan hasil prediksi (`app/components/result_card.py`), satu file component untuk visualisasi SHAP lokal (`app/components/shap_chart.py`), entry point aplikasi (`app/main.py`), dan tiga halaman: `prediction.py`, `batch_prediction.py`, dan `analytics.py`.

Streamlit tidak pernah memanggil model atau preprocessor secara langsung. Semua prediksi dilakukan melalui HTTP request ke FastAPI. Satu-satunya pengecualian adalah halaman `analytics.py` yang membaca file gambar dari `reports/xai_report/` — ini bukan inference, hanya menampilkan artefak laporan yang sudah ada.

DEV-03 bisa dikerjakan setelah DEV-01 selesai. DEV-03 tidak bergantung pada DEV-04. DEV-03 bergantung pada DEV-02 untuk verifikasi penuh, tapi bisa dikembangkan secara paralel dengan me-mock response API menggunakan data statis.

---

## BEFORE YOU START THIS PHASE

Baca file berikut secara penuh sebelum mengeksekusi task apapun di phase ini.

**Required reading:**
- `churn-doc1-project-overview.md` — Section 6.1 (Raw Data Schema): catat semua kolom, tipe, dan nilai valid karena semuanya menjadi field di form input halaman `prediction.py`. Section 4 (Tech Stack, bagian API & UI): pastikan memahami bahwa Streamlit menggunakan `httpx` untuk berkomunikasi ke FastAPI, bukan memanggil model secara langsung.
- `api/schemas.py` (hasil DEV-02): baca seluruh file. Semua response yang diterima Streamlit mengikuti schema yang didefinisikan di sana. Pahami struktur `PredictionResponse`, `BatchPredictionResponse`, dan `HealthResponse` sebelum menulis kode yang mem-parse-nya.
- `config/settings.py` (hasil DEV-01): catat `API_BASE_URL` — ini adalah satu-satunya konstanta yang dibutuhkan oleh `api_client.py`.

After reading, confirm with: "Reference files read. Ready to execute DEV-03."
Then wait for user instruction to begin.

---

## EXECUTION RULES FOR THIS PHASE

- Execute one task at a time.
- After completing each task, report what was done and wait for the user to say "next" or give a correction.
- Do not move to the next task unless the user explicitly confirms.
- Semua path file relatif terhadap root project.
- Jangan import apapun dari `api/` atau `src/training/` atau `src/xai/` di dalam kode Streamlit. Satu-satunya import yang diizinkan dari luar `app/` adalah `config/settings.py` (untuk `API_BASE_URL`) dan `src/utils/logger.py`.
- Semua komunikasi ke API menggunakan `httpx` dengan mode synchronous — bukan `asyncio`. Streamlit berjalan secara synchronous dan tidak mendukung `await` di level top-level script.
- Gunakan `st.session_state` untuk menyimpan hasil prediksi sehingga tidak hilang saat user berinteraksi dengan widget lain di halaman yang sama.
- Semua request ke API harus memiliki timeout yang eksplisit — gunakan 30 detik untuk single predict dan 120 detik untuk batch.

---

## STEP 1 — Shared Components

### Substep 1.1 — API Client

**Task 1.1.1**
Buat file `app/components/api_client.py`. File ini adalah satu-satunya tempat di seluruh `app/` yang boleh menggunakan `httpx`. Tidak ada halaman yang boleh membuat HTTP request secara langsung.

Tambahkan import yang diperlukan dan inisialisasi logger menggunakan `get_logger("app.api_client")`. Baca `API_BASE_URL` dari `config/settings.py` dan simpan sebagai konstanta modul.

Implementasikan fungsi `check_health` tanpa parameter. Fungsi ini mengirim `GET` ke `{API_BASE_URL}/health` dengan timeout 5 detik. Jika berhasil, kembalikan dict dari response JSON. Jika gagal karena koneksi ditolak, timeout, atau error HTTP apapun, kembalikan `None`. Jangan raise exception — fungsi ini digunakan untuk menampilkan status di sidebar dan kegagalannya tidak boleh crash aplikasi.

---

**Task 1.1.2**
Masih di `app/components/api_client.py`. Implementasikan fungsi `predict_single` yang menerima satu dict berisi data pelanggan. Fungsi ini mengirim `POST` ke `{API_BASE_URL}/predict` dengan body dict tersebut sebagai JSON, timeout 30 detik. Jika response status adalah 200, kembalikan response JSON sebagai dict. Jika status 422, kembalikan dict dengan key `"error"` dan value berisi detail validasi error dari response. Jika status 503, kembalikan dict dengan key `"error"` dan value pesan bahwa model belum siap. Untuk semua error lain termasuk koneksi gagal, log error-nya dan kembalikan dict dengan key `"error"` dan value pesan generik.

---

**Task 1.1.3**
Masih di `app/components/api_client.py`. Implementasikan fungsi `predict_batch_json` yang menerima `list` of dict dan mengirim `POST` ke `{API_BASE_URL}/predict/batch`, timeout 120 detik. Penanganan error mengikuti pola yang sama dengan `predict_single`.

Implementasikan fungsi `predict_batch_csv` yang menerima konten file dalam bentuk `bytes` dan nama file dalam bentuk `str`. Fungsi ini mengirim `POST` ke `{API_BASE_URL}/predict/batch-csv` menggunakan `files` parameter dari `httpx` — bukan `json`. Timeout 120 detik. Penanganan error mengikuti pola yang sama.

---

### Substep 1.2 — Result Card Component

**Task 1.2.1**
Buat file `app/components/result_card.py`. File ini berisi fungsi `render_result_card` yang menerima satu `PredictionResult`-equivalent dict dan me-render tampilan hasil prediksi ke Streamlit.

Tampilan yang harus dirender: sebuah container yang berisi label risiko (`risk_level`) ditampilkan sebagai badge berwarna — merah untuk `"high"`, kuning untuk `"medium"`, hijau untuk `"low"`. Di bawah badge, tampilkan `churn_probability` sebagai angka persentase besar (misal "73.4%") dengan label "Churn Probability". Di bawahnya, tampilkan `churn_prediction` sebagai teks "⚠ Likely to Churn" atau "✓ Likely to Stay". Gunakan `st.markdown` dengan HTML inline untuk warna badge — ini lebih fleksibel dari widget Streamlit standar.

Komponen ini tidak mengembalikan nilai — hanya me-render ke UI.

---

### Substep 1.3 — SHAP Chart Component

**Task 1.3.1**
Buat file `app/components/shap_chart.py`. File ini berisi fungsi `render_shap_bar_chart` yang menerima dict `shap_values` (key: nama fitur, value: float SHAP value) dan me-render horizontal bar chart ke Streamlit.

Chart yang harus dirender: urutkan fitur berdasarkan absolute SHAP value secara descending, tampilkan hanya top-10. Batang berwarna merah jika SHAP value positif (mendorong prediksi ke churn), biru jika negatif (mendorong ke tidak churn). Tambahkan label sumbu X "SHAP Value (impact on prediction)" dan judul "Feature Contributions". Gunakan `matplotlib` untuk membuat chart dan tampilkan ke Streamlit via `st.pyplot`. Pastikan figure di-close setelah ditampilkan menggunakan `plt.close()` untuk menghindari memory leak di Streamlit.

Jika `shap_values` adalah `None` atau dict kosong, tampilkan `st.info` dengan pesan bahwa SHAP tidak tersedia untuk prediksi ini.

---

## STEP 2 — Entry Point (`app/main.py`)

### Substep 2.1 — Page Config dan Sidebar

**Task 2.1.1**
Buka `app/main.py`. Tambahkan `st.set_page_config` di baris paling awal setelah import — ini harus menjadi perintah Streamlit pertama yang dieksekusi. Konfigurasi: `page_title="TCCP — Churn Predictor"`, `page_icon="📊"`, `layout="wide"`, `initial_sidebar_state="expanded"`.

Tambahkan import yang diperlukan termasuk `check_health` dari `app/components/api_client.py`.

---

**Task 2.1.2**
Masih di `app/main.py`. Implementasikan sidebar. Sidebar harus berisi: judul aplikasi "TCCP Churn Predictor" dengan subheader singkat, separator, navigasi ke tiga halaman menggunakan `st.page_link` atau pilihan navigasi yang sesuai dengan versi Streamlit yang digunakan, separator, dan section "API Status" di bagian bawah sidebar.

Section "API Status" harus memanggil `check_health()` dan menampilkan hasilnya: jika response tidak `None` dan `status` adalah `"healthy"`, tampilkan indikator hijau "🟢 API Connected" beserta `model_version`. Jika `status` adalah `"degraded"`, tampilkan "🟡 API Degraded". Jika response adalah `None`, tampilkan "🔴 API Unreachable".

Status API di-refresh setiap kali halaman di-render ulang — tidak ada cache khusus untuk ini karena informasinya harus selalu fresh.

---

**Task 2.1.3**
Masih di `app/main.py`. Tambahkan konten halaman utama (home page) yang ditampilkan ketika user pertama kali membuka aplikasi atau belum memilih halaman lain. Konten berupa: judul besar "Customer Churn Prediction", deskripsi singkat dua paragraf tentang apa yang bisa dilakukan aplikasi ini, dan tiga kolom yang masing-masing mendeskripsikan satu halaman tersedia (Single Prediction, Batch Prediction, Analytics) beserta navigasi menuju halaman tersebut.

---

## STEP 3 — Halaman Single Prediction (`app/pages/prediction.py`)

### Substep 3.1 — Form Input

**Task 3.1.1**
Buka `app/pages/prediction.py`. Tambahkan `st.set_page_config` identik dengan yang ada di `main.py` — ini diperlukan di setiap file halaman Streamlit multipage. Tambahkan import yang diperlukan.

Buat judul halaman "Single Customer Prediction" dan keterangan singkat. Gunakan `st.form` dengan `key="prediction_form"` untuk membungkus seluruh input field — ini memastikan semua input dikirim sekaligus saat tombol Submit ditekan, bukan satu per satu yang akan memicu re-render terus-menerus.

---

**Task 3.1.2**
Masih di `app/pages/prediction.py`, masih di dalam `st.form`. Bagi form menjadi tiga kolom horizontal menggunakan `st.columns(3)`. Distribusikan 20 field input ke dalam tiga kolom secara logis berdasarkan kelompoknya:

Kolom 1 — Demografi & Layanan Dasar: `gender` sebagai `st.selectbox` dengan opsi `["Male", "Female"]`, `SeniorCitizen` sebagai `st.selectbox` dengan opsi `[0, 1]` dan format display `"No (0)"/"Yes (1)"`, `Partner` sebagai `st.selectbox`, `Dependents` sebagai `st.selectbox`, `tenure` sebagai `st.slider` dengan range 1–72 dan default 12, `PhoneService` sebagai `st.selectbox`, `MultipleLines` sebagai `st.selectbox` dengan ketiga opsi termasuk `"No phone service"`.

Kolom 2 — Internet & Add-on: `InternetService` sebagai `st.selectbox` dengan opsi `["DSL", "Fiber optic", "No"]`. Enam kolom add-on (`OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`) masing-masing sebagai `st.selectbox` dengan opsi `["Yes", "No", "No internet service"]`.

Kolom 3 — Billing: `Contract` sebagai `st.selectbox` dengan opsi `["Month-to-month", "One year", "Two year"]`, `PaperlessBilling` sebagai `st.selectbox`, `PaymentMethod` sebagai `st.selectbox` dengan keempat opsi, `MonthlyCharges` sebagai `st.number_input` dengan `min_value=0.0`, `max_value=200.0`, `step=0.01`, default 65.0, `TotalCharges` sebagai `st.number_input` dengan `min_value=0.0`, default 1500.0.

Tambahkan `st.form_submit_button("Predict Churn", type="primary")` di bawah ketiga kolom, di luar kolom tapi masih di dalam form.

---

### Substep 3.2 — Hasil Prediksi

**Task 3.2.1**
Masih di `app/pages/prediction.py`, di luar blok `st.form`. Implementasikan logika yang dieksekusi saat form di-submit.

Ketika form di-submit: kumpulkan semua nilai form ke dalam dict dengan key sesuai nama kolom yang diharapkan API, panggil `predict_single` dari `api_client.py`, simpan hasilnya ke `st.session_state["last_prediction"]`. Jika response mengandung key `"error"`, tampilkan `st.error` dengan pesan error tersebut. Jika berhasil, lanjutkan ke rendering hasil.

Setelah form, cek apakah `st.session_state` mengandung `"last_prediction"` — jika iya, tampilkan section hasil. Ini memastikan hasil tetap terlihat meski user scroll atau klik widget lain di halaman.

---

**Task 3.2.2**
Masih di `app/pages/prediction.py`. Implementasikan rendering section hasil prediksi yang ditampilkan jika `"last_prediction"` ada di session state.

Section hasil harus berisi dua kolom: kolom kiri selebar 40% menampilkan `render_result_card` dengan data dari hasil prediksi. Kolom kanan selebar 60% menampilkan `render_shap_bar_chart` dengan `shap_values` dari hasil prediksi.

Di bawah kedua kolom, tambahkan `st.expander("See raw API response")` yang menampilkan seluruh response JSON dari API dalam format `st.json`. Ini berguna untuk portfolio — menunjukkan bahwa API response terstruktur dan transparan.

---

## STEP 4 — Halaman Batch Prediction (`app/pages/batch_prediction.py`)

### Substep 4.1 — Upload dan Preview

**Task 4.1.1**
Buka `app/pages/batch_prediction.py`. Tambahkan `st.set_page_config` identik dengan halaman lain. Tambahkan judul "Batch Customer Prediction" dan keterangan singkat yang menjelaskan format CSV yang diharapkan.

Implementasikan `st.file_uploader` dengan `type=["csv"]`, label "Upload CSV file", dan `help` text yang menyebutkan kolom apa yang wajib ada. Simpan file yang diupload ke `st.session_state["uploaded_file"]`.

---

**Task 4.1.2**
Masih di `app/pages/batch_prediction.py`. Jika file sudah diupload (ada di session state), baca konten CSV menggunakan `pd.read_csv` dan tampilkan preview menggunakan `st.dataframe` dengan `use_container_width=True` dan `height=200`. Tampilkan juga ringkasan: jumlah baris, jumlah kolom, dan daftar kolom yang terdeteksi.

Tambahkan tombol "Download Template CSV" yang memungkinkan user mengunduh CSV kosong dengan header kolom yang benar. Template CSV dibuat dari list nama kolom `CustomerInput` fields yang di-hardcode — bukan query ke API. Gunakan `st.download_button` dengan data berupa string CSV header dan `file_name="tccp_template.csv"`.

---

### Substep 4.2 — Eksekusi Batch dan Hasil

**Task 4.2.1**
Masih di `app/pages/batch_prediction.py`. Tambahkan tombol "Run Batch Prediction" yang hanya muncul jika file sudah diupload. Tombol ini tidak berada di dalam `st.form` — gunakan tombol biasa dengan kondisi `if st.button(...)`.

Ketika tombol ditekan: tampilkan `st.spinner("Running predictions...")` selama proses berlangsung, baca ulang konten file dari session state sebagai bytes, panggil `predict_batch_csv`, simpan hasilnya ke `st.session_state["batch_results"]`. Jika ada error, tampilkan `st.error`. Jika berhasil, lanjutkan ke rendering hasil.

---

**Task 4.2.2**
Masih di `app/pages/batch_prediction.py`. Implementasikan rendering hasil batch jika `"batch_results"` ada di session state.

Tampilkan metrik summary dalam tiga kolom: total pelanggan yang diprediksi, jumlah yang diprediksi churn (dimana `churn_prediction` adalah `True`), dan persentase churn rate dari batch tersebut. Gunakan `st.metric` untuk ketiga angka tersebut.

Di bawah metrik, konversi hasil batch menjadi DataFrame: setiap baris adalah satu pelanggan dengan kolom `index`, `churn_prediction`, `churn_probability` (dibulatkan 4 desimal), dan `risk_level`. Tampilkan DataFrame menggunakan `st.dataframe` dengan styling: baris dengan `risk_level == "high"` di-highlight merah, `"medium"` kuning, `"low"` hijau. Gunakan Pandas Styler untuk highlighting — bukan modifikasi data.

Tambahkan `st.download_button` yang memungkinkan user mengunduh DataFrame hasil sebagai CSV. Gunakan `df.to_csv(index=False).encode("utf-8")` sebagai data dan `file_name="tccp_predictions.csv"`.

---

## STEP 5 — Halaman Analytics (`app/pages/analytics.py`)

### Substep 5.1 — Model Information

**Task 5.1.1**
Buka `app/pages/analytics.py`. Tambahkan `st.set_page_config` identik dengan halaman lain. Tambahkan judul "Model Analytics & Insights" dan keterangan bahwa halaman ini menampilkan insight dari proses training dan analisis XAI.

Implementasikan section pertama: "Model Status". Panggil `check_health()` dan tampilkan informasi `model_version` dan `uptime_seconds` dari response. Format uptime dalam format yang mudah dibaca (jam:menit:detik). Jika API tidak tersedia, tampilkan pesan yang sesuai tapi jangan crash halaman.

---

### Substep 5.2 — XAI Visualizations

**Task 5.2.1**
Masih di `app/pages/analytics.py`. Implementasikan section "Global Feature Importance" menggunakan `st.tabs` dengan tiga tab: "SHAP Summary", "Permutation Importance", dan "Built-in Importance".

Untuk setiap tab: cek apakah file gambar yang relevan ada di `reports/xai_report/`. Jika ada, tampilkan gambar menggunakan `st.image` dengan `use_column_width=True` dan caption yang menjelaskan plot tersebut. Jika file tidak ada, tampilkan `st.info` dengan pesan bahwa file belum dihasilkan dan instruksi untuk menjalankan notebook XAI terlebih dahulu.

File yang dicek untuk masing-masing tab: tab SHAP mencari `reports/xai_report/shap_summary.png`, tab Permutation mencari `reports/xai_report/permutation_importance.png`, tab Built-in mencari file PNG apapun di `reports/xai_report/` yang mengandung kata `builtin` atau `feature_importance` dalam namanya.

Gunakan `pathlib.Path` untuk semua operasi cek file — jangan hardcode path string.

---

**Task 5.2.2**
Masih di `app/pages/analytics.py`. Implementasikan section "SHAP Force Plot" menggunakan `st.expander` dengan label "SHAP Force Plot (HTML)". Di dalam expander: cek apakah `reports/xai_report/shap_force_plot.html` ada. Jika ada, baca kontennya sebagai string dan tampilkan menggunakan `st.components.v1.html` dengan `height=200`. Jika tidak ada, tampilkan `st.info` yang sesuai.

---

### Substep 5.3 — Live Distribution dari Batch

**Task 5.3.1**
Masih di `app/pages/analytics.py`. Implementasikan section "Batch Prediction Distribution" yang menampilkan analisis dari hasil batch terakhir jika ada di session state (`st.session_state.get("batch_results")`).

Jika ada hasil batch di session state: konversi ke DataFrame, tampilkan tiga visualisasi dalam tiga kolom: pie chart distribusi `risk_level` (high/medium/low), histogram `churn_probability` dengan 20 bins, dan bar chart jumlah prediksi per `risk_level`. Gunakan `matplotlib` untuk semua chart dan tampilkan via `st.pyplot`. Pastikan semua figure di-close setelah ditampilkan.

Jika tidak ada hasil batch di session state: tampilkan `st.info` yang menginstruksikan user untuk terlebih dahulu menjalankan batch prediction di halaman Batch Prediction.

---

## STEP 6 — Verifikasi DEV-03

### Substep 6.1 — Verifikasi Startup

**Task 6.1.1**
Pastikan FastAPI (DEV-02) sedang berjalan di port 8000. Set environment variable `API_BASE_URL=http://localhost:8000`. Jalankan Streamlit dengan perintah `streamlit run app/main.py --server.port 8501` dari root project. Verifikasi bahwa tidak ada error saat startup di terminal. Buka `http://localhost:8501` di browser dan verifikasi halaman home tampil. Verifikasi bahwa sidebar menampilkan status API "🟢 API Connected" beserta model version. Report apakah ada error.

---

**Task 6.1.2**
Navigasi ke halaman Single Prediction. Verifikasi bahwa semua 20 field input tampil terbagi dalam tiga kolom. Verifikasi bahwa semua selectbox memiliki opsi yang benar — spot check minimal tiga field: `Contract`, `MultipleLines`, dan `InternetService`. Isi form dengan nilai apapun dan klik Submit. Verifikasi bahwa hasil prediksi muncul di bawah form tanpa halaman refresh penuh. Verifikasi bahwa `result_card` menampilkan risk level badge, persentase probability, dan label churn/no-churn. Verifikasi bahwa SHAP bar chart muncul dengan label fitur yang terbaca. Report apakah semua komponen tampil benar.

---

**Task 6.1.3**
Navigasi ke halaman Batch Prediction. Klik "Download Template CSV" dan verifikasi file ter-download dengan header yang benar. Buat CSV kecil (5 baris) menggunakan template tersebut, upload ke halaman, dan verifikasi preview DataFrame tampil. Klik "Run Batch Prediction" dan verifikasi tiga metrik summary muncul beserta DataFrame hasil dengan warna highlight. Klik "Download Results" dan verifikasi file CSV ter-download. Report apakah semua step berjalan benar.

---

**Task 6.1.4**
Navigasi ke halaman Analytics. Verifikasi section Model Status menampilkan model version dan uptime. Verifikasi section Feature Importance menampilkan gambar jika file ada di `reports/xai_report/`, atau pesan info jika tidak ada. Kembali ke halaman Batch Prediction, jalankan batch prediction, kemudian kembali ke Analytics — verifikasi section "Batch Prediction Distribution" sekarang menampilkan tiga chart. Report apakah semua section tampil benar.

---

**Task 6.1.5**
Uji kondisi API tidak tersedia: hentikan FastAPI, kemudian reload halaman Streamlit. Verifikasi bahwa sidebar menampilkan "🔴 API Unreachable" bukan error Python. Verifikasi bahwa halaman Analytics tetap bisa diakses dan menampilkan konten statis (file gambar) meski API mati. Verifikasi bahwa mencoba submit form di halaman Prediction menghasilkan pesan error yang terbaca, bukan exception traceback. Report hasilnya.

---

## DEV-03 COMPLETE

Setelah Task 6.1.5 selesai tanpa temuan yang tidak terduga, DEV-03 selesai.

Informasikan ke user: "DEV-03 complete. Streamlit UI berjalan di port 8501 dengan tiga halaman terverifikasi. Single prediction, batch prediction via CSV, dan analytics dengan XAI visualizations semua berfungsi. Graceful degradation saat API tidak tersedia dikonfirmasi. Siap untuk DEV-04 (Testing Suite) dan DEV-05 (Dockerization)."

---

## RINGKASAN DEV-03

| Step | Substep | Task | File |
|---|---|---|---|
| Step 1 — Shared Components | 1.1 | 1.1.1, 1.1.2, 1.1.3 | `app/components/api_client.py` |
| | 1.2 | 1.2.1 | `app/components/result_card.py` |
| | 1.3 | 1.3.1 | `app/components/shap_chart.py` |
| Step 2 — Entry Point | 2.1 | 2.1.1, 2.1.2, 2.1.3 | `app/main.py` |
| Step 3 — Single Prediction | 3.1 | 3.1.1, 3.1.2 | `app/pages/prediction.py` |
| | 3.2 | 3.2.1, 3.2.2 | `app/pages/prediction.py` |
| Step 4 — Batch Prediction | 4.1 | 4.1.1, 4.1.2 | `app/pages/batch_prediction.py` |
| | 4.2 | 4.2.1, 4.2.2 | `app/pages/batch_prediction.py` |
| Step 5 — Analytics | 5.1 | 5.1.1 | `app/pages/analytics.py` |
| | 5.2 | 5.2.1, 5.2.2 | `app/pages/analytics.py` |
| | 5.3 | 5.3.1 | `app/pages/analytics.py` |
| Step 6 — Verifikasi | 6.1 | 6.1.1, 6.1.2, 6.1.3, 6.1.4, 6.1.5 | — |
| **Total** | **12 substep** | **20 task** | **7 file** |
