"""
Packaging Script for EFREI Submission
Generates StApp26_20230873_MORIN_DAI.zip according to syllabus specifications.
"""

import os
import zipfile
from utils.config import ARCHIVE_NAME

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ZIP_OUTPUT_PATH = os.path.join(PROJECT_ROOT, ARCHIVE_NAME)

# Files and directories to include
INCLUDED_FILES = [
    "app.py",
    "requirements.txt",
    "README.md",
    "data/raw/france_departments.geojson",
]

INCLUDED_DIRS = [
    "sections",
    "utils",
    "data/processed",
]

EXCLUDED_EXTENSIONS = [".pyc", ".log", ".tmp"]
EXCLUDED_DIRS = ["__pycache__", ".git", ".venv", "raw"]


def create_submission_zip():
    print(f"Creating submission archive: {ARCHIVE_NAME}...")

    with zipfile.ZipFile(ZIP_OUTPUT_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add root files
        for filename in INCLUDED_FILES:
            filepath = os.path.join(PROJECT_ROOT, filename)
            if os.path.exists(filepath):
                print(f"  + Adding {filename}")
                zf.write(filepath, arcname=filename)

        # Add directories
        for dirname in INCLUDED_DIRS:
            dirpath = os.path.join(PROJECT_ROOT, dirname)
            if os.path.exists(dirpath):
                for root, dirs, files in os.walk(dirpath):
                    dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
                    for file in files:
                        if any(file.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                            continue
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, PROJECT_ROOT)
                        print(f"  + Adding {rel_path}")
                        zf.write(full_path, arcname=rel_path)

    size_mb = os.path.getsize(ZIP_OUTPUT_PATH) / (1024 * 1024)
    print(f"\nArchive successfully generated: {ZIP_OUTPUT_PATH} ({size_mb:.2f} MB)")
    print("Ready for upload to EFREI portal!")


if __name__ == "__main__":
    create_submission_zip()
