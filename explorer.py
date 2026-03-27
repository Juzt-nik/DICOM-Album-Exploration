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