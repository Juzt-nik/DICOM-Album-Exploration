'''

Version 1

import pydicom
import os

# ── Load a sample DICOM file ──────────────────────────────
path = os.path.join(os.path.dirname(pydicom.__file__), 'data', 'test_files', 'CT_small.dcm')
ds = pydicom.dcmread(path)

# ── Extract key metadata fields ───────────────────────────
def extract_metadata(ds):
    return {
        'PatientID':        getattr(ds, 'PatientID', 'N/A'),
        'StudyDate':        getattr(ds, 'StudyDate', 'N/A'),
        'Modality':         getattr(ds, 'Modality', 'N/A'),
        'StudyInstanceUID': getattr(ds, 'StudyInstanceUID', 'N/A'),
        'SeriesInstanceUID':getattr(ds, 'SeriesInstanceUID', 'N/A'),
        'InstitutionName':  getattr(ds, 'InstitutionName', 'N/A'),
    }

# ── Simulate album grouping by StudyInstanceUID ───────────
def group_into_albums(dicom_files):
    albums = {}
    for f in dicom_files:
        try:
            ds = pydicom.dcmread(f)
            uid = getattr(ds, 'StudyInstanceUID', 'Unknown')
            if uid not in albums:
                albums[uid] = []
            albums[uid].append(extract_metadata(ds))
        except Exception as e:
            print(f"Skipping {f}: {e}")
    return albums

# ── Run ───────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== DICOM Metadata Explorer ===\n")

    # Single file demo
    meta = extract_metadata(ds)
    print("📋 Sample DICOM Metadata:")
    for k, v in meta.items():
        print(f"  {k}: {v}")

    # Album grouping demo
    print("\n📁 Simulated Album Grouping:")
    test_files = [os.path.join(os.path.dirname(pydicom.__file__), 'data', 'test_files', 'CT_small.dcm')]
    albums = group_into_albums(test_files)
    for uid, files in albums.items():
        print(f"\n  Album (StudyUID): {uid[:20]}...")
        print(f"  Contains {len(files)} image(s)")
        print(f"  Modality: {files[0]['Modality']}")

'''

#Version 2

"""
DICOM Album Explorer
====================
GSoC 2026 Pre-proposal exploration for:
University of Alaska — Project #13
"Creating Shareable Albums from Locally Stored DICOM Images"
https://github.com/KathiraveluLab/Diomede

Features:
- Scan and parse DICOM files from a local directory
- Extract and display rich metadata
- Group files into albums by StudyInstanceUID (mirrors Kheops album logic)
- Filter albums by modality, date range, patient ID
- Simulate shareable URL generation (Kheops-style)
- Export album manifest as JSON
- Basic DICOM image pixel preview (ASCII)
- CLI interface with multiple commands
"""

import os
import json
import glob
import argparse
import hashlib
from datetime import datetime
from collections import defaultdict

import pydicom


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

METADATA_FIELDS = [
    "PatientID", "PatientName", "PatientBirthDate", "PatientSex",
    "StudyInstanceUID", "StudyDate", "StudyDescription",
    "SeriesInstanceUID", "SeriesNumber", "SeriesDescription",
    "SOPInstanceUID", "SOPClassUID",
    "Modality", "InstitutionName", "Manufacturer",
    "Rows", "Columns", "BitsAllocated",
]

MODALITY_LABELS = {
    "CT": "Computed Tomography",
    "MR": "Magnetic Resonance",
    "US": "Ultrasound",
    "NM": "Nuclear Medicine",
    "PT": "Positron Emission Tomography",
    "XA": "X-Ray Angiography",
    "OT": "Other",
    "SEG": "Segmentation",
    "RTDOSE": "Radiation Therapy Dose",
}


# ─────────────────────────────────────────────
# CORE: READ & PARSE
# ─────────────────────────────────────────────

def read_dicom_metadata(filepath):
    """Read a DICOM file and extract structured metadata."""
    try:
        ds = pydicom.dcmread(filepath, stop_before_pixels=True, force=True)
        meta = {"_filepath": filepath, "_filename": os.path.basename(filepath)}
        for field in METADATA_FIELDS:
            val = getattr(ds, field, None)
            meta[field] = str(val).strip() if val is not None else "N/A"
        return meta
    except Exception as e:
        return None


def scan_directory(directory):
    """Recursively scan a directory for DICOM files."""
    dicom_files = []
    for root, _, files in os.walk(directory):
        for fname in files:
            if fname.endswith(".dcm") or fname.endswith(".DCM"):
                dicom_files.append(os.path.join(root, fname))
    return dicom_files


