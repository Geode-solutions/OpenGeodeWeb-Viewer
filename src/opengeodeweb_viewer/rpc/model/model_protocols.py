# Standard library imports
import os

# Third party imports
from vtkmodules.vtkCommonDataModel import (
    vtkCompositeDataSet,
)
from vtkmodules.vtkRenderingCore import (
    vtkCompositeDataDisplayAttributes,
    vtkCompositePolyDataMapper,
)
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
from . import schemas


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
        color=None,
    ) -> list[dict]:
        mapper = pipeline.mapper
        if not isinstance(mapper, vtkCompositePolyDataMapper):
            return []
        attr = mapper.GetCompositeDataDisplayAttributes()
        colors: list[dict] = []
        for block_id in block_ids:
            block_ds = pipeline.blockDataSets[block_id]
            if color_mode == "random":
                geode_id = pipeline.blockGeodeIds[block_id]
                r, g, b = deterministic_color(str(geode_id))
                attr.SetBlockColor(block_ds, [r, g, b])
                colors.append(
                    {
                        "viewer_id": block_id,
                        "geode_id": str(geode_id),
                        "color": {
                            "r": round(r * 255),
                            "g": round(g * 255),
                            "b": round(b * 255),
                        },
                    }
                )
            elif color is not None:
                r, g, b = (
                    color.r / 255,
                    color.g / 255,
                    color.b / 255,
                )
                attr.SetBlockColor(block_ds, [r, g, b])
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
