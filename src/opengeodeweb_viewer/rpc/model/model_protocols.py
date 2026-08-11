# Standard library imports
import os
from typing import Optional, Protocol, TypedDict, cast

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict
from vtkmodules.vtkCommonDataModel import (
    vtkBoundingBox,
    vtkCompositeDataSet,
    vtkDataSet,
)
from vtkmodules.vtkCommonDataModel import vtkMultiBlockDataSet
from vtkmodules.vtkFiltersCore import vtkAppendDataSets
from vtkmodules.vtkIOXML import vtkXMLMultiBlockDataReader
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import (
    vtkColorTransferFunction,
    vtkCompositeDataDisplayAttributes,
    vtkCompositePolyDataMapper,
)
from wslink import register as exportRpc  # type: ignore

# Local application imports
from opengeodeweb_viewer.object.object_methods import VtkObjectView
from opengeodeweb_viewer.utils_functions import (
    create_color_transfer_function,
    deterministic_color,
    RpcParams,
    validate_schema,
)
from opengeodeweb_viewer.vtk_pipeline import BlockStyle, VtkPipeline
from . import schemas


class ColorProtocol(Protocol):
    red: int
    green: int
    blue: int
    alpha: float


class ColorRGBA(TypedDict):
    red: int
    green: int
    blue: int
    alpha: float


class ColorResult(TypedDict):
    viewer_id: int
    geode_id: str
    color: ColorRGBA


