# TCCP Deployment — Development Instructions
## DEV-04: Testing Suite

---

## WHAT THIS PHASE COVERS

DEV-04 mengimplementasikan seluruh test suite yang menjadi penjaga kualitas pipeline CI/CD. Phase ini mencakup satu file `conftest.py` berisi shared fixtures, tiga file unit test (`test_preprocessing.py`, `test_metrics.py`, `test_xai_validator.py`), dan satu file integration test (`test_api.py`).

Unit test menguji komponen `src/` secara terisolasi tanpa membutuhkan model artifact yang besar. Integration test menguji seluruh alur endpoint FastAPI menggunakan `TestClient` dan dummy model yang di-inject melalui fixture — tidak membutuhkan server yang berjalan dan tidak membutuhkan `model_final.joblib` yang nyata.

Prinsip utama phase ini: setiap test harus bisa lulus di CI environment yang bersih tanpa file eksternal besar, tanpa koneksi ke WandB, dan tanpa API server yang berjalan terpisah.

DEV-04 bisa dikerjakan paralel dengan DEV-02 dan DEV-03 setelah DEV-01 selesai. Test ditulis berdasarkan interface yang disepakati — test yang gagal sebelum implementasi ada adalah perilaku yang diharapkan. CI hanya dijalankan setelah semua implementasi selesai.

---

## BEFORE YOU START THIS PHASE

Baca file berikut secara penuh sebelum mengeksekusi task apapun di phase ini.

**Required reading:**
- `churn-doc1-project-overview.md` — Section 6.1 (Raw Data Schema): catat semua kolom dan nilai valid, karena fixture data sintetis harus mengikuti schema ini. Section 8 (Global ML Principles): pahami prinsip no data leakage dan training-serving parity — prinsip ini yang diverifikasi oleh unit test preprocessing.
- `api/schemas.py` (hasil DEV-02): baca seluruh file. Integration test mem-parse response berdasarkan schema ini.
- `config/settings.py` (hasil DEV-01): catat `EXPECTED_IMPORTANT_FEATURES`, `XAI_TOP_N_FEATURES`, dan `XAI_MIN_OVERLAP` — ketiga konstanta ini adalah input langsung untuk test `xai_validator`.

After reading, confirm with: "Reference files read. Ready to execute DEV-04."
Then wait for user instruction to begin.

---

## EXECUTION RULES FOR THIS PHASE

- Execute one task at a time.
- After completing each task, report what was done and wait for the user to say "next" or give a correction.
- Do not move to the next task unless the user explicitly confirms.
- Semua path file relatif terhadap root project.
- Tidak ada test yang boleh bergantung pada file `model_final.joblib` atau `preprocessor.joblib` yang nyata. Semua dependency pada model dan preprocessor harus dipenuhi melalui fixture.
- Tidak ada test yang boleh melakukan koneksi jaringan ke WandB, HuggingFace, atau API eksternal manapun.
- Setiap test harus bisa dijalankan secara independen — tidak ada test yang bergantung pada state yang ditinggalkan oleh test sebelumnya.
- Gunakan nama test yang deskriptif: pola `test_<apa_yang_diuji>_<kondisi>_<hasil_yang_diharapkan>`. Contoh: `test_encoder_no_internet_value_encoded_differently_from_no`.

---

## STEP 1 — Konfigurasi pytest dan Shared Fixtures

### Substep 1.1 — pytest Configuration

**Task 1.1.1**
Buat file `pytest.ini` di root project. Isi dengan konfigurasi berikut: `testpaths` menunjuk ke `tests/`, `python_files` dengan pola `test_*.py`, `python_classes` dengan pola `Test*`, `python_functions` dengan pola `test_*`. Tambahkan `addopts` dengan flag `--tb=short` untuk output traceback yang ringkas di CI, dan `-v` untuk verbose output. Tambahkan marker definitions: `unit` untuk test yang tidak butuh I/O eksternal, dan `integration` untuk test yang membutuhkan FastAPI TestClient.

---

### Substep 1.2 — Root conftest.py

**Task 1.2.1**
Buat file `tests/conftest.py`. File ini berisi fixtures yang tersedia untuk semua test di seluruh suite — baik unit maupun integration.

