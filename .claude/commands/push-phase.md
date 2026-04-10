Kamu akan menjalankan proses lint, verifikasi, dan push untuk satu DEV phase.

Argumen: $ARGUMENTS
Format yang valid: `DEV-02` atau `dev02`

---

## LANGKAH 1 — Verifikasi Kesiapan Push

Baca `docs/DEV-PROGRESS.md`.

Cek bahwa semua task non-verifikasi di phase yang diminta sudah `[x]`.
Verifikasi task tidak perlu selesai — step verifikasi memang dikerjakan manual.

Jika masih ada task implementasi yang `[ ]`:
Lapor ke user: "Masih ada task yang belum selesai di phase ini. Selesaikan dulu sebelum push."
Tampilkan daftar task yang masih `[ ]`. Lalu berhenti.

---

## LANGKAH 2 — Jalankan black --check

```bash
black --check src/ api/ app/ config/ --line-length 88
```

Jika ada output (berarti ada file yang perlu diformat):
- Tampilkan output lengkap ke user
- Lapor: "black menemukan file yang perlu diformat. Perbaiki dulu sebelum push."
- Berhenti — jangan lanjut ke flake8 dan jangan push

Jika clean (exit code 0):
Lapor: "black: clean" dan lanjut ke Langkah 3.

---

## LANGKAH 3 — Jalankan flake8

```bash
flake8 src/ api/ app/ config/
```

Jika ada output (berarti ada linting error):
- Tampilkan output lengkap ke user (file, baris, kode error, deskripsi)
- Lapor: "flake8 menemukan error. Perbaiki dulu sebelum push."
- Berhenti — jangan push

Jika clean (exit code 0):
Lapor: "flake8: clean" dan lanjut ke Langkah 4.

---

## LANGKAH 4 — Tampilkan Summary

Jalankan:

```bash
git log origin/main..HEAD --oneline
git diff origin/main..HEAD --name-only
```

Tampilkan ke user:
```
Lint passed. Siap untuk push.

Phase   : DEV-0X
Commits : N commit sejak push terakhir
Files   : [daftar file yang berubah]

Ketik "yes" untuk push ke origin/main.
Ketik apapun selain "yes" untuk membatalkan.
```

Tunggu respons user — jangan push sebelum konfirmasi eksplisit.

---

## LANGKAH 5 — Push (Hanya Setelah Konfirmasi "yes")

Jika user menjawab "yes" (case-insensitive):

```bash
git push origin main
```

Setelah push berhasil, lapor:

```
DEV-0X pushed ke origin/main.

Langkah berikutnya: jalankan step verifikasi manual sesuai instruksi di
docs/DEV-0X_*.md bagian STEP terakhir (Verifikasi).
```

Jika user menjawab selain "yes":
Lapor: "Push dibatalkan. Tidak ada perubahan yang dikirim." Lalu berhenti.