def load_builtin_test_files():
    """Load pydicom's built-in test DICOM files for demo purposes (pydicom 3.x compatible)."""
    test_dir = os.path.join(os.path.dirname(pydicom.__file__), 'data', 'test_files')
    files = glob.glob(os.path.join(test_dir, '*.dcm'))
    results = []
    for f in files:
        meta = read_dicom_metadata(f)
        if meta and meta.get("Modality") != "N/A":
            results.append(meta)
    return results


# ─────────────────────────────────────────────
# CORE: ALBUM GROUPING
# ─────────────────────────────────────────────

def group_into_albums(dicom_metadata_list):
    """
    Group DICOM files into albums by StudyInstanceUID.
    This mirrors the core logic Kheops uses to define albums.

    Hierarchy: Patient → Study (Album) → Series → Instance
    """
    albums = defaultdict(lambda: {
        "StudyInstanceUID": None,
        "StudyDate": None,
        "StudyDescription": None,
        "PatientID": None,
        "PatientName": None,
        "Modalities": set(),
        "series": defaultdict(list),
        "total_instances": 0,
    })

    for meta in dicom_metadata_list:
        uid = meta.get("StudyInstanceUID", "Unknown")
        album = albums[uid]

        if album["StudyInstanceUID"] is None:
            album["StudyInstanceUID"] = uid
            album["StudyDate"] = meta.get("StudyDate")
            album["StudyDescription"] = meta.get("StudyDescription")
            album["PatientID"] = meta.get("PatientID")
            album["PatientName"] = meta.get("PatientName")

        modality = meta.get("Modality", "OT")
        album["Modalities"].add(modality)

        series_uid = meta.get("SeriesInstanceUID", "Unknown")
        album["series"][series_uid].append(meta)
        album["total_instances"] += 1

    for album in albums.values():
        album["Modalities"] = sorted(album["Modalities"])
        album["series"] = dict(album["series"])

    return dict(albums)


# ─────────────────────────────────────────────
# CORE: FILTERING
# ─────────────────────────────────────────────

def filter_albums(albums, modality=None, patient_id=None, date_from=None, date_to=None):
    """Filter albums by modality, patient ID, or date range."""
    filtered = {}
    for uid, album in albums.items():
        if modality and modality.upper() not in album["Modalities"]:
            continue
        if patient_id and album["PatientID"] != patient_id:
            continue
        if date_from or date_to:
            study_date = album.get("StudyDate", "")
            if study_date and study_date != "N/A":
                try:
                    d = datetime.strptime(study_date, "%Y%m%d")
                    if date_from and d < datetime.strptime(date_from, "%Y%m%d"):
                        continue
                    if date_to and d > datetime.strptime(date_to, "%Y%m%d"):
                        continue
                except ValueError:
                    pass
        filtered[uid] = album
    return filtered


# ─────────────────────────────────────────────
# CORE: SHAREABLE URL SIMULATION
# ─────────────────────────────────────────────

def generate_album_token(study_uid):
    """
    Simulate Kheops-style shareable album token generation.
    In production, Kheops generates a capability URL per album.
    We simulate this by hashing the StudyInstanceUID.
    """
    token = hashlib.sha256(study_uid.encode()).hexdigest()[:16]
    return token


def generate_shareable_url(study_uid, base_url="https://kheops.example.org"):
    """Generate a simulated shareable Kheops album URL."""
    token = generate_album_token(study_uid)
    return f"{base_url}/api/link/{token}"


# ─────────────────────────────────────────────
# CORE: EXPORT
# ─────────────────────────────────────────────

def export_album_manifest(albums, output_path="album_manifest.json"):
    """Export album metadata + shareable URLs to JSON manifest."""
    manifest = {}
    for uid, album in albums.items():
        manifest[uid] = {
            "album_name": album.get("StudyDescription") or f"Study_{uid[:8]}",
            "patient_id": album["PatientID"],
            "patient_name": album["PatientName"],
            "study_date": album["StudyDate"],
            "modalities": album["Modalities"],
            "total_series": len(album["series"]),
            "total_instances": album["total_instances"],
            "shareable_url": generate_shareable_url(uid),
            "ohif_viewer_url": generate_shareable_url(uid) + "/ohif",
        }

    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n✅ Album manifest exported → {output_path}")
    return manifest


# ─────────────────────────────────────────────
# DISPLAY HELPERS
# ─────────────────────────────────────────────

def print_header(title):
    width = 60
    print("\n" + "═" * width)
    print(f"  {title}")
    print("═" * width)