Implementasikan fixture `sample_raw_row` dengan scope `function`. Fixture ini mengembalikan satu dict yang merepresentasikan satu baris data pelanggan yang valid sesuai raw data schema. Gunakan nilai yang secara bisnis masuk akal: pelanggan dengan `Contract = "Month-to-month"`, `tenure = 3`, `InternetService = "Fiber optic"`, `MonthlyCharges = 85.5`, `TotalCharges = 256.5`, semua add-on bernilai `"No"`, `MultipleLines = "No"`, `PhoneService = "Yes"`, `PaymentMethod = "Electronic check"`, `PaperlessBilling = "Yes"`, `SeniorCitizen = 0`, `gender = "Male"`, `Partner = "No"`, `Dependents = "No"`. Ini adalah profil pelanggan berisiko tinggi churn.

---

**Task 1.2.2**
Masih di `tests/conftest.py`. Implementasikan fixture `sample_raw_df` dengan scope `function`. Fixture ini mengembalikan `pd.DataFrame` berisi 20 baris data sintetis yang valid. DataFrame ini dibuat secara programatik — bukan di-load dari file. Konstruksi DataFrame harus mencakup variasi nilai yang realistis: campuran pelanggan dengan `InternetService = "No"` (sehingga add-on bernilai `"No internet service"`), pelanggan dengan `PhoneService = "No"` (sehingga `MultipleLines = "No phone service"`), berbagai nilai `Contract`, dan `tenure` yang bervariasi dari 1 hingga 72. Distribusi Churn label (kolom `Churn`) harus mengandung minimal 5 baris `"Yes"` dan minimal 10 baris `"No"` untuk mencerminkan class imbalance yang realistis.

---

**Task 1.2.3**
Masih di `tests/conftest.py`. Implementasikan fixture `dummy_preprocessor` dengan scope `session` — dibuat sekali dan digunakan ulang oleh semua test yang membutuhkannya. Fixture ini membangun dan melakukan `fit_transform` pada `sample_raw_df` menggunakan pipeline preprocessing dari `src/preprocessing/pipeline.py`. Hasilnya adalah objek preprocessor yang sudah di-fit dan siap digunakan untuk `transform`.

Jika `src/preprocessing/pipeline.py` belum diimplementasikan saat test dijalankan, fixture ini akan gagal — ini adalah perilaku yang diharapkan dan menandakan bahwa implementasi belum siap untuk ditest. Jangan buat workaround dengan hardcode pipeline di dalam fixture.

---

**Task 1.2.4**
Masih di `tests/conftest.py`. Implementasikan fixture `dummy_model` dengan scope `session`. Fixture ini melatih model `LogisticRegression` yang sangat sederhana pada data sintetis kecil yang dibuat secara in-memory — bukan membaca dari file artifact. Data sintetis yang digunakan harus memiliki jumlah fitur yang sama dengan output `dummy_preprocessor`. Oleh karena itu, fixture ini bergantung pada `dummy_preprocessor`: gunakan `dummy_preprocessor.transform(sample_raw_df)` untuk mendapatkan X, buat y sintetis yang sesuai, kemudian fit `LogisticRegression(random_state=42)`. Model yang dihasilkan harus memiliki method `predict_proba` — ini yang diverifikasi oleh integration test.

---

**Task 1.2.5**
Masih di `tests/conftest.py`. Implementasikan fixture `api_client` dengan scope `function`. Fixture ini menyiapkan FastAPI `TestClient` dengan dummy model dan preprocessor yang sudah di-inject. Langkah-langkahnya: import `predictor` singleton dari `api.predictor`, gunakan `unittest.mock.patch.object` atau langsung set atribut `predictor._model`, `predictor._preprocessor`, `predictor._is_ready`, dan `predictor._model_version` dengan nilai dari fixture `dummy_model` dan `dummy_preprocessor`. Setelah setup, buat `TestClient(app)` dari `api.main` dan yield client-nya. Setelah test selesai (bagian setelah yield), reset semua atribut predictor kembali ke nilai default-nya (`None`, `None`, `False`, `"unknown"`) untuk menghindari interferensi antar test.

---

## STEP 2 — Unit Test: Preprocessing (`tests/unit/test_preprocessing.py`)

### Substep 2.1 — Test Custom Encoder

**Task 2.1.1**
Buka `tests/unit/test_preprocessing.py`. Tambahkan import yang diperlukan dan mark seluruh modul dengan `@pytest.mark.unit`.

