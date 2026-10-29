"""Package the HCX-Patent project source code into a clean, reproducible ZIP archive."""

import os
import zipfile
from pathlib import Path

EXCLUDE_DIRS = {
    "node_modules",
    ".pytest_cache",
    "__pycache__",
    ".git",
    "dist",
    "build",
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".parquet",
    ".joblib",
}


def package_project(root_dir: str, output_zip: str):
    root = Path(root_dir)
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in root.rglob("*"):
            if file_path.is_dir():
                continue

            parts = set(file_path.parts)
            if any(ex in parts for ex in EXCLUDE_DIRS):
                continue

            if file_path.suffix in EXCLUDE_EXTENSIONS:
                continue

            rel_path = file_path.relative_to(root.parent)
            zf.write(file_path, str(rel_path))

    print(f"Project successfully packaged to: {output_zip}")
    print(f"Archive size: {os.path.getsize(output_zip) / (1024 * 1024):.2f} MB")


if __name__ == "__main__":
    project_root = r"D:\ALT-PROJECT\hcx-patent"
    output_archive = r"D:\ALT-PROJECT\hcx-patent.zip"
    package_project(project_root, output_archive)

