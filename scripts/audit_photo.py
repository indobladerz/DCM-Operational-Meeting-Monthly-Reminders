#!/usr/bin/env python3
"""Audit one or more meeting photos for metadata integrity.

Usage:
  python3 -I scripts/audit_photo.py --month 2026-11 \
      --photo PATH[:UPLOAD_ISO_TIME] [--photo ...]

Outputs JSON: one record per photo with `status` and `flags`.

Status values
  OK            Photo has EXIF capture time (and GPS) inside the target month.
  NO_METADATA   No usable EXIF (screenshot / WhatsApp / stripped). NOT proof of
                tampering, but it does NOT count as a valid meeting proof.
  SUSPECT       Signs of tampering or reuse. Report immediately.

Camera timezone: EXIF has no timezone, so comparisons use a 24h tolerance.
Requires Pillow only.
"""
import argparse, hashlib, json, sys
from datetime import datetime, timedelta, timezone

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

EDITORS = ("photoshop", "gimp", "lightroom", "snapseed", "picsart", "pixlr",
           "canva", "facetune", "paint", "affinity", "photopea", "adobe",
           "exiftool", "exif editor", "photo exif", "metadata")
TOL = timedelta(hours=24)


def parse_exif_dt(s):
    if not s:
        return None
    s = str(s).strip().replace("\x00", "")
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s[:19], fmt)
        except ValueError:
            pass
    return None


def parse_iso(s):
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc).replace(tzinfo=None)


def read_exif(path):
    img = Image.open(path)
    ex = img.getexif()
    data = {TAGS.get(k, k): v for k, v in ex.items()}
    sub = ex.get_ifd(0x8769)
    data.update({TAGS.get(k, k): v for k, v in sub.items()})
    gps = {GPSTAGS.get(k, k): v for k, v in ex.get_ifd(0x8825).items()}
    return data, gps, img


def audit(path, month, upload_iso, seen_hashes):
    rec = {"file": path, "status": "OK", "flags": [], "details": {}}
    raw = open(path, "rb").read()
    h = hashlib.sha256(raw).hexdigest()
    rec["details"]["sha256"] = h
    if h in seen_hashes:
        rec["flags"].append("DUPLICATE_OF:" + seen_hashes[h])
        rec["status"] = "SUSPECT"
    seen_hashes.setdefault(h, path)

    try:
        exif, gps, img = read_exif(path)
    except Exception as e:  # not an image / corrupt
        rec["status"] = "NO_METADATA"
        rec["flags"].append("UNREADABLE:" + type(e).__name__)
        return rec

    taken = parse_exif_dt(exif.get("DateTimeOriginal"))
    digitized = parse_exif_dt(exif.get("DateTimeDigitized"))
    modified = parse_exif_dt(exif.get("DateTime"))
    soft = str(exif.get("Software", "")).strip()
    make, model = exif.get("Make"), exif.get("Model")
    rec["details"].update({
        "DateTimeOriginal": str(taken) if taken else None,
        "DateTime": str(modified) if modified else None,
        "Software": soft or None, "Make": make, "Model": model,
        "has_gps": bool(gps.get("GPSLatitude")),
        "format": img.format, "size": img.size,
    })
    if gps.get("GPSLatitude"):
        rec["details"]["gps_datestamp"] = str(gps.get("GPSDateStamp"))

    if not taken:
        rec["status"] = "NO_METADATA" if rec["status"] == "OK" else rec["status"]
        rec["flags"].append("NO_CAPTURE_TIME")
    if not gps.get("GPSLatitude") or not gps.get("GPSLongitude"):
        if rec["status"] == "OK":
            rec["status"] = "NO_METADATA"
        rec["flags"].append("NO_GPS")
    if not make and not model:
        rec["flags"].append("NO_CAMERA_MAKE_MODEL")

    suspect = []
    y, m = map(int, month.split("-"))
    if taken and (taken.year, taken.month) != (y, m):
        suspect.append("CAPTURE_TIME_OUTSIDE_MONTH:%s" % taken)
    if soft and any(w in soft.lower() for w in EDITORS):
        suspect.append("EDITING_SOFTWARE:" + soft)
    if taken and modified and abs(modified - taken) > TOL:
        suspect.append("MODIFIED_LONG_AFTER_CAPTURE:%s vs %s" % (modified, taken))
    if taken and digitized and abs(digitized - taken) > timedelta(minutes=5):
        suspect.append("ORIGINAL_VS_DIGITIZED_MISMATCH")
    if taken and gps.get("GPSDateStamp"):
        try:
            gd = datetime.strptime(str(gps["GPSDateStamp"]), "%Y:%m:%d")
            if abs(gd.date() - taken.date()) > timedelta(days=1):
                suspect.append("GPS_DATE_NE_CAPTURE_DATE:%s vs %s" % (gd.date(), taken.date()))
        except ValueError:
            suspect.append("GPS_DATESTAMP_MALFORMED")
    if upload_iso and taken:
        up = parse_iso(upload_iso)
        if taken - up > TOL:
            suspect.append("CAPTURED_AFTER_UPLOAD:%s vs upload %s" % (taken, up))
        if up - taken > timedelta(days=45):
            suspect.append("OLD_PHOTO_UPLOADED_LATER:%s" % taken)
    if suspect:
        rec["status"] = "SUSPECT"
        rec["flags"].extend(suspect)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--month", required=True, help="YYYY-MM")
    ap.add_argument("--photo", action="append", required=True,
                    help="PATH or PATH::UPLOAD_ISO (Drive createdTime)")
    a = ap.parse_args()
    seen, out = {}, []
    for p in a.photo:
        path, _, up = p.partition("::")
        out.append(audit(path, a.month, up or None, seen))
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    sys.exit(main())