Implementasikan test class `TestStructuralEncoder` yang menguji perilaku custom encoder di `src/preprocessing/encoders.py`. Encoder ini bertanggung jawab menangani nilai `"No internet service"` dan `"No phone service"` agar tidak di-encode sama dengan `"No"` biasa.

Tulis test `test_no_internet_service_encoded_differently_from_no`: buat dua DataFrame identik kecuali satu kolom add-on — satu bernilai `"No"` dan satu bernilai `"No internet service"`. Setelah transform, verifikasi bahwa encoded value dari kedua nilai ini berbeda.

Tulis test `test_no_phone_service_encoded_differently_from_no`: logika identik untuk `MultipleLines` dengan nilai `"No"` vs `"No phone service"`.

Tulis test `test_encoder_only_fit_on_training_data`: fit encoder pada data training kecil, kemudian transform data test yang mengandung nilai yang belum pernah ada di training. Verifikasi bahwa transform tidak crash dan menghasilkan output dengan dimensi yang konsisten.

---

**Task 2.1.2**
Masih di `tests/unit/test_preprocessing.py`. Implementasikan test class `TestFeatureEngineering` yang menguji transformer di `src/preprocessing/feature_engineering.py`.

Tulis test `test_tc_residual_is_difference_from_expected`: buat row dengan `TotalCharges = 300.0`, `tenure = 3`, `MonthlyCharges = 90.0`. Nilai `tc_residual` yang diharapkan adalah `300.0 - (3 × 90.0) = 30.0`. Verifikasi hasil sesuai dengan toleransi floating point.

Tulis test `test_monthly_to_total_ratio_computed_correctly`: buat row dengan `MonthlyCharges = 80.0`, `TotalCharges = 400.0`. Ratio yang diharapkan adalah `80.0 / 400.0 = 0.2`. Verifikasi hasil.

Tulis test `test_tenure_group_uses_correct_boundaries`: buat beberapa baris dengan tenure yang berada di berbagai posisi relatif terhadap boundaries `[0, 2, 18, 44, 72]`. Verifikasi bahwa `tenure = 1` masuk grup pertama, `tenure = 10` masuk grup kedua, `tenure = 30` masuk grup ketiga, dan `tenure = 60` masuk grup keempat. Grup didefinisikan oleh boundaries ini — test mengverifikasi bahwa pembagiannya sesuai.

Tulis test `test_service_count_counts_only_active_addons`: buat row dengan 3 add-on bernilai `"Yes"`, 2 bernilai `"No"`, dan 1 bernilai `"No internet service"`. Nilai `service_count` yang diharapkan adalah 3 — hanya yang aktif (`"Yes"`) yang dihitung.

Tulis test `test_is_auto_payment_true_for_automatic_methods`: verifikasi bahwa `"Bank transfer (automatic)"` dan `"Credit card (automatic)"` menghasilkan `is_auto_payment = 1`, sementara `"Electronic check"` dan `"Mailed check"` menghasilkan `is_auto_payment = 0`.

---

### Substep 2.2 — Test Pipeline Serialization

**Task 2.2.1**
Masih di `tests/unit/test_preprocessing.py`. Implementasikan test class `TestPipelineSerialization` yang menguji prinsip training-serving parity.

Tulis test `test_pipeline_output_consistent_after_joblib_roundtrip`: fit pipeline pada `sample_raw_df`, jalankan `transform` dan simpan hasilnya sebagai `output_before`. Serialize pipeline menggunakan `joblib.dump` ke file temporary (`tmp_path` dari pytest), load kembali dengan `joblib.load`, jalankan `transform` lagi pada data yang sama, simpan hasilnya sebagai `output_after`. Verifikasi bahwa `output_before` dan `output_after` identik menggunakan `numpy.testing.assert_array_almost_equal`. Hapus file temporary setelah test selesai — gunakan `tmp_path` fixture dari pytest yang otomatis cleanup.

Tulis test `test_pipeline_transform_produces_no_nan`: fit pipeline pada `sample_raw_df`, transform data yang sama, verifikasi bahwa output tidak mengandung NaN apapun menggunakan `numpy.isnan(output).any()`.

Tulis test `test_pipeline_fit_and_transform_produce_same_shape`: `fit_transform` menghasilkan array dengan shape tertentu. `transform` pada data baru dengan jumlah baris berbeda harus menghasilkan array dengan jumlah kolom yang sama. Verifikasi `n_columns` konsisten antara keduanya.

---

## STEP 3 — Unit Test: Metrics (`tests/unit/test_metrics.py`)

