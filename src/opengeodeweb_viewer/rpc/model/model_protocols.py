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
from opengeodeweb_viewer.vtk_protocol import VtkPipeline
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

    @exportRpc(model_prefix + model_schemas_dict["register"]["rpc"])
    def registerModel(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.model_schemas_dict["register"], self.model_prefix
        )
        params = schemas.Register.from_dict(rpc_params)
        data_id = params.id
        try:
            file_name = str(self.get_viewer_data(data_id).viewable_file)
            reader = vtkXMLMultiBlockDataReader()
            reader.SetFileName(os.path.join(self.DATA_FOLDER_PATH, data_id, file_name))
            reader.Update()
            filter = vtkGeometryFilter()
            filter.SetInputConnection(reader.GetOutputPort())
            filter.Update()
            geometry_output = filter.GetOutputDataObject(0)
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

    def modelSetupColorMap(
        self, data_id: str, points: list[float], minimum: float, maximum: float
    ) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        from vtkmodules.vtkRenderingCore import vtkColorTransferFunction
        lookup_table = vtkColorTransferFunction()
        pipeline.mapper.SetLookupTable(lookup_table)

        if not points:
            lookup_table.AddRGBPoint(minimum, 0, 0, 0)
            lookup_table.AddRGBPoint(maximum, 1, 1, 1)
        else:
            x_values = points[::4]
            x_minimum = min(x_values)
            x_maximum = max(x_values)
            x_range = x_maximum - x_minimum
            target_range = maximum - minimum

            for x_val, red_val, green_val, blue_val in zip(*[iter(points)] * 4):
                if x_range != 0:
                    new_x_val = minimum + (x_val - x_minimum) / x_range * target_range
                else:
                    new_x_val = minimum
                lookup_table.AddRGBPoint(new_x_val, red_val, green_val, blue_val)

        pipeline.mapper.SetScalarRange(minimum, maximum)
        lookup_table.SetRange(minimum, maximum)
        pipeline.mapper.SetUseLookupTableScalarRange(False)
        pipeline.mapper.InterpolateScalarsBeforeMappingOn()

    def modelDisplayScalarRange(self, data_id: str, minimum: float, maximum: float) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        pipeline.mapper.SetScalarRange(minimum, maximum)
        pipeline.mapper.GetLookupTable().SetRange(minimum, maximum)
        pipeline.mapper.SetUseLookupTableScalarRange(False)