class VtkModelView(VtkObjectView):
    model_prefix = "opengeodeweb_viewer.model."
    model_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    def apply_color(
        self,
        pipeline: VtkPipeline,
        block_ids: list[int],
        color_mode: str,
        color: Optional[ColorProtocol] = None,
    ) -> list[ColorResult]:
        mapper = pipeline.mapper
        if not isinstance(mapper, vtkCompositePolyDataMapper):
            return []
        attr = mapper.GetCompositeDataDisplayAttributes()
        print(f"{attr=}", flush=True)
        colors: list[ColorResult] = []
        for block_id in block_ids:
            block_dataset = pipeline.blockDataSets[block_id]
            if isinstance(block_dataset, vtkDataSet):
                block_dataset.GetPointData().SetActiveScalars("")
                block_dataset.GetCellData().SetActiveScalars("")
                pipeline.get_block_style(block_id)["name"] = ""
                if color_mode == "random":
                    geode_id = pipeline.blockGeodeIds[block_id]
                    red, green, blue = deterministic_color(str(geode_id))
                    attr.SetBlockColor(block_dataset, [red, green, blue])
                    attr.SetBlockOpacity(block_dataset, 1.0)
                    colors.append(
                        {
                            "viewer_id": block_id,
                            "geode_id": str(geode_id),
                            "color": {
                                "red": round(red * 255),
                                "green": round(green * 255),
                                "blue": round(blue * 255),
                                "alpha": 1.0,
                            },
                        }
                    )
                elif color is not None:
                    red, green, blue, alpha = (
                        color.red / 255,
                        color.green / 255,
                        color.blue / 255,
                        color.alpha,
                    )
                    attr.SetBlockColor(block_dataset, [red, green, blue])
                    attr.SetBlockOpacity(block_dataset, alpha)
        mapper.Modified()
        self.setup_model_color_map(pipeline)
        return colors

    def setup_model_color_map(self, pipeline: VtkPipeline) -> None:
        active_attrs: dict[str, BlockStyle] = {}
        for block_id, style in pipeline.block_styles.items():
            if style and style["name"]:
                name = style["name"]
                item = style["item"]
                minimum = style["minimum"]
                maximum = style["maximum"]
                points = style["points"]
                attr_key = f"{name} (Item {item + 1})" if item > 0 else name
                if attr_key in active_attrs and (
                    active_attrs[attr_key]["minimum"] != minimum
                    or active_attrs[attr_key]["maximum"] != maximum
                    or active_attrs[attr_key]["points"] != points
                ):
                    attr_key = f"{attr_key} [{minimum:g}, {maximum:g}]"
                    if attr_key in active_attrs and active_attrs[attr_key]["points"] != points:
                        attr_key = f"{attr_key} (Block {block_id})"
                active_attrs[attr_key] = style
        for name, style in active_attrs.items():
            if name not in pipeline.scalar_bars:
                bar = vtkScalarBarActor()
                self.get_renderer().AddActor2D(bar)
                pipeline.scalar_bars[name] = bar
            bar = pipeline.scalar_bars[name]
            item = style["item"]
            minimum = style["minimum"]
            maximum = style["maximum"]
            points = style["points"]
            lut = create_color_transfer_function(points, minimum, maximum, item)
            bar.SetLookupTable(lut)
            bar.SetVisibility(True)
        for name, bar in pipeline.scalar_bars.items():
            if name not in active_attrs:
                bar.SetVisibility(False)

        self.update_scalar_bars_layout()

    def displayAttributeOnVertices(
        self,
        data_id: str,
        block_ids: list[int],
        name: str,
        item: int,
        color_map: list[float],
        minimum: float,
        maximum: float,
    ) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        for block_id in block_ids:
            style = pipeline.get_block_style(block_id)
            style["name"] = name
            style["item"] = item
            style["attribute_location"] = "point"
            style["points"] = color_map
            style["minimum"] = minimum
            style["maximum"] = maximum
            pipeline.update_block_colors(block_id)
        self.setup_model_color_map(pipeline)

    def displayAttributeOnCells(
        self,
        data_id: str,
        block_ids: list[int],
        name: str,
        item: int,
        color_map: list[float],
        minimum: float,
        maximum: float,
    ) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        for block_id in block_ids:
            style = pipeline.get_block_style(block_id)
            style["name"] = name
            style["item"] = item
            style["attribute_location"] = "cell"
            style["points"] = color_map
            style["minimum"] = minimum
            style["maximum"] = maximum
            pipeline.update_block_colors(block_id)
        self.setup_model_color_map(pipeline)

    def setupColorMap(
        self,
        pipeline: VtkPipeline,
        block_ids: list[int],
        points: list[float],
        minimum: float,
        maximum: float,
    ) -> None:
        for block_id in block_ids:
            style = pipeline.get_block_style(block_id)
            style["points"] = points
            style["minimum"] = minimum
            style["maximum"] = maximum
            pipeline.update_block_colors(block_id)
        self.setup_model_color_map(pipeline)

    @exportRpc(model_prefix + model_schemas_dict["register"]["rpc"])
    def registerModel(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.model_schemas_dict["register"], self.model_prefix
        )
        params = schemas.Register.from_dict(rpc_params)
        data_id = params.id
        try:
            viewer_data = self.get_viewer_data(data_id)
            file_name = str(viewer_data.viewable_file)

            reader = vtkXMLMultiBlockDataReader()
            reader.SetFileName(os.path.join(self.DATA_FOLDER_PATH, data_id, file_name))
            reader.Update()
            mapper = vtkCompositePolyDataMapper()
            attributes = vtkCompositeDataDisplayAttributes()
            mapper.SetCompositeDataDisplayAttributes(attributes)
            data = VtkPipeline(reader, mapper)
            geometry_output = cast(
                vtkMultiBlockDataSet, self.setup_pipeline(data, params.name)
            )
            self.highlight(data)
            iterator = geometry_output.NewTreeIterator()
            iterator.InitTraversal()
            while not iterator.IsDoneWithTraversal():
                block = iterator.GetCurrentDataObject()
                if block:
                    flat_index = iterator.GetCurrentFlatIndex()
                    while flat_index > len(data.blockDataSets):
                        data.blockDataSets.append(None)
                        data.blockGeodeIds.append("")
                    data.blockDataSets.append(block)
                    meta = iterator.GetCurrentMetaData()
                    name = meta.Get(vtkCompositeDataSet.NAME())
                    data.blockGeodeIds.append(name)
                iterator.GoToNextItem()
            self.registerObject(data_id, file_name, data)
        except Exception as e:
            print(f"Error registering model {data_id}: {str(e)}", flush=True)
            raise

    @exportRpc(model_prefix + model_schemas_dict["deregister"]["rpc"])
    def deregisterModel(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.model_schemas_dict["deregister"], self.model_prefix
        )
        params = schemas.Deregister.from_dict(rpc_params)
        self.deregisterObject(params.id)

    @exportRpc(model_prefix + model_schemas_dict["visibility"]["rpc"])
    def setModelVisibility(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.model_schemas_dict["visibility"], self.model_prefix
        )
        params = schemas.Visibility.from_dict(rpc_params)
        self.SetVisibility(params.id, params.visibility)

    @exportRpc(model_prefix + model_schemas_dict["highlight"]["rpc"])
    def setModelhighlight(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.model_schemas_dict["highlight"], self.model_prefix
        )
        params = schemas.Highlight.from_dict(rpc_params)
        pipeline = self.get_vtk_pipeline(params.id)
        if params.visibility and params.block_ids:
            append = vtkAppendDataSets()
            for i in params.block_ids:
                block = (
                    pipeline.blockDataSets[i]
                    if i < len(pipeline.blockDataSets)
                    else None
                )
                if isinstance(block, vtkDataSet):
                    append.AddInputData(block)
            append.Update()
            pipeline.highlight.mapper.SetInputDataObject(append.GetOutput())
        else:
            pipeline.highlight.mapper.SetInputConnection(
                pipeline.highlight.extractSelection.GetOutputPort()
            )
        pipeline.highlight.actor.SetVisibility(params.visibility)
        self.render(-1)

    @exportRpc(model_prefix + model_schemas_dict["get_blocks_bounds"]["rpc"])
    def getBlocksBounds(self, rpc_params: RpcParams) -> list[float]:
        validate_schema(
            rpc_params, self.model_schemas_dict["get_blocks_bounds"], self.model_prefix
        )
        params = schemas.GetBlocksBounds.from_dict(rpc_params)
        pipeline = self.get_vtk_pipeline(params.id)
        bbox = vtkBoundingBox()
        for block_id in params.block_ids:
            if isinstance(block := pipeline.blockDataSets[block_id], vtkDataSet):
                bbox.AddBounds(block.GetBounds())

        bounds = [0.0] * 6
        bbox.GetBounds(bounds)
        return bounds