### Substep 3.1 — Test Kalkulasi Metric

**Task 3.1.1**
Buka `tests/unit/test_metrics.py`. Tambahkan import yang diperlukan dan mark seluruh modul dengan `@pytest.mark.unit`.

Implementasikan test class `TestMetricCalculations` yang menguji fungsi-fungsi di `src/evaluation/metrics.py`. Setiap test menggunakan `y_true` dan `y_pred` atau `y_prob` yang sudah diketahui nilai metricnya secara eksak.

Tulis test `test_perfect_prediction_yields_all_ones`: buat `y_true = [1, 1, 0, 0, 1]` dan `y_pred` yang identik dengan `y_true`. Verifikasi bahwa precision, recall, dan F1 semuanya bernilai 1.0. Verifikasi bahwa ROC-AUC bernilai 1.0.

Tulis test `test_all_wrong_prediction_yields_zero_metrics`: buat `y_true = [1, 1, 0, 0]` dan `y_pred = [0, 0, 1, 1]` (semua terbalik). Verifikasi bahwa precision dan recall bernilai 0.0.

Tulis test `test_roc_auc_random_prediction_near_0_5`: buat `y_true` dan `y_prob` yang tidak berkorelasi sama sekali (probability random). Verifikasi bahwa ROC-AUC yang dihasilkan berada dalam range [0.3, 0.7] — tidak perlu tepat 0.5, hanya verifikasi bahwa fungsinya berjalan dan menghasilkan nilai dalam range yang masuk akal.

Tulis test `test_metric_function_returns_dict_with_required_keys`: panggil fungsi utama kalkulasi metric dari `src/evaluation/metrics.py` dengan data dummy. Verifikasi bahwa return value adalah dict dan mengandung setidaknya key berikut: `precision`, `recall`, `f1`, `roc_auc`, `pr_auc`.

---

**Task 3.1.2**
Masih di `tests/unit/test_metrics.py`. Implementasikan test untuk PR-AUC secara terpisah karena metric ini lebih sensitif terhadap class imbalance.

Tulis test `test_pr_auc_reflects_class_distribution`: buat dua skenario. Skenario A: model yang bisa membedakan positif dan negatif dengan sempurna. Skenario B: model yang selalu memprediksi probabilitas random. Verifikasi bahwa PR-AUC skenario A lebih tinggi dari skenario B.

Tulis test `test_classification_threshold_affects_precision_recall_tradeoff`: gunakan satu set `y_prob` yang sama, hitung metric pada threshold 0.3 dan threshold 0.7. Verifikasi bahwa threshold lebih rendah menghasilkan recall lebih tinggi tapi precision lebih rendah, dan sebaliknya. Ini memverifikasi bahwa fungsi kalkulasi metric mendukung custom threshold.

---

## STEP 4 — Unit Test: XAI Validator (`tests/unit/test_xai_validator.py`)

### Substep 4.1 — Test Quality Gate Logic

**Task 4.1.1**
Buka `tests/unit/test_xai_validator.py`. Tambahkan import yang diperlukan termasuk konstanta `EXPECTED_IMPORTANT_FEATURES`, `XAI_TOP_N_FEATURES`, dan `XAI_MIN_OVERLAP` dari `config/settings.py`. Mark seluruh modul dengan `@pytest.mark.unit`.

Implementasikan helper function `build_mock_shap_values` di dalam file test ini — bukan di conftest karena spesifik untuk XAI test saja. Fungsi ini menerima `top_features` (list nama fitur yang ingin memiliki SHAP value tinggi) dan `other_features` (list nama fitur dengan SHAP value rendah), dan mengembalikan dict `{feature_name: shap_value}`. Fitur dalam `top_features` mendapat nilai antara 0.5 dan 1.0, fitur dalam `other_features` mendapat nilai antara 0.01 dan 0.1.

---

**Task 4.1.2**
Masih di `tests/unit/test_xai_validator.py`. Implementasikan test class `TestXAIValidatorPass`.

Tulis test `test_model_passes_when_all_expected_features_in_top_n`: bangun mock SHAP values di mana semua 5 fitur dari `EXPECTED_IMPORTANT_FEATURES` masuk ke top-10. Panggil fungsi validator dari `src/xai/xai_validator.py`. Verifikasi hasilnya `True`.

