import logging

# Standard library imports
from pathlib import Path

from opengeodeweb_microservice.database.data import Data

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict
from vtkmodules.vtkIOXML import vtkXMLGenericDataObjectReader, vtkXMLImageDataReader
from vtkmodules.vtkRenderingCore import (
    vtkDataSetMapper,
    vtkTexture,
)

# Local application imports
from opengeodeweb_viewer.object.object_methods import VtkObjectView
from opengeodeweb_viewer.typed_rpc import typed_rpc
from opengeodeweb_viewer.utils_functions import (
    AttributeProtocol,
    create_color_transfer_function,
)
from opengeodeweb_viewer.vtk_pipeline import VtkPipeline

from . import schemas

logger = logging.getLogger(__name__)


class VtkMeshView(VtkObjectView):
    mesh_prefix = "opengeodeweb_viewer.mesh."
    mesh_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @typed_rpc(mesh_prefix, schemas.register_route)
    def register_mesh(self, params: schemas.Register) -> schemas.RegisterResponse:
        logger.debug("%s", self.mesh_schemas_dict["register"])
        data_id = params.id
        try:
            viewer_data = self.get_viewer_data(data_id)
            file_name = str(viewer_data.viewable_file)

            reader = vtkXMLGenericDataObjectReader()
            reader.SetFileName(str(Path(self.DATA_FOLDER_PATH) / data_id / file_name))
            reader.Update()
            mapper = vtkDataSetMapper()
            data = VtkPipeline(reader, mapper)
            self.setup_pipeline(data, params.name)
            self.highlight(data)
            self.add_object(data_id, data)
        except Exception:
            logger.exception("Error registering mesh %s", data_id)
            raise
        return schemas.RegisterResponse()

    @typed_rpc(mesh_prefix, schemas.deregister_route)
    def deregister_mesh(self, params: schemas.Deregister) -> schemas.DeregisterResponse:
        self.remove_object(params.id)
        return schemas.DeregisterResponse()

    @typed_rpc(mesh_prefix, schemas.visibility_route)
    def set_mesh_visibility(self, params: schemas.Visibility) -> schemas.VisibilityResponse:
        self.set_visibility(params.id, visibility=params.visibility)
        return schemas.VisibilityResponse()

    @typed_rpc(mesh_prefix, schemas.color_route)
    def set_mesh_color(self, params: schemas.Color) -> schemas.ColorResponse:
        color = params.color
        self.set_color(params.id, color)
        return schemas.ColorResponse()

    @typed_rpc(mesh_prefix, schemas.apply_textures_route)
    def mesh_apply_textures(self, params: schemas.ApplyTextures) -> schemas.ApplyTexturesResponse:
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

    def display_attribute_on_vertices(self, data_id: str, attribute: AttributeProtocol) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        name = attribute.name
        pipeline.reader.GetOutputAsDataSet().GetPointData().SetActiveScalars(name)
        pipeline.filter.Update()
        if active_ds := pipeline.mapper.GetInputDataObject(0, 0):
            active_ds.GetPointData().SetActiveScalars(name)
        pipeline.mapper.ScalarVisibilityOn()
        pipeline.mapper.SetScalarModeToUsePointData()
        pipeline.mapper.ColorByArrayComponent(name, attribute.item)
        self.setup_color_map(data_id, attribute)

    def display_attribute_on_cells(self, data_id: str, attribute: AttributeProtocol) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        name = attribute.name
        pipeline.reader.GetOutputAsDataSet().GetCellData().SetActiveScalars(name)
        pipeline.filter.Update()
        if active_ds := pipeline.mapper.GetInputDataObject(0, 0):
            active_ds.GetCellData().SetActiveScalars(name)
        pipeline.mapper.ScalarVisibilityOn()
        pipeline.mapper.SetScalarModeToUseCellData()
        pipeline.mapper.ColorByArrayComponent(name, attribute.item)
        self.setup_color_map(data_id, attribute)

    def display_scalar_range(self, data_id: str, minimum: float, maximum: float) -> None:
        logger.debug("Setting scalar range for %s to (%s, %s)", data_id, minimum, maximum)
        data = self.get_vtk_pipeline(data_id)
        data.mapper.SetScalarRange(minimum, maximum)
        data.mapper.GetLookupTable().SetRange(minimum, maximum)
        data.mapper.UseLookupTableScalarRangeOff()

    def setup_color_map(self, data_id: str, attribute: AttributeProtocol) -> None:
        data = self.get_vtk_pipeline(data_id)
        minimum = attribute.minimum
        maximum = attribute.maximum
        lut = create_color_transfer_function(
            attribute.points, minimum, maximum, attribute.item, attribute.no_data_color
        )
        data.mapper.SetLookupTable(lut)

        data.mapper.SetScalarRange(minimum, maximum)
        lut.SetRange(minimum, maximum)
        data.mapper.UseLookupTableScalarRangeOff()
        data.mapper.InterpolateScalarsBeforeMappingOn()

        data.scalar_bar.SetLookupTable(lut)
        data.scalar_bar.VisibilityOn()
        self.update_scalar_bars_layout()

    @typed_rpc(mesh_prefix, schemas.highlight_route)
    def set_mesh_highlight(self, params: schemas.Highlight) -> schemas.HighlightResponse:
        pipeline = self.get_vtk_pipeline(params.id)
        if params.visibility:
            dataset = pipeline.reader.GetOutputDataObject(0)
            pipeline.highlight.mapper.SetInputDataObject(dataset)
        else:
            pipeline.highlight.mapper.SetInputConnection(
                pipeline.highlight.extract_selection.GetOutputPort()
            )
        pipeline.highlight.actor.SetVisibility(params.visibility)
        self.render(-1)
        return schemas.HighlightResponse()