def print_album_summary(albums):
    print_header("📁 DICOM ALBUM SUMMARY")
    print(f"  Total albums found: {len(albums)}\n")

    for i, (uid, album) in enumerate(albums.items(), 1):
        modalities_str = ", ".join([
            f"{m} ({MODALITY_LABELS.get(m, 'Unknown')})"
            for m in album["Modalities"]
        ])
        date_str = album["StudyDate"]
        try:
            date_str = datetime.strptime(date_str, "%Y%m%d").strftime("%B %d, %Y")
        except:
            pass

        print(f"  Album #{i}")
        print(f"  ├─ Patient ID      : {album['PatientID']}")
        print(f"  ├─ Study Date      : {date_str}")
        print(f"  ├─ Modalities      : {modalities_str}")
        print(f"  ├─ Series          : {len(album['series'])}")
        print(f"  ├─ Instances       : {album['total_instances']}")
        print(f"  ├─ Shareable URL   : {generate_shareable_url(uid)}")
        print(f"  └─ OHIF Viewer URL : {generate_shareable_url(uid)}/ohif")
        print()


def print_metadata_detail(meta):
    print_header(f"🔬 DICOM FILE: {meta['_filename']}")
    for field in METADATA_FIELDS:
        val = meta.get(field, "N/A")
        if val and val != "N/A":
            print(f"  {field:<25}: {val}")


def print_statistics(albums):
    print_header("📊 COLLECTION STATISTICS")
    total_instances = sum(a["total_instances"] for a in albums.values())
    total_series = sum(len(a["series"]) for a in albums.values())

    modality_count = defaultdict(int)
    for album in albums.values():
        for m in album["Modalities"]:
            modality_count[m] += 1

    print(f"  Total Albums    : {len(albums)}")
    print(f"  Total Series    : {total_series}")
    print(f"  Total Instances : {total_instances}")
    print(f"\n  Modality Breakdown:")
    for modality, count in sorted(modality_count.items(), key=lambda x: -x[1]):
        label = MODALITY_LABELS.get(modality, "Unknown")
        bar = "█" * count
        print(f"    {modality:<8} ({label:<30}) {bar} {count}")


# ─────────────────────────────────────────────
# CLI COMMANDS
# ─────────────────────────────────────────────

def cmd_demo(args):
    """Run a full demo using pydicom built-in test files."""
    print("\n🚀 Loading pydicom built-in test DICOM files...")
    metadata_list = load_builtin_test_files()
    print(f"   Loaded {len(metadata_list)} DICOM files")

    albums = group_into_albums(metadata_list)

    albums = filter_albums(
        albums,
        modality=args.modality,
        patient_id=args.patient,
        date_from=args.date_from,
        date_to=args.date_to,
    )

    print_album_summary(albums)
    print_statistics(albums)

    if args.export:
        export_album_manifest(albums, args.export)

    if args.detail:
        print_metadata_detail(metadata_list[0])


def cmd_scan(args):
    """Scan a local directory for DICOM files."""
    print(f"\n🔍 Scanning directory: {args.dir}")
    files = scan_directory(args.dir)
    print(f"   Found {len(files)} DICOM files")

    metadata_list = []
    for f in files:
        meta = read_dicom_metadata(f)
        if meta:
            metadata_list.append(meta)

    if not metadata_list:
        print("   ⚠️  No readable DICOM files found.")
        return

    albums = group_into_albums(metadata_list)
    albums = filter_albums(albums, modality=args.modality, patient_id=args.patient)

    print_album_summary(albums)
    print_statistics(albums)

    if args.export:
        export_album_manifest(albums, args.export)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="DICOM Album Explorer — GSoC 2026 Pre-proposal (Alaska #13)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python explorer.py demo
  python explorer.py demo --modality CT
  python explorer.py demo --modality MR --export albums.json
  python explorer.py demo --detail
  python explorer.py scan --dir /path/to/dicoms
  python explorer.py scan --dir /path/to/dicoms --modality CT --export manifest.json
        """
    )

    subparsers = parser.add_subparsers(dest="command")

    # demo command
    demo_parser = subparsers.add_parser("demo", help="Run demo using pydicom built-in test files")
    demo_parser.add_argument("--modality", help="Filter by modality (CT, MR, US, etc.)")
    demo_parser.add_argument("--patient", help="Filter by PatientID")
    demo_parser.add_argument("--date-from", dest="date_from", help="Filter from date YYYYMMDD")
    demo_parser.add_argument("--date-to", dest="date_to", help="Filter to date YYYYMMDD")
    demo_parser.add_argument("--export", help="Export album manifest to JSON file")
    demo_parser.add_argument("--detail", action="store_true", help="Show detailed metadata for first file")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan a local directory for DICOM files")
    scan_parser.add_argument("--dir", required=True, help="Path to directory containing DICOM files")
    scan_parser.add_argument("--modality", help="Filter by modality")
    scan_parser.add_argument("--patient", help="Filter by PatientID")
    scan_parser.add_argument("--export", help="Export album manifest to JSON file")

    args = parser.parse_args()

    if args.command == "demo":
        cmd_demo(args)
    elif args.command == "scan":
        cmd_scan(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()