Tulis test `test_model_passes_at_exact_minimum_overlap`: bangun SHAP values di mana tepat 3 dari 5 expected features masuk top-10 (50% overlap = tepat di threshold `XAI_MIN_OVERLAP = 0.5`). Verifikasi hasilnya `True` — tepat di threshold harus lulus.

Tulis test `test_validator_returns_bool_not_none`: verifikasi bahwa return value fungsi validator adalah `bool` (`True` atau `False`), bukan `None`, bukan integer, bukan float.

---

**Task 4.1.3**
Masih di `tests/unit/test_xai_validator.py`. Implementasikan test class `TestXAIValidatorFail`.

Tulis test `test_model_fails_when_no_expected_features_in_top_n`: bangun SHAP values di mana tidak satupun dari `EXPECTED_IMPORTANT_FEATURES` masuk top-10 — fitur lain yang tidak relevan secara bisnis mendominasi. Verifikasi hasilnya `False`.

Tulis test `test_model_fails_below_minimum_overlap`: bangun SHAP values di mana hanya 2 dari 5 expected features masuk top-10 (40% overlap, di bawah threshold 50%). Verifikasi hasilnya `False`.

Tulis test `test_validator_message_indicates_which_features_missing`: jika fungsi validator mendukung return detail (misal return tuple `(bool, dict)`) atau menyimpan hasil ke atribut, verifikasi bahwa informasi tentang fitur mana yang masuk dan tidak masuk bisa diakses. Jika fungsi hanya return `bool`, verifikasi bahwa minimal log atau print output tersedia — cek menggunakan `caplog` pytest fixture.

---

**Task 4.1.4**
Masih di `tests/unit/test_xai_validator.py`. Implementasikan test class `TestXAIValidatorEdgeCases`.

Tulis test `test_validator_with_custom_top_n`: panggil validator dengan `top_n = 5` alih-alih default 10. Bangun SHAP values di mana expected features ada di posisi 1-5 tapi tidak di posisi 6-10. Verifikasi hasilnya `True` dengan top_n=5 dan `False` jika dipaksa menggunakan top_n=3 dan tidak semua expected features masuk top-3.

Tulis test `test_validator_with_custom_min_overlap`: panggil validator dengan `min_overlap = 1.0` (semua expected features harus ada di top-N). Bangun SHAP values di mana hanya 4 dari 5 yang masuk. Verifikasi hasilnya `False` dengan min_overlap=1.0 tapi `True` dengan min_overlap=0.5.

---

## STEP 5 — Integration Test: API (`tests/integration/test_api.py`)

### Substep 5.1 — Setup dan Test Endpoint Dasar

**Task 5.1.1**
Buka `tests/integration/test_api.py`. Tambahkan import yang diperlukan: `pytest`, `TestClient` dari `fastapi.testclient`, `app` dari `api.main`. Mark seluruh modul dengan `@pytest.mark.integration`. Semua test class di file ini menerima `api_client` fixture dari `tests/conftest.py`.

Implementasikan test class `TestBaseEndpoints`.

Tulis test `test_root_endpoint_returns_200_with_navigation_info`: kirim `GET /`. Verifikasi status code 200. Verifikasi response JSON mengandung key `docs` dan `health`.

Tulis test `test_health_endpoint_returns_healthy_when_model_loaded`: kirim `GET /health`. Verifikasi status code 200. Verifikasi `model_loaded` bernilai `True`. Verifikasi `status` bernilai `"healthy"`. Verifikasi `uptime_seconds` bertipe float dan nilainya lebih dari 0.

---

**Task 5.1.2**
Masih di `tests/integration/test_api.py`. Implementasikan test class `TestHealthDegraded`. Test class ini menggunakan fixture yang berbeda: bukan `api_client` biasa, tapi versi di mana `predictor._is_ready = False` untuk mensimulasikan kondisi model tidak berhasil di-load.

Buat fixture lokal `degraded_api_client` di dalam file ini (scope `function`) yang mengikuti pola yang sama dengan `api_client` di conftest tapi set `predictor._is_ready = False`.

Tulis test `test_health_returns_degraded_when_model_not_loaded`: kirim `GET /health` menggunakan `degraded_api_client`. Verifikasi status code tetap 200 (bukan 503). Verifikasi `status` bernilai `"degraded"`. Verifikasi `model_loaded` bernilai `False`.

---

### Substep 5.2 — Test Endpoint Predict

**Task 5.2.1**
Masih di `tests/integration/test_api.py`. Implementasikan test class `TestPredictEndpoint`.

