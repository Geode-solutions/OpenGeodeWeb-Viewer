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
from vtkmodules.vtkFiltersSources import vtkCubeSource
from vtkmodules.vtkIOXML import vtkXMLMultiBlockDataReader
from vtkmodules.vtkRenderingCore import (
    vtkCompositeDataDisplayAttributes,
    vtkCompositePolyDataMapper,
)

# Local application imports
from opengeodeweb_viewer.vtk_pipeline import STACKING_GAP_RATIO, VtkPipeline


def test_sync_block_display_attributes_drops_replaced_blocks() -> None:
    mapper = vtkCompositePolyDataMapper()
    mapper.SetCompositeDataDisplayAttributes(vtkCompositeDataDisplayAttributes())
    pipeline = VtkPipeline(vtkXMLMultiBlockDataReader(), mapper)
    source_block = vtkPolyData()
    destination_block = vtkPolyData()
    pipeline.block_data_sets = [source_block]
    attributes = mapper.GetCompositeDataDisplayAttributes()
    attributes.SetBlockVisibility(source_block, False)  # noqa: FBT003 VTK API
    attributes.SetBlockOpacity(source_block, 0.5)
    attributes.SetBlockColor(source_block, [1.0, 0.0, 0.0])

    pipeline.sync_block_display_attributes([destination_block])

    attributes = mapper.GetCompositeDataDisplayAttributes()
    assert not attributes.GetBlockVisibility(destination_block)
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
    image.SetSpacing(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])
    return image


def component_group(
    name: str, blocks: list[vtkPolyData] | list[vtkImageData]
) -> vtkMultiBlockDataSet:
    group = vtkMultiBlockDataSet()
    for index, block in enumerate(blocks):
        group.SetBlock(index, block)
    group.SetObjectName(name)
    return group


def model_of(*groups: vtkMultiBlockDataSet) -> vtkMultiBlockDataSet:
    model = vtkMultiBlockDataSet()
    for index, group in enumerate(groups):
        model.SetBlock(index, group)
        model.GetMetaData(index).Set(vtkCompositeDataSet.NAME(), group.GetObjectName())
    return model


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
    return model_of(surfaces, blocks)


UPPER_BLOCK_ID = 7
STACKED_HEIGHT = 10
GAP = STACKING_GAP_RATIO * STACKED_HEIGHT


def explode(
    model: vtkMultiBlockDataSet,
    explode_factor: float,
    shrink_factor: float = 1.0,
    hidden_block_ids: tuple[int, ...] = (),
) -> tuple[list[vtkDataSet], list[vtkDataSet]]:
    model_source = vtkTrivialProducer()
    model_source.SetOutput(model)
    mapper = vtkCompositePolyDataMapper()
    mapper.SetCompositeDataDisplayAttributes(vtkCompositeDataDisplayAttributes())
    pipeline = VtkPipeline(model_source, mapper)  # type: ignore[arg-type]
    shrink_filter = vtkShrinkFilter()
    shrink_filter.SetShrinkFactor(shrink_factor)
    shrink_filter.SetInputConnection(model_source.GetOutputPort())
    pipeline.filter.SetInputConnection(shrink_filter.GetOutputPort())
    pipeline.filter.Update()
    filtered_model = pipeline.filter.GetOutputDataObject(0)
    pipeline.block_data_sets = pipeline.extract_blocks(filtered_model)
    for block_id in hidden_block_ids:
        mapper.GetCompositeDataDisplayAttributes().SetBlockVisibility(
            pipeline.block_data_sets[block_id],
            False,  # noqa: FBT003 VTK API
        )
    pipeline.explode_factor = explode_factor
    exploded_model = pipeline.explode_blocks(filtered_model)
    return (
        [
            block
            for block in pipeline.extract_blocks(filtered_model)
            if isinstance(block, vtkDataSet)
        ],
        [
            block
            for block in pipeline.extract_blocks(exploded_model)
            if isinstance(block, vtkDataSet)
        ],
    )


def z_ranges(blocks: list[vtkDataSet]) -> list[tuple[float, float]]:
    return [(block.GetBounds()[4], block.GetBounds()[5]) for block in blocks]


def test_explode_blocks_stacks_overlapping_blocks_along_z() -> None:
    (
        interface,
        upper_surface,
        upper_side_surface,
        lower_block,
        upper_block,
        side_block,
    ) = z_ranges(explode(stacked_model(), 1.0)[1])
    assert lower_block == pytest.approx((0, 7))
    assert upper_block == pytest.approx((7 + GAP, 14 + GAP))
    assert side_block == pytest.approx((0, 10))
    assert interface == pytest.approx((5, 5))
    assert upper_surface == pytest.approx((13 + GAP, 13 + GAP))
    assert upper_side_surface == pytest.approx((7 + GAP, 14 + GAP))


def test_explode_blocks_interpolates_with_factor() -> None:
    upper_block = z_ranges(explode(stacked_model(), 0.5)[1])[4]
    assert upper_block == pytest.approx((3 + (4 + GAP) / 2, 10 + (4 + GAP) / 2))


def test_explode_blocks_keeps_components_on_their_block_after_shrink() -> None:
    filtered_blocks, exploded_blocks = explode(stacked_model(), 1.0, shrink_factor=0.8)
    shifts = [
        exploded[0] - filtered[0]
        for filtered, exploded in zip(
            z_ranges(filtered_blocks), z_ranges(exploded_blocks), strict=True
        )
    ]
    upper_side_surface, upper_block = shifts[2], shifts[4]
    assert upper_block == pytest.approx(4 + GAP)
    assert upper_side_surface == pytest.approx(4 + GAP)


def test_explode_blocks_stacks_hidden_blocks() -> None:
    upper_block = z_ranges(explode(stacked_model(), 1.0, hidden_block_ids=(UPPER_BLOCK_ID,))[1])[4]
    assert upper_block == pytest.approx((7 + GAP, 14 + GAP))


def test_explode_blocks_reuses_unshifted_blocks() -> None:
    filtered_blocks, exploded_blocks = explode(stacked_model(), 1.0)
    lower_block, upper_block = 3, 4
    assert exploded_blocks[lower_block] is filtered_blocks[lower_block]
    assert exploded_blocks[upper_block] is not filtered_blocks[upper_block]


def test_explode_blocks_stacks_block_nested_in_another() -> None:
    blocks = component_group(
        "blocks",
        [solid([0, 10, 0, 10, 0, 10]), solid([0, 10, 0, 10, 0, 4])],
    )
    outer_block, inner_block = z_ranges(explode(model_of(blocks), 1.0)[1])
    assert outer_block[0] == pytest.approx(0)
    assert inner_block[0] == pytest.approx(10 + GAP)
