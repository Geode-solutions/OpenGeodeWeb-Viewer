# Standard library imports
from pathlib import Path
from typing import TYPE_CHECKING, override

# Third party imports
from opengeodeweb_microservice.schemas import get_schemas_dict
from vtkmodules.vtkIOXML import vtkXMLImageDataReader

# Local application imports
from opengeodeweb_viewer.object.object_methods import VtkObjectView
from opengeodeweb_viewer.typed_rpc import typed_rpc

from . import schemas

if TYPE_CHECKING:
    from opengeodeweb_viewer.vtk_pipeline import VtkPipeline


class VtkImageView(VtkObjectView):
    image_prefix = "opengeodeweb_viewer.image."
    image_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()

    @override
    def configure_actor(self, pipeline: VtkPipeline) -> None:
        # The scalars are the colors of the image, shown as they are
        pipeline.mapper.ScalarVisibilityOn()
        pipeline.mapper.SetColorModeToDirectScalars()
        pipeline.actor.GetProperty().LightingOff()
        pipeline.actor.PickableOff()

    @typed_rpc(image_prefix, schemas.register_route)
    def register_image(self, params: schemas.Register) -> schemas.RegisterResponse:
        self.register_dataset(params.id, params.name, vtkXMLImageDataReader())
        return schemas.RegisterResponse()

    @typed_rpc(image_prefix, schemas.deregister_route)
    def deregister_image(self, params: schemas.Deregister) -> schemas.DeregisterResponse:
        self.remove_object(params.id)
        return schemas.DeregisterResponse()

    @typed_rpc(image_prefix, schemas.visibility_route)
    def set_image_visibility(self, params: schemas.Visibility) -> schemas.VisibilityResponse:
        self.set_visibility(params.id, visibility=params.visibility)
        return schemas.VisibilityResponse()

    @typed_rpc(image_prefix, schemas.opacity_route)
    def set_image_opacity(self, params: schemas.Opacity) -> schemas.OpacityResponse:
        self.set_opacity(params.id, params.opacity)
        return schemas.OpacityResponse()
