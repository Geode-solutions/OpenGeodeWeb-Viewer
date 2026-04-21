# Standard library imports
import os

# Third party imports
from vtkmodules.vtkFiltersExtraction import vtkExtractBlock
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCompositePolyDataMapper,
)
from wslink import register as exportRpc  # type: ignore
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.utils_functions import validate_schema, RpcParams
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from . import schemas


class VtkModelHighlightView(VtkModelView):
    model_highlight_prefix = "opengeodeweb_viewer.model.highlight."
    model_highlight_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    def _get_highlight_actor(self, pipeline) -> vtkActor:
        if pipeline.highlightActor is None:
            pipeline.highlightActor = vtkActor()
            mapper = vtkCompositePolyDataMapper()
            pipeline.highlightActor.SetMapper(mapper)
            prop = pipeline.highlightActor.GetProperty()
            prop.SetColor(1.0, 0.0, 1.0)
            prop.SetEdgeVisibility(True)
            prop.SetLineWidth(6.0)
            prop.SetLighting(False)

            renderer = self.get_renderer()
            renderer.AddActor(pipeline.highlightActor)
        return pipeline.highlightActor

    def _remove_highlight_actor(self, pipeline) -> None:
        if pipeline.highlightActor is not None:
            renderer = self.get_renderer()
            renderer.RemoveActor(pipeline.highlightActor)
            pipeline.highlightActor = None

    @exportRpc(model_highlight_prefix + model_highlight_schemas_dict["highlight"]["rpc"])
    def setModelHighlight(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.model_highlight_schemas_dict["highlight"],
            self.model_highlight_prefix,
        )
        params = schemas.Highlight.from_dict(rpc_params)
        pipeline = self.get_vtk_pipeline(params.id)

        if not params.block_ids:
            self._remove_highlight_actor(pipeline)
        else:
            actor = self._get_highlight_actor(pipeline)
            extractBlock = vtkExtractBlock()
            extractBlock.SetInputDataObject(pipeline.reader.GetOutputDataObject(0))
            for block_id in params.block_ids:
                extractBlock.AddIndex(block_id)
            extractBlock.Update()

            mapper = actor.GetMapper()
            mapper.SetInputDataObject(extractBlock.GetOutput())

        self.render("-1")
