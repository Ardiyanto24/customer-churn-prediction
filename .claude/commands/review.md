Kamu diminta mereview kode yang ditulis secara manual oleh user — bukan oleh Claude Code.

Argumen: $ARGUMENTS
Format yang valid: "Task 2.1.1 api/schemas.py" atau "Task 3.1.1 3.1.2 api/predictor.py api/main.py"
Parse argumen: ambil semua kode task (X.X.X) dan semua path file yang disebutkan.

---

## LANGKAH 1 — Baca Konteks Task

Dari argumen, identifikasi nomor DEV dan nomor step berdasarkan kode task.
Contoh: Task 2.1.1 → DEV phase sedang berjalan (baca dari DEV-PROGRESS.md), Step 2.

Baca DEV-PROGRESS.md untuk konfirmasi phase yang sedang aktif.

Extract instruksi task yang relevan dari file DEV menggunakan sed:
```bash
sed -n '/^## STEP X/,/^## STEP X+1/p' docs/DEV-0X_*.md
```

Baca instruksi setiap task yang disebutkan secara seksama —
ini adalah spesifikasi yang akan dijadikan patokan review.

---

## LANGKAH 2 — Baca File yang Ditulis Manual

Baca seluruh isi setiap file yang disebutkan dalam argumen.
Jangan skip bagian apapun meskipun panjang.

---

## LANGKAH 3 — Review

Evaluasi setiap file terhadap tiga lapisan:

### Lapisan A — Kesesuaian dengan Spesifikasi DEV
Bandingkan implementasi dengan instruksi task secara literal.
Periksa:
- Apakah semua field, method, class, dan fungsi yang diminta sudah ada?
- Apakah nama, tipe, dan constraint sudah sesuai spesifikasi?
- Apakah ada instruksi yang di-skip atau disederhanakan secara tidak tepat?
- Apakah ada tambahan yang tidak diminta dan berpotensi konflik?

### Lapisan B — Kepatuhan terhadap ML Principles (CLAUDE.md Section 3)
Periksa:
- Apakah ada konstanta yang di-hardcode padahal sudah ada di `config/settings.py`?
- Apakah ada logika preprocessing yang ditulis ulang di `api/`?
- Apakah `app/` mengimport langsung dari `api/` atau `src/training/`?
- Apakah semua path menggunakan `pathlib.Path`?
- Apakah `random_state` atau seed di-hardcode alih-alih import dari settings?

### Lapisan C — Kualitas Kode Umum
Periksa:
- Import yang tidak digunakan atau missing
- Type hint yang tidak konsisten dengan Pydantic schema atau spesifikasi
- Error handling yang hilang di titik yang diminta spesifikasi
- Potensi bug yang jelas (index error, None tidak dicek, dll)
- Nama variabel yang tidak konsisten dengan konvensi codebase

---

## LANGKAH 4 — Laporan Review

Tampilkan laporan dalam format berikut:

```
REVIEW — Task X.X.X [nama file]

STATUS: ✅ LULUS / ⚠️ LULUS DENGAN CATATAN / ❌ ADA MASALAH

--- Lapisan A: Spesifikasi ---
✅ [hal yang sudah benar]
❌ [hal yang kurang atau salah] — lokasi: baris N
   Seharusnya: [penjelasan singkat]

--- Lapisan B: ML Principles ---
✅ Tidak ada pelanggaran
❌ [pelanggaran yang ditemukan] — lokasi: baris N

--- Lapisan C: Kualitas Kode ---
✅ Tidak ada masalah
⚠️ [catatan minor yang tidak menghalangi fungsi tapi perlu diperbaiki]

--- Rekomendasi ---
[Jika ada masalah: tunjukkan potongan kode spesifik yang perlu diubah]
[Jika lulus: konfirmasi siap untuk git commit]
```

Jika semua lapisan bersih, tutup dengan:
`"Siap di-commit. Gunakan: git commit -m \"feat(DEV-0X): Task X.X.X — <deskripsi>\"`"

Jika ada masalah di Lapisan A atau B, jangan rekomendasikan commit
sampai masalah tersebut diperbaiki.

---

## ATURAN REVIEW

- Review harus objektif berdasarkan spesifikasi — bukan preferensi gaya
- Jangan rewrite seluruh file kecuali diminta — cukup tunjukkan bagian yang bermasalah
- Bedakan antara masalah yang menghalangi fungsi (❌) dan catatan minor (⚠️)
- Jika ada ambiguitas antara implementasi dan spesifikasi,
  sebutkan ambiguitasnya dan berikan rekomendasi yang paling aman