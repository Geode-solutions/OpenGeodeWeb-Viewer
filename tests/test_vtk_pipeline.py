# Standard library imports

# Third party imports
import pytest
from vtkmodules.vtkCommonDataModel import (
    vtkCompositeDataSet,
    vtkDataSet,
    vtkImageData,
    vtkMultiBlockDataSet,
    vtkPolyData,
)
from vtkmodules.vtkCommonExecutionModel import vtkTrivialProducer
from vtkmodules.vtkFiltersGeneral import vtkShrinkFilter
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkFiltersSources import vtkCubeSource
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


def box(bounds: list[float]) -> vtkPolyData:
    cube = vtkCubeSource()
    cube.SetBounds(bounds)
    cube.Update()
    return cube.GetOutput()


def solid(bounds: list[float]) -> vtkImageData:
    image = vtkImageData()
    image.SetDimensions(2, 2, 2)
    image.SetOrigin(bounds[0], bounds[2], bounds[4])
    image.SetSpacing(
        bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4]
    )
    return image


def component_group(
    name: str, blocks: list[vtkPolyData] | list[vtkImageData]
) -> vtkMultiBlockDataSet:
    group = vtkMultiBlockDataSet()
    for index, block in enumerate(blocks):
        group.SetBlock(index, block)
    group.SetObjectName(name)
    return group


def stacked_model() -> vtkMultiBlockDataSet:
    surfaces = component_group(
        "surfaces",
        [
            box([0, 10, 0, 10, 5, 5]),
            box([0, 10, 0, 10, 9, 9]),
            box([0, 0, 0, 10, 3, 10]),
        ],
    )
    blocks = component_group(
        "blocks",
        [
            solid([0, 10, 0, 10, 0, 7]),
            solid([0, 10, 0, 10, 3, 10]),
            solid([20, 30, 0, 10, 0, 10]),
        ],
    )
    model = vtkMultiBlockDataSet()
    for index, group in enumerate((surfaces, blocks)):
        model.SetBlock(index, group)
        model.GetMetaData(index).Set(vtkCompositeDataSet.NAME(), group.GetObjectName())
    return model


def exploded_z_ranges(
    explode_factor: float, shrink_factor: float = 1.0
) -> list[tuple[float, float]]:
    model_source = vtkTrivialProducer()
    model_source.SetOutput(stacked_model())
    mapper = vtkCompositePolyDataMapper()
    mapper.SetCompositeDataDisplayAttributes(vtkCompositeDataDisplayAttributes())
    pipeline = VtkPipeline(model_source, mapper)  # type: ignore[arg-type]
    shrink_filter = vtkShrinkFilter()
    shrink_filter.SetShrinkFactor(shrink_factor)
    shrink_filter.SetInputConnection(model_source.GetOutputPort())
    pipeline.filter.SetInputConnection(shrink_filter.GetOutputPort())
    pipeline.filter.Update()
    filtered_model = pipeline.filter.GetOutputDataObject(0)
    pipeline.blockDataSets = pipeline.extract_blocks(filtered_model)
    pipeline.explode_factor = explode_factor
    exploded_blocks = pipeline.extract_blocks(pipeline.explode_blocks(filtered_model))
    return [
        (block.GetBounds()[4], block.GetBounds()[5])
        for block in exploded_blocks
        if isinstance(block, vtkDataSet)
    ]


def test_explode_blocks_stacks_overlapping_blocks_along_z() -> None:
    (
        interface,
        upper_surface,
        upper_side_surface,
        lower_block,
        upper_block,
        side_block,
    ) = exploded_z_ranges(1.0)
    gap = 0.05 * 10
    assert lower_block == pytest.approx((0, 7))
    assert upper_block == pytest.approx((7 + gap, 14 + gap))
    assert side_block == pytest.approx((0, 10))
    assert interface == pytest.approx((5, 5))
    assert upper_surface == pytest.approx((13 + gap, 13 + gap))
    assert upper_side_surface == pytest.approx((7 + gap, 14 + gap))


def test_explode_blocks_interpolates_with_factor() -> None:
    upper_block = exploded_z_ranges(0.5)[4]
    gap = 0.05 * 10
    assert upper_block == pytest.approx((3 + (4 + gap) / 2, 10 + (4 + gap) / 2))


def test_explode_blocks_keeps_components_on_their_block_after_shrink() -> None:
    upper_side_surface, upper_block = (
        exploded_z_ranges(1.0, shrink_factor=0.8)[index] for index in (2, 4)
    )
    gap = 0.05 * 10
    assert upper_block[0] > 7 + gap - 0.1
    assert upper_side_surface[0] > 7 + gap - 0.1
