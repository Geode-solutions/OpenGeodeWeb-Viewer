# Standard library imports
import os

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict
from opengeodeweb_microservice.database.data import Data
from vtkmodules.vtkIOXML import vtkXMLGenericDataObjectReader, vtkXMLImageDataReader
from vtkmodules.vtkRenderingCore import (
    vtkColorTransferFunction,
    vtkDataSetMapper,
    vtkTexture,
)

# Local application imports
from opengeodeweb_viewer.object.object_methods import VtkObjectView
from opengeodeweb_viewer.utils_functions import (
    ColorClassProtocol,
    create_color_transfer_function,
)
from opengeodeweb_viewer.vtk_pipeline import VtkPipeline
from opengeodeweb_viewer.typed_rpc import typed_rpc
from . import schemas


class VtkMeshView(VtkObjectView):
    mesh_prefix = "opengeodeweb_viewer.mesh."
    mesh_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_prefix, schemas.register_route)
    def registerMesh(self, params: schemas.Register) -> schemas.RegisterResponse:
        print(f"{self.mesh_schemas_dict["register"]}", flush=True)
        data_id = params.id
        try:
            viewer_data = self.get_viewer_data(data_id)
            file_name = str(viewer_data.viewable_file)

            reader = vtkXMLGenericDataObjectReader()
            reader.SetFileName(os.path.join(self.DATA_FOLDER_PATH, data_id, file_name))
            reader.Update()
            mapper = vtkDataSetMapper()
            data = VtkPipeline(reader, mapper)
            self.setup_pipeline(data, params.name)
            self.highlight(data)
            self.registerObject(data_id, file_name, data)
        except Exception as e:
            print(f"Error registering mesh {data_id}: {str(e)}", flush=True)
            raise
        return schemas.RegisterResponse()

    @typed_rpc(mesh_prefix, schemas.deregister_route)
    def deregisterMesh(self, params: schemas.Deregister) -> schemas.DeregisterResponse:
        self.deregisterObject(params.id)
        return schemas.DeregisterResponse()

    @typed_rpc(mesh_prefix, schemas.visibility_route)
    def SetMeshVisibility(
        self, params: schemas.Visibility
    ) -> schemas.VisibilityResponse:
        self.SetVisibility(params.id, params.visibility)
        return schemas.VisibilityResponse()

    @typed_rpc(mesh_prefix, schemas.color_route)
    def setMeshColor(self, params: schemas.Color) -> schemas.ColorResponse:
        color = params.color
        self.SetColor(params.id, color.red, color.green, color.blue, color.alpha)
        return schemas.ColorResponse()

    @typed_rpc(mesh_prefix, schemas.apply_textures_route)
    def meshApplyTextures(
        self, params: schemas.ApplyTextures
    ) -> schemas.ApplyTexturesResponse:
        mesh_id = params.id
        for tex_info in params.textures:
            texture_id = tex_info.id
            texture_data = Data.get(texture_id)
            if texture_data is None:
                continue
            texture_file = texture_data.viewable_file
            if texture_file is None or not texture_file.lower().endswith(".vti"):
                continue
            texture_file_path = self.get_data_file_path(texture_id)
            texture_reader = vtkXMLImageDataReader()
            texture_reader.SetFileName(texture_file_path)
            texture_reader.Update()
            texture = vtkTexture()
            texture.SetInputConnection(texture_reader.GetOutputPort())
            texture.InterpolateOn()
            pipeline = self.get_vtk_pipeline(mesh_id)
            output = pipeline.reader.GetOutputAsDataSet()
            array = output.GetPointData().GetArray(tex_info.texture_name)
            if array:
                output.GetPointData().SetTCoords(array)
            pipeline.filter.Modified()
            pipeline.filter.Update()
            pipeline.actor.SetTexture(texture)
        return schemas.ApplyTexturesResponse()

    def displayAttributeOnVertices(
        self,
        data_id: str,
        name: str,
        item: int,
        color_map: list[float],
        minimum: float,
        maximum: float,
        no_data_color: ColorClassProtocol | None = None,
    ) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        pipeline.reader.GetOutputAsDataSet().GetPointData().SetActiveScalars(name)
        pipeline.filter.Update()
        if active_ds := pipeline.mapper.GetInputDataObject(0, 0):
            active_ds.GetPointData().SetActiveScalars(name)
        pipeline.mapper.ScalarVisibilityOn()
        pipeline.mapper.SetScalarModeToUsePointData()
        pipeline.mapper.ColorByArrayComponent(name, item)
        self.setupColorMap(data_id, color_map, minimum, maximum, item, no_data_color)

    def displayAttributeOnCells(
        self,
        data_id: str,
        name: str,
        item: int,
        color_map: list[float],
        minimum: float,
        maximum: float,
        no_data_color: ColorClassProtocol | None = None,
    ) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        pipeline.reader.GetOutputAsDataSet().GetCellData().SetActiveScalars(name)
        pipeline.filter.Update()
        if active_ds := pipeline.mapper.GetInputDataObject(0, 0):
            active_ds.GetCellData().SetActiveScalars(name)
        pipeline.mapper.ScalarVisibilityOn()
        pipeline.mapper.SetScalarModeToUseCellData()
        pipeline.mapper.ColorByArrayComponent(name, item)
        self.setupColorMap(data_id, color_map, minimum, maximum, item, no_data_color)

    def displayScalarRange(self, data_id: str, minimum: float, maximum: float) -> None:
        print(
            f"Setting scalar range for {data_id} to ({minimum}, {maximum})", flush=True
        )
        data = self.get_vtk_pipeline(data_id)
        data.mapper.SetScalarRange(minimum, maximum)
        data.mapper.GetLookupTable().SetRange(minimum, maximum)
        data.mapper.SetUseLookupTableScalarRange(False)

    def setupColorMap(
        self,
        data_id: str,
        points: list[float],
        minimum: float,
        maximum: float,
        item: int = 0,
        no_data_color: ColorClassProtocol | None = None,
    ) -> None:
        data = self.get_vtk_pipeline(data_id)
        lut = create_color_transfer_function(
            points, minimum, maximum, item, no_data_color
        )
        data.mapper.SetLookupTable(lut)

        data.mapper.SetScalarRange(minimum, maximum)
        lut.SetRange(minimum, maximum)
        data.mapper.SetUseLookupTableScalarRange(False)
        data.mapper.InterpolateScalarsBeforeMappingOn()

        data.scalarBar.SetLookupTable(lut)
        data.scalarBar.SetVisibility(True)
        self.update_scalar_bars_layout()

    @typed_rpc(mesh_prefix, schemas.highlight_route)
    def setMeshhighlight(self, params: schemas.Highlight) -> schemas.HighlightResponse:
        pipeline = self.get_vtk_pipeline(params.id)
        if params.visibility:
            dataset = pipeline.reader.GetOutputDataObject(0)
            pipeline.highlight.mapper.SetInputDataObject(dataset)
        else:
            pipeline.highlight.mapper.SetInputConnection(
                pipeline.highlight.extractSelection.GetOutputPort()
            )
        pipeline.highlight.actor.SetVisibility(params.visibility)
        self.render(-1)
        return schemas.HighlightResponse()