Tulis test `test_predict_returns_200_with_valid_input`: kirim `POST /predict` dengan `sample_raw_row` dari conftest. Verifikasi status code 200. Verifikasi response mengandung key `status`, `model_version`, dan `result`. Verifikasi `result` mengandung `churn_prediction` (bool), `churn_probability` (float antara 0 dan 1), dan `risk_level` (salah satu dari `"high"`, `"medium"`, `"low"`).

Tulis test `test_predict_shap_values_present_and_dict`: kirim `POST /predict` dengan input valid. Verifikasi bahwa `result.shap_values` bukan `null` dan bertipe dict. Verifikasi bahwa setiap key dalam dict adalah string dan setiap value adalah float.

Tulis test `test_predict_returns_422_for_invalid_tenure`: kirim `POST /predict` dengan `tenure = 999` (di luar range 1–72). Verifikasi status code 422. Verifikasi response body mengandung informasi tentang field `tenure`.

Tulis test `test_predict_returns_422_for_invalid_contract_value`: kirim `POST /predict` dengan `Contract = "Weekly"` (nilai tidak valid). Verifikasi status code 422.

Tulis test `test_predict_returns_422_for_missing_required_field`: kirim `POST /predict` dengan body yang tidak mengandung field `MonthlyCharges`. Verifikasi status code 422.

---

**Task 5.2.2**
Masih di `tests/integration/test_api.py`. Implementasikan test class `TestPredictWhenModelNotReady`. Gunakan `degraded_api_client` fixture dari Task 5.1.2.

Tulis test `test_predict_returns_503_when_model_not_loaded`: kirim `POST /predict` dengan input valid menggunakan `degraded_api_client`. Verifikasi status code 503. Verifikasi response body mengandung pesan yang menjelaskan bahwa model belum siap.

---

### Substep 5.3 — Test Endpoint Batch Predict

**Task 5.3.1**
Masih di `tests/integration/test_api.py`. Implementasikan test class `TestBatchPredictEndpoint`.

Tulis test `test_batch_predict_returns_correct_count`: buat list 5 customer input yang valid. Kirim `POST /predict/batch`. Verifikasi status code 200. Verifikasi `total_input` bernilai 5. Verifikasi `results` berisi 5 item. Verifikasi setiap item memiliki `index` dari 0 sampai 4 secara berurutan. Verifikasi `shap_values` adalah `null` untuk semua item dalam batch.

Tulis test `test_batch_predict_returns_422_for_empty_list`: kirim `POST /predict/batch` dengan list kosong `[]`. Verifikasi status code 422.

Tulis test `test_batch_predict_returns_422_when_exceeding_limit`: buat list berisi 1001 customer input (di atas batas 1000). Kirim `POST /predict/batch`. Verifikasi status code 422. Untuk membuat 1001 item secara efisien, gunakan `[sample_raw_row] * 1001` — `sample_raw_row` dari conftest adalah dict yang bisa di-multiply.

---

**Task 5.3.2**
Masih di `tests/integration/test_api.py`. Implementasikan test class `TestBatchCsvEndpoint`.

Tulis test `test_batch_csv_returns_200_with_valid_csv`: buat konten CSV valid menggunakan `sample_raw_df` dari conftest — konversi ke string CSV menggunakan `df.to_csv(index=False)`. Kirim ke `POST /predict/batch-csv` menggunakan parameter `files` dari httpx — format `{"file": ("test.csv", csv_string.encode(), "text/csv")}`. Verifikasi status code 200. Verifikasi `total_input` sesuai jumlah baris CSV.

Tulis test `test_batch_csv_returns_422_for_non_csv_file`: kirim file dengan nama `test.json` dan konten sembarang. Verifikasi status code 422.

Tulis test `test_batch_csv_returns_422_when_required_column_missing`: buat CSV yang tidak memiliki kolom `Contract`. Kirim ke endpoint. Verifikasi status code 422. Verifikasi response body menyebutkan nama kolom yang hilang.

Tulis test `test_batch_csv_drops_id_and_churn_columns_if_present`: buat CSV yang mengandung kolom `id` dan `Churn` tambahan (selain 20 kolom input). Kirim ke endpoint. Verifikasi bahwa API tidak mengembalikan error karena kolom tersebut — kolom ekstra ini harus di-drop secara otomatis oleh endpoint sebelum diproses.

