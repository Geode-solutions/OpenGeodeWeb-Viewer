# Standard library imports
import os

# Third party imports
from vtkmodules.vtkCommonDataModel import (
    vtkCompositeDataSet,
    vtkBoundingBox,
    vtkDataSet,
    vtkSelectionNode,
)
from vtkmodules.vtkRenderingCore import (
    vtkCompositePolyDataMapper,
    vtkCompositeDataDisplayAttributes,
    vtkColorTransferFunction,
)
from vtkmodules.vtkFiltersCore import vtkAppendDataSets
from vtkmodules.vtkIOXML import vtkXMLMultiBlockDataReader
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from wslink import register as exportRpc  # type: ignore
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.utils_functions import (
    validate_schema,
    RpcParams,
    deterministic_color,
)
from opengeodeweb_viewer.object.object_methods import VtkObjectView
from opengeodeweb_viewer.vtk_protocol import VtkPipeline, BlockStyle
from typing import Optional, List, TypedDict, Protocol
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

    def _get_block_style(self, pipeline: VtkPipeline, block_id: int) -> BlockStyle:
        if block_id not in pipeline.block_styles:
            style = BlockStyle(
                name="",
                attribute_location="point",
                points=[],
                minimum=0.0,
                maximum=1.0,
                item=0,
            )
            pipeline.block_styles[block_id] = style
        return pipeline.block_styles[block_id]

    def updateBlockColors(self, pipeline: VtkPipeline, block_id: int) -> None:
        block = pipeline.blockDataSets[block_id]
        if not isinstance(block, vtkDataSet):
            return

        style = self._get_block_style(pipeline, block_id)
        if not style["name"]:
            block.GetPointData().SetActiveScalars("")
            block.GetCellData().SetActiveScalars("")
            return

        field_data = (
            block.GetPointData()
            if style["attribute_location"] == "point"
            else block.GetCellData()
        )
        scalar_array = field_data.GetArray(style["name"])
        if not scalar_array:
            return

        lut = vtkColorTransferFunction()
        points = style["points"]
        minimum = style["minimum"]
        maximum = style["maximum"]
        if points:
            x_min, x_max = points[0], points[-4]
            span = x_max - x_min
            for i in range(0, len(points), 4):
                x, r, g, b = points[i : i + 4]
                new_x = (
                    minimum + (x - x_min) / span * (maximum - minimum)
                    if span
                    else minimum
                )
                lut.AddRGBPoint(new_x, r, g, b)
        else:
            lut.AddRGBPoint(minimum, 0, 0, 0)
            lut.AddRGBPoint(maximum, 1, 1, 1)

        lut.SetRange(minimum, maximum)
        rgba_colors = lut.MapScalars(scalar_array, 0, style.get("item", 0))
        rgba_colors.SetName(f"__colors_{style['name']}")

        field_data.AddArray(rgba_colors)
        field_data.SetActiveScalars(rgba_colors.GetName())

        other_field_data = (
            block.GetCellData()
            if style["attribute_location"] == "point"
            else block.GetPointData()
        )
        other_field_data.SetActiveScalars("")

        mapper = pipeline.mapper
        mapper.ScalarVisibilityOn()
        mapper.SetColorModeToDirectScalars()
        mapper.SetScalarModeToDefault()
        mapper.Modified()

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
        colors: list[ColorResult] = []
        for block_id in block_ids:
            block_dataset = pipeline.blockDataSets[block_id]
            if isinstance(block_dataset, vtkDataSet):
                block_dataset.GetPointData().SetActiveScalars("")
                block_dataset.GetCellData().SetActiveScalars("")
                self._get_block_style(pipeline, block_id)["name"] = ""
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
        return colors

    def displayAttributeOnVertices(
        self,
        pipeline: VtkPipeline,
        block_ids: list[int],
        name: str,
        item: int,
        color_map: list[float],
        minimum: float,
        maximum: float,
    ) -> None:
        for block_id in block_ids:
            style = self._get_block_style(pipeline, block_id)
            style["name"] = name
            style["item"] = item
            style["attribute_location"] = "point"
            style["points"] = color_map
            style["minimum"] = minimum
            style["maximum"] = maximum
            self.updateBlockColors(pipeline, block_id)

    def displayAttributeOnCells(
        self,
        pipeline: VtkPipeline,
        block_ids: list[int],
        name: str,
        item: int,
        color_map: list[float],
        minimum: float,
        maximum: float,
    ) -> None:
        for block_id in block_ids:
            style = self._get_block_style(pipeline, block_id)
            style["name"] = name
            style["item"] = item
            style["attribute_location"] = "cell"
            style["points"] = color_map
            style["minimum"] = minimum
            style["maximum"] = maximum
            self.updateBlockColors(pipeline, block_id)

    def setupColorMap(
        self,
        pipeline: VtkPipeline,
        block_ids: list[int],
        points: list[float],
        minimum: float,
        maximum: float,
    ) -> None:
        for block_id in block_ids:
            style = self._get_block_style(pipeline, block_id)
            style["points"] = points
            style["minimum"] = minimum
            style["maximum"] = maximum
            self.updateBlockColors(pipeline, block_id)

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
            filter = vtkGeometryFilter()
            filter.SetInputConnection(reader.GetOutputPort())
            filter.Update()
            geometry_output = filter.GetOutputDataObject(0)
            if geometry_output:
                geometry_output.SetObjectName(params.name)
            mapper = vtkCompositePolyDataMapper()
            mapper.SetInputDataObject(geometry_output)
            attributes = vtkCompositeDataDisplayAttributes()
            mapper.SetCompositeDataDisplayAttributes(attributes)
            data = VtkPipeline(reader, mapper, filter)
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
