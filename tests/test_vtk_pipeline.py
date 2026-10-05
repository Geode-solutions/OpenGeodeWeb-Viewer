# Standard library imports

# Third party imports
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkIOXML import vtkXMLMultiBlockDataReader
from vtkmodules.vtkRenderingCore import (
    vtkCompositeDataDisplayAttributes,
    vtkCompositePolyDataMapper,
)

# Local application imports
from opengeodeweb_viewer.vtk_pipeline import VtkPipeline


def test_sync_block_display_attributes_drops_replaced_blocks() -> None:
    mapper = vtkCompositePolyDataMapper()
    mapper.SetCompositeDataDisplayAttributes(vtkCompositeDataDisplayAttributes())
    pipeline = VtkPipeline(vtkXMLMultiBlockDataReader(), mapper)
    source_block = vtkPolyData()
    destination_block = vtkPolyData()
    pipeline.blockDataSets = [source_block]
    attributes = mapper.GetCompositeDataDisplayAttributes()
    attributes.SetBlockVisibility(source_block, False)
    attributes.SetBlockOpacity(source_block, 0.5)
    attributes.SetBlockColor(source_block, [1.0, 0.0, 0.0])

    pipeline.sync_block_display_attributes([destination_block])

    attributes = mapper.GetCompositeDataDisplayAttributes()
    assert attributes.GetBlockVisibility(destination_block) == False
    assert attributes.GetBlockOpacity(destination_block) == 0.5
    assert attributes.HasBlockColor(destination_block)
    assert not attributes.HasBlockVisibility(source_block)
    assert not attributes.HasBlockOpacity(source_block)
    assert not attributes.HasBlockColor(source_block)