---

## STEP 6 — Verifikasi DEV-04

### Substep 6.1 — Jalankan Unit Tests

**Task 6.1.1**
Dari root project, jalankan perintah `pytest tests/unit/ -v --tb=short`. Verifikasi bahwa semua test di tiga file unit test dapat ditemukan oleh pytest — jumlah test yang terkumpul (collected) harus sesuai dengan jumlah test yang ditulis. Jika ada `ImportError` atau `ModuleNotFoundError`, laporkan pesan error lengkapnya — ini kemungkinan menandakan implementasi di `src/` belum selesai atau import path salah.

Report: berapa test yang `PASSED`, berapa yang `FAILED`, berapa yang `ERROR`, dan berapa yang `SKIPPED`.

---

**Task 6.1.2**
Jalankan hanya test preprocessing dengan perintah `pytest tests/unit/test_preprocessing.py -v`. Jika ada test yang fail, laporkan nama test dan pesan assertion error-nya secara lengkap. Jangan lanjutkan ke task berikutnya sebelum laporan diberikan — test failure di sini bisa mengindikasikan bug di implementasi preprocessing yang perlu diperbaiki sebelum CI dikonfigurasi.

---

**Task 6.1.3**
Jalankan integration test dengan perintah `pytest tests/integration/ -v --tb=short`. Verifikasi bahwa fixture `api_client` berhasil di-setup tanpa error. Report: berapa test `PASSED`, berapa yang `FAILED`, dan pesan lengkap untuk setiap yang `FAILED`.

---

### Substep 6.2 — Jalankan Full Suite dengan Coverage

**Task 6.2.1**
Jalankan seluruh test suite dengan coverage report menggunakan perintah `pytest tests/ --cov=src --cov=api --cov-report=term-missing`. Verifikasi bahwa coverage keseluruhan untuk `api/` mencapai minimal 70% — ini adalah threshold minimum yang akan digunakan di CI. Verifikasi bahwa `api/predictor.py` dan `api/main.py` memiliki coverage masing-masing minimal 60%. Report output coverage report lengkapnya.

---

**Task 6.2.2**
Verifikasi bahwa perintah `pytest tests/ -m unit` hanya menjalankan test yang di-mark `unit`, dan `pytest tests/ -m integration` hanya menjalankan test yang di-mark `integration`. Report jumlah test yang terkumpul untuk masing-masing perintah — ini memverifikasi bahwa marker registration di `pytest.ini` berfungsi benar dan akan digunakan oleh CI workflow di DEV-07.

---

## DEV-04 COMPLETE

Setelah Task 6.2.2 selesai dan semua test lulus, DEV-04 selesai.

Informasikan ke user: "DEV-04 complete. Test suite terdiri dari [N] unit tests dan [M] integration tests. Coverage api/ mencapai [X]%. Marker `unit` dan `integration` berfungsi untuk selective test execution di CI. Siap untuk DEV-05 (Dockerization)."

---

## RINGKASAN DEV-04

| Step | Substep | Task | File |
|---|---|---|---|
| Step 1 — Setup | 1.1 | 1.1.1 | `pytest.ini` |
| | 1.2 | 1.2.1, 1.2.2, 1.2.3, 1.2.4, 1.2.5 | `tests/conftest.py` |
| Step 2 — Unit: Preprocessing | 2.1 | 2.1.1, 2.1.2 | `tests/unit/test_preprocessing.py` |
| | 2.2 | 2.2.1 | `tests/unit/test_preprocessing.py` |
| Step 3 — Unit: Metrics | 3.1 | 3.1.1, 3.1.2 | `tests/unit/test_metrics.py` |
| Step 4 — Unit: XAI Validator | 4.1 | 4.1.1, 4.1.2, 4.1.3, 4.1.4 | `tests/unit/test_xai_validator.py` |
| Step 5 — Integration: API | 5.1 | 5.1.1, 5.1.2 | `tests/integration/test_api.py` |
| | 5.2 | 5.2.1, 5.2.2 | `tests/integration/test_api.py` |
| | 5.3 | 5.3.1, 5.3.2 | `tests/integration/test_api.py` |
| Step 6 — Verifikasi | 6.1 | 6.1.1, 6.1.2, 6.1.3 | — |
| | 6.2 | 6.2.1, 6.2.2 | — |
| **Total** | **11 substep** | **22 task** | **3 file baru + 1 config** |
