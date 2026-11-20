"""Read the pieces of a VTK multiblock file ahead of the VTK reader."""

# Standard library imports
import contextlib
import re
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

_PIECE_FILE = re.compile(r'\bfile="([^"]+)"')
_PREFETCH_WORKERS = 32


def _read_piece(path: Path) -> None:
    # The VTK reader reports missing or unreadable pieces itself
    with contextlib.suppress(OSError):
        path.read_bytes()


def prefetch_vtm_pieces(vtm_path: Path) -> int:
    """Read every piece of a .vtm file once, in parallel, and return how many were read.

    The XML multiblock reader opens its pieces one by one. Right after an import they
    are new files, and an on-access antivirus scan (Windows Defender) makes each first
    open slow: about 5 s for a model of 764 pieces, against 0.6 s for the VTK parsing
    itself. Opening them first from threads, which release the GIL during I/O, runs
    those scans in parallel; the VTK reader then opens files already scanned and cached.
    """
    folder = vtm_path.parent
    pieces = [folder / name for name in _PIECE_FILE.findall(vtm_path.read_text())]
    with ThreadPoolExecutor(min(_PREFETCH_WORKERS, len(pieces) or 1)) as executor:
        list(executor.map(_read_piece, pieces))
    return len(pieces)
