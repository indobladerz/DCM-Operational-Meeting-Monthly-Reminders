# DCM Operational Meeting Reminders — Procedure

PT Duta Cendana Mobilindo (DCM), dealer Toyota. Same rules and dates as the DCA reminder.

You are running unattended. Follow this file exactly. If anything here cannot be
read or a tool fails, **stop and send nothing** (never improvise a report).
Most firings send nothing; that is normal.

## Tool ceiling (important)
Use only: Bash, Read, Write, Edit, Glob, Grep, plus the Google Drive and Gmail
tools. Never call Agent/Task*, Workflow, TodoWrite, Skill, Artifact, Monitor,
and never use `run_in_background`. Do every step yourself, in order.

## Config
- Root folder "DCM Operational Meeting Reminders": `1GdguznxJ8Gx9K082fv8a5r2Ok5YQXjPz`
- Company: PT Duta Cendana Mobilindo (DCM), a Toyota dealership. Two branches (parent folder IDs):
  - Cianjur `1yWsQ8Ne6v1d8xeGpLmS2C5fltntpvLUy` — adh@toyotadutacendana.com, bm@toyotadutacendana.com
  - Bandung `1kZETNio3oY2Gv7mUVCItqjpNzdoFa7rw` — adh.pdl@toyotadutacendana.com, bm.pdl@toyotadutacendana.com
- Management (always these three): om@dutacendana.com, finance@suzukidutacendana.com, vwilliam@dutacendana.com
- Timezone: Asia/Jakarta (WIB, UTC+7). Decide "today" and "this month" in WIB.
- Month folder name: `<English Month> Meeting`, e.g. `December Meeting`.
- Rules: photo deadline = 17th; all must be in by 19th; keep max 3 month folders per branch.

## Mode is given by the routine prompt: CREATE, AUDIT, or FINAL-NOV-2026

---
## Mode CREATE (runs on the 10th)
For each of the 2 branches:
1. `search_files` with `parentId = '<branch id>' and mimeType = 'application/vnd.google-apps.folder' and trashed = false`.
2. If a folder named `<This Month> Meeting` does not exist, create it under the branch folder. If it exists, do nothing (idempotent).
3. **Retention (max 3):** list the branch's month folders again, sort by `createdTime` newest first. Keep the newest 3 (this month + 2 previous). Delete every older one immediately. Only touch folders whose name ends in ` Meeting`. Never touch anything else. Log what you deleted.
   - The Drive connector can only move to trash (`trash_file`); do that. Trash purges itself after 30 days.
Send no email in this mode.

---
## Mode AUDIT (runs on the 19th) and FINAL-NOV-2026 (one-off, 30 Nov 2026)
Target month = current month in WIB (for FINAL-NOV-2026: `2026-11`, folder `November Meeting`).
Silence rule: before sending anything, `search_threads` Gmail for the exact subject you are about to send, restricted to this month; if already sent for that branch/month, do not send again.

For each branch:
1. Find its `<Month> Meeting` folder. Missing folder → branch status NOT_DONE.
2. List files inside (`parentId`). Keep images only (`mimeType contains 'image/'`). Note each file's `createdTime` (upload time).
3. Download each image with `download_file_content` to a fresh scratchpad directory (never the repo directory). If the tool returns base64, decode it to a file with Write + `base64 -d`.
4. Run: `python3 -I scripts/audit_photo.py --month YYYY-MM --photo '<path>::<createdTime>' ...` (all photos of BOTH branches in one run so duplicates across branches are caught).
5. Classify each branch:
   - **DONE**: at least one photo with status `OK`, none `SUSPECT`.
   - **NOT_DONE**: no photos, or only `NO_METADATA` photos (say so: "foto tidak memiliki metadata lokasi/waktu yang valid").
   - **SUSPECT**: any photo `SUSPECT`.
   Also flag uploads whose `createdTime` is after the 19th 23:59 WIB as LATE.
6. Reconciliation: every branch must be assigned exactly one status; total = 2. If extraction or the script fails, stop and send nothing.

Then act:
- **Any SUSPECT** → send IMMEDIATELY the "Peringatan Integritas" email (template below) to the three management addresses, listing branch, file name, and exact flags. This is independent of the other emails.
- **Both branches DONE** → send "Laporan" email to the three management addresses.
- **Each NOT_DONE branch** → send the "NOTICE" email to that branch's adh+bm, CC the three management addresses. SUSPECT branches are not sent the NOTICE; management handles them.
- Mixed result (some DONE, some not): send the NOTICE(s) and no "all done" email.

FINAL-NOV-2026 additionally: always send one summary email (Bahasa) to the three management addresses with the status of both branches, even if some failed, in addition to the emails above.

Never claim tampering from a missing-metadata result alone; that is NOT_DONE, not SUSPECT.
Never invent file names, counts, or dates; use only what the tools returned.

---
## Email templates (Bahasa Indonesia, send as plain text)

### Laporan (semua selesai)
To: om@dutacendana.com, finance@suzukidutacendana.com, vwilliam@dutacendana.com
Subject: Laporan Meeting Operasional Bulanan DCM – <Bulan> <Tahun>: Semua Cabang Selesai
Body: Salam,\n\nDengan ini dilaporkan bahwa seluruh cabang DCM (Cianjur dan Bandung) telah melaksanakan meeting operasional bulan <Bulan> <Tahun> dan mengunggah foto bukti (dengan lokasi dan waktu). Hasil pemeriksaan metadata foto: tidak ditemukan indikasi manipulasi. Ringkasan per cabang: <tabel: cabang, jumlah foto valid, waktu unggah terakhir>.\n\nPesan ini dikirim otomatis.

### NOTICE (cabang belum meeting)
To: adh@ & bm@ of the branch
CC: om@dutacendana.com, finance@suzukidutacendana.com, vwilliam@dutacendana.com
Subject: NOTICE: Cabang anda belum melakukan meeting bulanan.
Body (adapt wording, keep substance): Kepada Yth. ADH dan Branch Manager <Cabang>,\n\nHingga <tanggal>, belum ada bukti meeting operasional bulan <Bulan> <Tahun> di folder cabang Anda (<alasan: tidak ada foto / foto tanpa metadata lokasi & waktu yang valid>). Meeting bulanan yang konsisten sangat penting untuk membahas berbagai permasalahan operasional, terutama Piutang (Accounts Receivable): umur piutang, tagihan yang menunggak, dan rencana penagihan. Tanpa meeting rutin, masalah terlambat diketahui dan risiko piutang macet meningkat.\n\nMohon segera laksanakan meeting dan unggah foto ber-geotag dan ber-timestamp ke folder "<Bulan> Meeting" cabang Anda, lalu konfirmasi balasan email ini.\n\nPesan ini dikirim otomatis dan ditembuskan kepada manajemen.

### Peringatan Integritas (dugaan manipulasi)
To: three management addresses
Subject: SEGERA: Dugaan manipulasi foto meeting DCM – Cabang <Cabang>
Body: Pemeriksaan metadata menemukan indikasi manipulasi pada foto bukti meeting cabang <Cabang> (<Bulan> <Tahun>): <file> – <flag dalam bahasa sederhana>. Temuan ini merupakan indikasi otomatis dan perlu diverifikasi manual.
