from pathlib import Path
from typing import TYPE_CHECKING

from opengeodeweb_viewer import vtm_prefetch
from opengeodeweb_viewer.vtm_prefetch import prefetch_vtm_pieces

if TYPE_CHECKING:
    import pytest

DATA = Path(__file__).parent / "data"


def test_prefetch_reads_every_piece(monkeypatch: pytest.MonkeyPatch) -> None:
    read: list[Path] = []
    monkeypatch.setattr(vtm_prefetch, "_read_piece", read.append)
    assert prefetch_vtm_pieces(DATA / "cube.vtm") == 45
    assert len(read) == 45
    assert all(path.is_file() for path in read)
    assert all(path.parent.parent == DATA for path in read)


def test_prefetch_ignores_missing_pieces(tmp_path: Path) -> None:
    (tmp_path / "piece.vtp").write_bytes(b"data")
    vtm = tmp_path / "model.vtm"
    vtm.write_text(
        '<VTKFile><vtkMultiBlockDataSet><Block index="0">'
        '<DataSet index="0" file="piece.vtp" />'
        '<DataSet index="1" file="missing.vtp" />'
        "</Block></vtkMultiBlockDataSet></VTKFile>"
    )
    assert prefetch_vtm_pieces(vtm) == 2


def test_prefetch_without_pieces(tmp_path: Path) -> None:
    vtm = tmp_path / "empty.vtm"
    vtm.write_text("<VTKFile><vtkMultiBlockDataSet /></VTKFile>")
    assert prefetch_vtm_pieces(vtm) == 0
