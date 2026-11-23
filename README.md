# DCM Operational Meeting Monthly Reminder

PT Duta Cendana Mobilindo (Toyota dealer): Cianjur and Bandung branches. Drive layout: root "DCM Operational Meeting Reminder" > "<Month> Meeting" > Cianjur / Bandung. Manager: vwilliam@toyotadutacendana.com.
Same procedure and dates as the DCA reminder. Procedure: `instructions/PROCEDURE.md`.
Photo audit: `scripts/audit_photo.py`.

Routines (claude.ai/code/routines, create in the web form, select this repo, connectors: Google Drive + Gmail):

| Routine | MODE | Schedule (WIB) |
|---|---|---|
| DCM meeting - create folders & cleanup | CREATE | day 10 every month |
| DCM meeting - audit & report | AUDIT | day 19 every month |
| DCM meeting - November 2026 final check (one-off) | FINAL-NOV-2026 | 30 Nov 2026 |

Prompt (replace MODE):

> Open instructions/PROCEDURE.md in this repository (branch main), read it in full, and follow it for MODE = <MODE>. If you cannot read the file, stop silently and send nothing. Before sending any email, search Gmail for the same subject this month; if it was already sent, do not send it again. Never call the Agent/Task tools, Workflow, TodoWrite, Skill, Artifact or Monitor, and never run Bash in the background. Do every step yourself, in order. Never retype or estimate a figure; if downloading or the audit script fails, stop and send nothing.
