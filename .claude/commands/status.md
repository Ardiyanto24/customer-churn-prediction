Baca `docs/DEV-PROGRESS.md` secara penuh.

Hitung untuk setiap DEV phase:
- Total task (hitung semua baris yang mengandung `- [ ]` atau `- [x]`)
- Task selesai (hitung baris `- [x]`)
- Task belum selesai (hitung baris `- [ ]`)

Tampilkan ringkasan dalam format berikut:

---

**TCCP Deployment — Progress**

| Phase | Selesai | Total | Status |
|---|---|---|---|
| DEV-01 | N | N | ✅ Complete / 🔄 In progress (step X) / ⬜ Not started |
| DEV-02 | N | N | ... |
| DEV-03 | N | N | ... |
| DEV-04 | N | N | ... |
| DEV-05 | N | N | ... |
| DEV-06 | N | N | ... |
| DEV-07 | N | N | ... |
| DEV-08 | N | N | ... |

**Posisi saat ini:** DEV-0X Step Y — Task X.X.X
(ambil dari task `[ ]` pertama yang ditemukan di DEV-PROGRESS.md)

**Command berikutnya:** `/project:run DEV-0X stepY`

---

Aturan status:
- ✅ Complete: semua task di phase itu `[x]`
- 🔄 In progress: ada campuran `[x]` dan `[ ]` — tampilkan step mana yang sedang berjalan
- ⬜ Not started: semua task masih `[ ]`