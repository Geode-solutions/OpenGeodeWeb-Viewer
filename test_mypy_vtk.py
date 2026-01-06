from vtkmodules.vtkIOXML import vtkXMLReader
from typing import Any


def test_reader(reader: vtkXMLReader) -> None:
    reader.SetFileName("test.vtp")
    reader.Update()
    out = reader.GetOutputAsDataSet()
    reveal_type(out)
    port = reader.GetOutputPort()
    print(out, port)
