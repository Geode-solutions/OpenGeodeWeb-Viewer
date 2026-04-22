# Standard library imports
import os

# Third party imports
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCompositeDataDisplayAttributes,
    vtkCompositePolyDataMapper,
    vtkDataSetMapper,
    vtkMapper,
)
from vtkmodules.vtkCommonDataModel import vtkCompositeDataSet
from wslink import register as exportRpc  # type: ignore
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.utils_functions import validate_schema, RpcParams
from opengeodeweb_viewer.rpc.model.model_protocols import VtkModelView
from . import schemas

# Enable polygon offset globally so highlight can render in front
vtkMapper.SetResolveCoincidentTopologyToPolygonOffset()


class VtkModelHighlightView(VtkModelView):
    model_highlight_prefix = "opengeodeweb_viewer.model.highlight."
    model_highlight_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    def _remove_highlight_actor(self, pipeline) -> None:
        if pipeline.highlightActor is not None:
            self.get_renderer().RemoveActor(pipeline.highlightActor)
            pipeline.highlightActor = None

    def _create_highlight_actor(self, pipeline, input_ds, is_composite):
        self._remove_highlight_actor(pipeline)

        actor = vtkActor()
        if is_composite:
            mapper = vtkCompositePolyDataMapper()
            mapper.SetInputDataObject(input_ds)
            mapper.SetCompositeDataDisplayAttributes(
                vtkCompositeDataDisplayAttributes()
            )
        else:
            mapper = vtkDataSetMapper()
            mapper.SetInputDataObject(input_ds)

        # Force highlight color instead of dataset scalars
        mapper.ScalarVisibilityOff()
        # Render in front of coincident main geometry
        mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(-2.0, -10.0)
        mapper.SetRelativeCoincidentTopologyLineOffsetParameters(-2.0, -10.0)
        mapper.SetRelativeCoincidentTopologyPointOffsetParameter(-10.0)

        actor.SetMapper(mapper)
        prop = actor.GetProperty()
        prop.SetColor(1.0, 0.0, 1.0)
        prop.SetEdgeVisibility(True)
        prop.SetLineWidth(6.0)
        prop.SetPointSize(12.0)
        prop.SetRenderPointsAsSpheres(True)
        prop.SetLighting(False)

        pipeline.highlightActor = actor
        self.get_renderer().AddActor(actor)
        return actor

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
            input_ds = (
                pipeline.filter.GetOutputDataObject(0)
                if pipeline.filter is not None
                else pipeline.reader.GetOutputDataObject(0)
            )

            if isinstance(input_ds, vtkCompositeDataSet):
                actor = self._create_highlight_actor(pipeline, input_ds, True)
                attr = actor.GetMapper().GetCompositeDataDisplayAttributes()

                # Hide all blocks
                iterator = input_ds.NewTreeIterator()
                iterator.InitTraversal()
                while not iterator.IsDoneWithTraversal():
                    block = iterator.GetCurrentDataObject()
                    if block:
                        attr.SetBlockVisibility(block, False)
                    iterator.GoToNextItem()

                # Show only the requested blocks
                for block_id in params.block_ids:
                    if block_id < len(pipeline.blockDataSets):
                        block_ds = pipeline.blockDataSets[block_id]
                        if block_ds is not None:
                            attr.SetBlockVisibility(block_ds, True)

                actor.GetMapper().Modified()
            else:
                self._create_highlight_actor(pipeline, input_ds, False)

        self.render("-1")
