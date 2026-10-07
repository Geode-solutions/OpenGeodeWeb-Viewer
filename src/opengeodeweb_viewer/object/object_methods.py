import logging

# Third party imports
from vtkmodules.vtkCommonDataModel import (
    vtkDataSet,
    vtkMultiBlockDataSet,
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCompositePolyDataMapper,
    vtkDataSetMapper,
)

# Local application imports
from opengeodeweb_viewer.utils_functions import ColorClassProtocol
from opengeodeweb_viewer.vtk_pipeline import VtkPipeline
from opengeodeweb_viewer.vtk_protocol import VtkView

logger = logging.getLogger(__name__)


class VtkObjectView(VtkView):
    def __init__(self) -> None:
        super().__init__()

    def add_object(self, data_id: str, data: VtkPipeline) -> None:
        self.register_object(data_id, data)
        data.actor.SetMapper(data.mapper)
        data.mapper.SetColorModeToMapScalars()
        data.mapper.SetResolveCoincidentTopologyLineOffsetParameters(1, -0.1)
        data.mapper.SetResolveCoincidentTopologyPolygonOffsetParameters(2, 0)
        data.mapper.SetResolveCoincidentTopologyPointOffsetParameter(-2)
        data.scalar_bar.VisibilityOff()

        render_window = self.getView("-1")
        renderer = render_window.GetRenderers().GetFirstRenderer()
        should_reset_camera = True
        actors = renderer.GetActors()
        actors.InitTraversal()
        while actor := actors.GetNextItem():
            if actor.visibility:
                should_reset_camera = False
        renderer.AddActor(data.actor)
        renderer.AddActor(data.highlight.actor)
        renderer.AddViewProp(data.scalar_bar)
        if should_reset_camera:
            renderer.ResetCamera()

    def remove_object(self, data_id: str) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        render_window = self.getView("-1")
        renderer = render_window.GetRenderers().GetFirstRenderer()
        renderer.RemoveActor(pipeline.actor)
        renderer.RemoveActor(pipeline.highlight.actor)
        renderer.RemoveViewProp(pipeline.scalar_bar)
        for bar in pipeline.scalar_bars.values():
            renderer.RemoveViewProp(bar)
        self.deregister_object(data_id)
        self.update_scalar_bars_layout()

    def set_visibility(self, data_id: str, *, visibility: bool) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        pipeline.actor.SetVisibility(visibility)
        if not visibility:
            pipeline.scalar_bar.VisibilityOff()
            for bar in pipeline.scalar_bars.values():
                bar.VisibilityOff()
        else:
            if (
                pipeline.mapper.GetScalarVisibility()
                and pipeline.mapper.GetLookupTable() is not None
            ):
                pipeline.scalar_bar.VisibilityOn()
            for style in pipeline.block_styles.values():
                if style and style.get("name"):
                    for bar in pipeline.scalar_bars.values():
                        if bar.GetLookupTable() is not None:
                            bar.VisibilityOn()
                    break
        self.update_scalar_bars_layout()

    def set_opacity(self, data_id: str, opacity: float) -> None:
        actor = self.get_vtk_pipeline(data_id).actor
        actor.GetProperty().SetOpacity(opacity)

    def set_color(self, data_id: str, color: ColorClassProtocol) -> None:
        mapper = self.get_vtk_pipeline(data_id).mapper
        mapper.ScalarVisibilityOff()
        actor = self.get_vtk_pipeline(data_id).actor
        actor.GetProperty().SetColor(
            [color.red / 255, color.green / 255, color.blue / 255]
        )
        actor.GetProperty().SetOpacity(color.alpha)

    def set_edges_visibility(self, data_id: str, *, visibility: bool) -> None:
        if self.get_viewer_data(data_id).viewer_elements_type == "edges":
            self.set_visibility(data_id, visibility=visibility)
        else:
            actor = self.get_vtk_pipeline(data_id).actor
            actor.GetProperty().SetEdgeVisibility(visibility)

    def set_edges_width(self, data_id: str, width: float) -> None:
        actor = self.get_vtk_pipeline(data_id).actor
        if self.get_viewer_data(data_id).viewer_elements_type == "edges":
            actor.GetProperty().SetLineWidth(width)
        else:
            actor.GetProperty().SetEdgeWidth(width)

    def set_edges_color(self, data_id: str, color: ColorClassProtocol) -> None:
        if self.get_viewer_data(data_id).viewer_elements_type == "edges":
            self.set_color(data_id, color)
        else:
            actor = self.get_vtk_pipeline(data_id).actor
            actor.GetProperty().SetEdgeColor(
                [color.red / 255, color.green / 255, color.blue / 255]
            )

    def set_points_visibility(self, data_id: str, *, visibility: bool) -> None:
        if self.get_viewer_data(data_id).viewer_elements_type == "points":
            self.set_visibility(data_id, visibility=visibility)
        else:
            actor = self.get_vtk_pipeline(data_id).actor
            actor.GetProperty().SetVertexVisibility(visibility)

    def set_points_size(self, data_id: str, size: float) -> None:
        actor = self.get_vtk_pipeline(data_id).actor
        actor.GetProperty().SetPointSize(size)

    def set_points_color(self, data_id: str, color: ColorClassProtocol) -> None:
        if self.get_viewer_data(data_id).viewer_elements_type == "points":
            self.set_color(data_id, color)
        else:
            actor = self.get_vtk_pipeline(data_id).actor
            actor.GetProperty().SetVertexColor(
                [color.red / 255, color.green / 255, color.blue / 255]
            )

    def set_blocks_visibility(
        self, data_id: str, block_ids: list[int], *, visibility: bool
    ) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        mapper = pipeline.mapper
        if not isinstance(mapper, vtkCompositePolyDataMapper):
            msg = "Mapper is not a vtkCompositePolyDataMapper"
            raise TypeError(msg)
        blocks = pipeline.block_data_sets
        visibility_attributes = mapper.GetCompositeDataDisplayAttributes()
        logger.debug("visibility_attributes=%s", visibility_attributes)
        for block_id in block_ids:
            visibility_attributes.SetBlockVisibility(blocks[block_id], visibility)
        dataset = mapper.GetInputDataObject(0, 0)
        if not isinstance(dataset, vtkMultiBlockDataSet):
            return
        # Re-build a pruned dataset for the dedicated pick mapper
        if pipeline.pick_mapper is None:
            pipeline.pick_mapper = vtkCompositePolyDataMapper()
        pipeline.pick_mapper.SetInputDataObject(
            pipeline.prune_hidden_blocks(dataset, visibility_attributes)
        )

    def clear_colors(self, data_id: str) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        mapper = pipeline.mapper
        reader = pipeline.reader
        output = reader.GetOutputDataObject(0)
        if isinstance(output, vtkDataSet):
            output.GetPointData().SetActiveScalars("")
            output.GetCellData().SetActiveScalars("")
        elif isinstance(mapper, vtkCompositePolyDataMapper):
            pipeline.clear_blocks_scalars()
        mapper.ScalarVisibilityOff()
        pipeline.scalar_bar.VisibilityOff()
        for bar in pipeline.scalar_bars.values():
            bar.VisibilityOff()
        self.update_scalar_bars_layout()

    def _apply_highlight_style(self, actor: vtkActor, mapper: vtkDataSetMapper) -> None:
        mapper.ScalarVisibilityOff()
        mapper.SetResolveCoincidentTopologyToPolygonOffset()
        mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(-2, -2)
        prop = actor.GetProperty()
        prop.SetColor(0.235, 0.6, 0.514)
        prop.SetLineWidth(4)
        prop.SetPointSize(15)
        prop.RenderPointsAsSpheresOn()
        prop.LightingOff()
        prop.EdgeVisibilityOn()
        prop.SetEdgeColor(0.12, 0.35, 0.30)
        actor.SetMapper(mapper)
        actor.VisibilityOff()
        actor.UseBoundsOff()

    def highlight(self, pipeline: VtkPipeline) -> None:
        highlight = pipeline.highlight
        self._apply_highlight_style(highlight.actor, highlight.mapper)
        if pipeline.filter.GetNumberOfInputConnections(0) == 0:
            pipeline.filter.SetInputConnection(pipeline.reader.GetOutputPort())
        input_port = pipeline.filter.GetOutputPort()
        highlight.selection.AddNode(highlight.selection_node)
        highlight.extract_selection.SetInputConnection(0, input_port)
        highlight.extract_selection.SetInputData(1, highlight.selection)
        highlight.mapper.SetInputConnection(highlight.extract_selection.GetOutputPort())
