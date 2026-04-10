Tampilkan 8 prinsip ML global project TCCP berikut sebagai pengingat.
Prinsip-prinsip ini berlaku untuk seluruh codebase dan tidak boleh dilanggar.

---

**TCCP — Global ML Principles**

**8.1 No Data Leakage**
Semua operasi fit (encoder, scaler, imputer) hanya boleh dilakukan pada training data.
Validation set dan test set hanya boleh di-transform menggunakan parameter yang sudah di-fit dari training data.
Pelanggaran prinsip ini menghasilkan metric yang optimis palsu.

**8.2 Preprocessing Consistency (Training-Serving Parity)**
Pipeline preprocessing yang di-fit saat training harus identik dengan yang digunakan saat inference.
Cara menjaminnya: save `preprocessor.joblib` setelah fit, load kembali saat inference.
Jangan menulis ulang logika preprocessing di `api/predictor.py` — selalu load dari artifact.

**8.3 Reproducibility**
Semua random operation harus menggunakan seed yang terdefinisi di `config/settings.py`.
Ini mencakup: train/val/test split, inisialisasi model, dan hyperparameter search.
Konstanta: `RANDOM_SEED = 42` — selalu import dari settings, tidak pernah hardcode.

**8.4 Experiment Tracking Wajib**
Setiap training run — termasuk eksperimen awal — harus di-log ke wandb.
Minimum yang di-log: semua hyperparameter, semua metric evaluasi, path artifact model.
Tidak ada "quick run" yang tidak di-log.

**8.5 Model Selection Berbasis EDA**
Pemilihan arsitektur model tidak dilakukan sebelum EDA selesai.
EDA menghasilkan kesimpulan tentang distribusi fitur, korelasi, missing values, outlier.
Kesimpulan EDA menjadi input untuk pemilihan kandidat model.

**8.6 XAI sebagai Quality Gate — bukan hanya Interpretasi**
XAI dijalankan setelah base model training dan setelah hyperparameter tuning.
Model hanya dilanjutkan jika top features konsisten dengan domain knowledge churn.
Metric yang bagus tidak cukup — model yang belajar dari fitur yang salah tidak dilanjutkan.
Threshold formal: minimal 3 dari 5 `EXPECTED_IMPORTANT_FEATURES` harus masuk top-10 SHAP.

**8.7 Perbandingan Base Model vs Final Model Wajib Ada**
`base_model.joblib` disimpan dan tidak boleh ditimpa.
Laporan evaluasi final harus menyertakan perbandingan metric antara base model dan final model.

**8.8 Constants dari config/settings.py**
Semua threshold, nama kolom, path artifact, dan nama konstanta berasal dari `config/settings.py`.
Tidak ada nilai yang boleh di-hardcode di file manapun jika sudah terdefinisi di settings.
Import: `from config.settings import RANDOM_SEED, TARGET_COLUMN, ...`