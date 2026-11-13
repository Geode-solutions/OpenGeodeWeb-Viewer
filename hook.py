import os
import sys
from pathlib import Path

# For --onefile (extracted to temp _MEI folder)
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    bundle_dir = Path(sys._MEIPASS)  # noqa: SLF001 PyInstaller API
else:
    # For --onedir bundle (easier to debug first)
    bundle_dir = Path(sys.executable).parent / "_internal"

dri_path = bundle_dir / "dri"
if dri_path.exists():
    os.environ["LIBGL_DRIVERS_PATH"] = str(dri_path)
    print(f"Set LIBGL_DRIVERS_PATH to {dri_path}")  # noqa: T201 runtime hook log
