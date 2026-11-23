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
- Root folder "DCM Operational Meeting Reminder": `1GdguznxJ8Gx9K082fv8a5r2Ok5YQXjPz`
- Structure: root > `<English Month> Meeting` (one folder per month) > one subfolder per branch (`Cianjur`, `Bandung`). The root is shared with all branch addresses, so month and branch folders inherit access; never change sharing.
- Company: PT Duta Cendana Mobilindo (DCM), a Toyota dealership. Two branches:
  - Cianjur (subfolder `Cianjur`) — adh@toyotadutacendana.com, bm@toyotadutacendana.com
  - Bandung (subfolder `Bandung`) — adh.pdl@toyotadutacendana.com, bm.pdl@toyotadutacendana.com
- Management: only one person, vwilliam@toyotadutacendana.com (acts as the manager). Wherever this file says "management", it means this single address.
- Timezone: Asia/Jakarta (WIB, UTC+7). Decide "today" and "this month" in WIB.
- Month folder name: `<English Month> Meeting`, e.g. `December Meeting`.
- Rules: photo deadline = 17th; all must be in by 19th; keep max 3 month folders under the root.

## Mode is given by the routine prompt: CREATE, AUDIT, or FINAL-NOV-2026

---
## Mode CREATE (runs on the 10th)
1. `search_files` with `parentId = '1GdguznxJ8Gx9K082fv8a5r2Ok5YQXjPz' and mimeType = 'application/vnd.google-apps.folder' and trashed = false`.
2. If a folder named `<This Month> Meeting` does not exist, create it under the root. If it exists, reuse it (idempotent).
3. Inside that month folder, make sure the subfolders `Cianjur` and `Bandung` exist (search with `parentId = '<month folder id>'`); create any that are missing. Never create duplicates.
4. **Retention (max 3):** list the root's month folders again, sort by `createdTime` newest first. Keep the newest 3 (this month + 2 previous). Delete every older one immediately (its subfolders go with it). Only touch folders whose name ends in ` Meeting`. Never touch anything else. Log what you deleted.
   - The Drive connector can only move to trash (`trash_file`); do that. Trash purges itself after 30 days.
Send no email in this mode.

---
## Mode AUDIT (runs on the 19th) and FINAL-NOV-2026 (one-off, 30 Nov 2026)
Target month = current month in WIB (for FINAL-NOV-2026: `2026-11`, folder `November Meeting`).
Silence rule: before sending anything, `search_threads` Gmail for the exact subject you are about to send, restricted to this month; if already sent for that branch/month, do not send again.

For each branch:
1. Find the `<Month> Meeting` folder under the root, then the branch's subfolder (`Cianjur` or `Bandung`) inside it. Missing folder → branch status NOT_DONE.
2. List files inside the branch subfolder (`parentId`). Keep images only (`mimeType contains 'image/'`). Note each file's `createdTime` (upload time).
3. Download each image with `download_file_content` to a fresh scratchpad directory (never the repo directory). If the tool returns base64, decode it to a file with Write + `base64 -d`.
4. Run: `python3 -I scripts/audit_photo.py --month YYYY-MM --photo '<path>::<createdTime>' ...` (all photos of BOTH branches in one run so duplicates across branches are caught).
5. Classify each branch:
   - **DONE**: at least one photo with status `OK`, none `SUSPECT`.
   - **NOT_DONE**: no photos, or only `NO_METADATA` photos (say so: "foto tidak memiliki metadata lokasi/waktu yang valid").
   - **SUSPECT**: any photo `SUSPECT`.
   Also flag uploads whose `createdTime` is after the 19th 23:59 WIB as LATE.
6. Reconciliation: every branch must be assigned exactly one status; total = 2. If extraction or the script fails, stop and send nothing.

Then act:
- **Any SUSPECT** → send IMMEDIATELY the "Peringatan Integritas" email (template below) to vwilliam@toyotadutacendana.com, listing branch, file name, and exact flags. This is independent of the other emails.
- **Both branches DONE** → send "Laporan" email to vwilliam@toyotadutacendana.com.
- **Each NOT_DONE branch** → send the "NOTICE" email to that branch's adh+bm, CC vwilliam@toyotadutacendana.com. SUSPECT branches are not sent the NOTICE; management handles them.
- Mixed result (some DONE, some not): send the NOTICE(s) and no "all done" email.

FINAL-NOV-2026 additionally: always send one summary email (Bahasa) to vwilliam@toyotadutacendana.com with the status of both branches, even if some failed, in addition to the emails above.

Never claim tampering from a missing-metadata result alone; that is NOT_DONE, not SUSPECT.
Never invent file names, counts, or dates; use only what the tools returned.

---
## Email templates (Bahasa Indonesia, send as plain text)

### Laporan (semua selesai)
To: vwilliam@toyotadutacendana.com
Subject: Laporan Meeting Operasional Bulanan DCM – <Bulan> <Tahun>: Semua Cabang Selesai
Body: Salam,\n\nDengan ini dilaporkan bahwa seluruh cabang DCM (Cianjur dan Bandung) telah melaksanakan meeting operasional bulan <Bulan> <Tahun> dan mengunggah foto bukti (dengan lokasi dan waktu). Hasil pemeriksaan metadata foto: tidak ditemukan indikasi manipulasi. Ringkasan per cabang: <tabel: cabang, jumlah foto valid, waktu unggah terakhir>.\n\nPesan ini dikirim otomatis.

### NOTICE (cabang belum meeting)
To: the branch's adh and bm addresses (see Config)
CC: vwilliam@toyotadutacendana.com
Subject: NOTICE: Cabang anda belum melakukan meeting bulanan.
Body (adapt wording, keep substance): Kepada Yth. ADH dan Branch Manager <Cabang>,\n\nHingga <tanggal>, belum ada bukti meeting operasional bulan <Bulan> <Tahun> di folder cabang Anda (<alasan: tidak ada foto / foto tanpa metadata lokasi & waktu yang valid>). Meeting bulanan yang konsisten sangat penting untuk membahas berbagai permasalahan operasional, terutama Piutang (Accounts Receivable): umur piutang, tagihan yang menunggak, dan rencana penagihan. Tanpa meeting rutin, masalah terlambat diketahui dan risiko piutang macet meningkat.\n\nMohon segera laksanakan meeting dan unggah foto ber-geotag dan ber-timestamp ke folder "<Bulan> Meeting" > subfolder cabang Anda, lalu konfirmasi balasan email ini.\n\nPesan ini dikirim otomatis dan ditembuskan kepada manajemen.

### Peringatan Integritas (dugaan manipulasi)
To: vwilliam@toyotadutacendana.com
Subject: SEGERA: Dugaan manipulasi foto meeting DCM – Cabang <Cabang>
Body: Pemeriksaan metadata menemukan indikasi manipulasi pada foto bukti meeting cabang <Cabang> (<Bulan> <Tahun>): <file> – <flag dalam bahasa sederhana>. Temuan ini merupakan indikasi otomatis dan perlu diverifikasi manual.
