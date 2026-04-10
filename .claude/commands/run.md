Kamu akan mengeksekusi satu step dari satu DEV phase berdasarkan argumen berikut: $ARGUMENTS

Format argumen yang valid: `DEV-02 step2` atau `DEV-02 step 2` atau `dev02 step2`
Parse argumen: ambil nomor DEV (01-08) dan nomor step (1-9).

---

## LANGKAH 1 — Orientasi

Baca `docs/DEV-PROGRESS.md` secara penuh.

Dari file tersebut:
- Konfirmasi step yang diminta belum selesai (masih ada `[ ]` di dalamnya)
- Jika semua task di step itu sudah `[x]` — lapor ke user: "Step ini sudah selesai. Cek /project:status untuk melihat step berikutnya." Lalu berhenti.
- Jika step belum dimulai atau sebagian selesai — lanjut ke Langkah 2.

---

## LANGKAH 2 — Baca Instruksi Step

Tentukan file DEV yang relevan berdasarkan nomor DEV:
- DEV-01 → `docs/DEV-01_repository_project_setup.md`
- DEV-02 → `docs/DEV-02_fastapi_service.md`
- DEV-03 → `docs/DEV-03_streamlit_ui.md`
- DEV-04 → `docs/DEV-04_testing_suite.md`
- DEV-05 → `docs/DEV-05_dockerization.md`
- DEV-06 → `docs/DEV-06_huggingface_spaces_setup.md`
- DEV-07 → `docs/DEV-07_cicd_pipeline.md`
- DEV-08 → `docs/DEV-08_readme_portfolio_documentation.md`

Extract HANYA section step yang diminta menggunakan sed. Jangan baca seluruh file.
Contoh untuk DEV-02 Step 2:

```bash
sed -n '/^## STEP 2/,/^## STEP 3/p' docs/DEV-02_fastapi_service.md
```

Jika step yang diminta adalah step terakhir di file tersebut (tidak ada step berikutnya),
gunakan sed sampai akhir file:

```bash
sed -n '/^## STEP 2/,$p' docs/DEV-02_fastapi_service.md
```

Baca output sed tersebut. Identifikasi semua Task X.X.X yang ada di dalamnya.

---

## LANGKAH 3 — Filter Task yang Belum Selesai

Dari DEV-PROGRESS.md, identifikasi task mana dalam step ini yang masih `[ ]`.
Mulai eksekusi dari task `[ ]` pertama — skip task yang sudah `[x]`.

Ini memungkinkan resume di tengah step jika sesi sebelumnya terputus.

---

## LANGKAH 4 — Eksekusi Task (Loop Otomatis)

Untuk setiap task yang belum selesai, jalankan loop berikut secara otomatis tanpa menunggu konfirmasi:

### 4a. Cek risiko sebelum eksekusi

Sebelum mengeksekusi task, evaluasi apakah task ini menyentuh:

**Hard stop — minta konfirmasi eksplisit dulu:**
- Akan overwrite file yang sudah ada dan tidak kosong (bukan file placeholder dari DEV-01)
- Akan memodifikasi `config/settings.py`
- Akan menyentuh `models/artifacts/`

**Lanjut otomatis jika:**
- Membuat file baru
- Mengisi file yang masih kosong (placeholder dari DEV-01)
- Mengedit file yang dibuat di sesi ini sendiri

### 4b. Eksekusi task

Implementasikan task sesuai instruksi yang sudah di-extract di Langkah 2.
Ikuti spesifikasi secara literal — jangan skip atau simplifikasi.

### 4c. Commit

```bash
git add <file-file yang diubah saja, bukan git add .>
git commit -m "feat(DEV-0X): Task X.X.X — <deskripsi singkat dalam bahasa Inggris>"
```

Hook `post-commit-update-progress.sh` akan otomatis update DEV-PROGRESS.md.
Jika hook gagal, update DEV-PROGRESS.md secara manual dan commit:
```bash
git add docs/DEV-PROGRESS.md
git commit -m "chore: progress Task X.X.X"
```

### 4d. Lanjut ke task berikutnya

Tanpa jeda, tanpa menunggu konfirmasi — langsung eksekusi task berikutnya.

---

## LANGKAH 5 — Setelah Semua Task Selesai

Setelah task terakhir dalam step ini selesai dan di-commit:

1. Baca DEV-PROGRESS.md — pastikan semua task di step ini sudah `[x]`
2. Update STATUS OVERVIEW table di DEV-PROGRESS.md jika seluruh phase selesai
3. Lapor ke user dengan format:

```
Step X selesai — N task dikerjakan.

File yang dibuat/diubah:
- path/to/file1.py
- path/to/file2.py

Sesi ini bisa ditutup.
Langkah berikutnya: /project:run DEV-0X stepY+1
```

Jangan mulai step berikutnya tanpa perintah eksplisit dari user.

---

## ATURAN YANG BERLAKU SELAMA EKSEKUSI

- Semua konstanta diambil dari `config/settings.py` — jangan hardcode nilai apapun yang sudah didefinisikan di sana
- Preprocessing hanya boleh ada di `api/predictor.py` via artifact load — tidak boleh ditulis ulang
- `app/` tidak boleh import dari `api/` atau `src/training/` atau `src/xai/`
- Semua path menggunakan `pathlib.Path`, bukan string concatenation
- `data/raw/` tidak boleh disentuh — hook akan memblokir otomatis
- Jika ada ambiguitas dalam instruksi DEV, pilih implementasi yang paling konsisten dengan prinsip di `CLAUDE.md` Section 3