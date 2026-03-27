# 🏥 DICOM Album Explorer

A Python CLI utility to scan, parse, group, filter, and export locally stored DICOM images into shareable albums — built as a pre-proposal exploration for **GSoC 2026**.

---

## 🎯 GSoC 2026 Context

This project is a pre-proposal prototype for:

> **University of Alaska — Project #13**
> *"Creating Shareable Albums from Locally Stored DICOM Images"*
> Source: [github.com/KathiraveluLab/Diomede](https://github.com/KathiraveluLab/Diomede)

The goal of the GSoC project is to implement a standalone utility within the **Diomede** framework that allows researchers to query DICOM metadata, create albums, and share them via unique URLs through **Kheops** — viewable in the **OHIF Viewer**.

This prototype validates the core technical approach.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📂 **Directory Scan** | Recursively scan any local folder for `.dcm` files |
| 🔬 **Metadata Extraction** | Parse 15+ DICOM fields per file (PatientID, StudyDate, Modality, UIDs...) |
| 📁 **Album Grouping** | Group files by `StudyInstanceUID` — mirrors Kheops album logic |
| 🔍 **Filtering** | Filter albums by modality, patient ID, or date range |
| 🔗 **Shareable URLs** | Simulate Kheops-style capability URL generation per album |
| 👁️ **OHIF Viewer URLs** | Generate simulated OHIF Viewer links per album |
| 📊 **Statistics** | Modality breakdown with visual bar chart |
| 💾 **JSON Export** | Export full album manifest with URLs to JSON |
| 🖥️ **CLI Interface** | Multiple commands with flags for flexible usage |

---

## 🧠 Key Design Insight

The DICOM data hierarchy forms the natural data model for album grouping:

```
Patient
  └── Study  ← This is the "Album" (grouped by StudyInstanceUID)
        └── Series
              └── Instance (individual .dcm file)
```

Each unique `StudyInstanceUID` becomes one shareable album — exactly how Kheops organizes data.

---

## 🚀 Setup

```bash
git clone https://github.com/YOURUSERNAME/dicom-album-explorer
cd dicom-album-explorer
pip install -r requirements.txt
```

---

## 💻 Usage

### Demo mode (uses pydicom built-in test files — no DICOM files needed)
```bash
# Full demo
python explorer.py demo

# Filter by modality
python explorer.py demo --modality CT
python explorer.py demo --modality MR

# Export album manifest to JSON
python explorer.py demo --modality CT --export albums.json

# Show detailed metadata for first file
python explorer.py demo --detail

# Filter by date range
python explorer.py demo --date-from 20040101 --date-to 20041231
```

### Scan your own DICOM directory
```bash
python explorer.py scan --dir /path/to/your/dicoms
python explorer.py scan --dir /path/to/your/dicoms --modality CT --export manifest.json
python explorer.py scan --dir /path/to/your/dicoms --patient PATIENT_ID
```

---

## 📋 Example Output

```
🚀 Loading pydicom built-in test DICOM files...
   Loaded 63 DICOM files

════════════════════════════════════════════════════════════
  📁 DICOM ALBUM SUMMARY
════════════════════════════════════════════════════════════
  Total albums found: 3

  Album #1
  ├─ Patient ID      : 1CT1
  ├─ Study Date      : January 19, 2004
  ├─ Modalities      : CT (Computed Tomography)
  ├─ Series          : 1
  ├─ Instances       : 1
  ├─ Shareable URL   : https://kheops.example.org/api/link/2966c9f9fbae278d
  └─ OHIF Viewer URL : https://kheops.example.org/api/link/2966c9f9fbae278d/ohif

════════════════════════════════════════════════════════════
  📊 COLLECTION STATISTICS
════════════════════════════════════════════════════════════
  Total Albums    : 3
  Total Series    : 3
  Total Instances : 3

  Modality Breakdown:
    CT  (Computed Tomography) ███ 3
```

---

## 📄 JSON Export Sample

```json
{
  "1.3.6.1.4.1.5962.1.2.1.20040119": {
    "album_name": "Study_CT_Chest",
    "patient_id": "1CT1",
    "study_date": "20040119",
    "modalities": ["CT"],
    "total_series": 1,
    "total_instances": 4,
    "shareable_url": "https://kheops.example.org/api/link/2966c9f9fbae278d",
    "ohif_viewer_url": "https://kheops.example.org/api/link/2966c9f9fbae278d/ohif"
  }
}
```

---

## 🔗 How This Maps to the GSoC Project

| This Prototype | GSoC Diomede Implementation |
|---|---|
| `read_dicom_metadata()` | DICOM parsing layer in Diomede |
| `group_into_albums()` | Album creation logic via Kheops API |
| `generate_shareable_url()` | Real Kheops capability URL generation |
| `filter_albums()` | Researcher query interface |
| JSON export | Album manifest for MEDIator integration |
| OHIF Viewer URL | Native Kheops ↔ OHIF integration |

---

## 📦 Requirements

```
pydicom>=3.0.0
```

---

## 👤 Author

Built by Sagnik Roy Chowdhury as a pre-proposal exploration for GSoC 2026.
