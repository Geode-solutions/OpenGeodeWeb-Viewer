# Standard library imports
import math
import os
from pathlib import Path
from typing import Any

from opengeodeweb_microservice.schemas import get_schemas_dict
from vtkmodules.vtkCommonCore import reference, vtkPoints, vtkUnsignedCharArray
from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkDataSet, vtkPolyData
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackball
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget

# Third party imports
from vtkmodules.vtkIOImage import vtkJPEGWriter, vtkPNGWriter
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor, vtkCubeAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkAbstractMapper,
    vtkActor,
    vtkCellPicker,
    vtkDataSetMapper,
    vtkPropPicker,
    vtkRenderer,
    vtkRenderWindowInteractor,
    vtkWindowToImageFilter,
    vtkWorldPointPicker,
)

from opengeodeweb_viewer.rpc.viewer import schemas
from opengeodeweb_viewer.typed_rpc import typed_rpc

# Local application imports
from opengeodeweb_viewer.vtk_pipeline import RulerPipeline
from opengeodeweb_viewer.vtk_protocol import VtkView


class VtkViewerView(VtkView):
    viewer_prefix = "opengeodeweb_viewer.viewer."
    viewer_schemas_dict = get_schemas_dict(Path(__file__).parent / "schemas")

    def __init__(self) -> None:
        super().__init__()
        self._preview_actor: vtkActor | None = None

    @typed_rpc(viewer_prefix, schemas.reset_visualization_route)
    def resetVisualization(
        self, params: schemas.ResetVisualization
    ) -> schemas.ResetVisualizationResponse:
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        renderer.RemoveAllViewProps()

        grid_scale = vtkCubeAxesActor()
        grid_scale.SetCamera(renderer.GetActiveCamera())
        grid_scale.DrawXGridlinesOn()
        grid_scale.DrawYGridlinesOn()
        grid_scale.DrawZGridlinesOn()
        grid_scale.SetGridLineLocation(grid_scale.VTK_GRID_LINES_FURTHEST)
        grid_scale.GetTitleTextProperty(0).SetColor(0, 0, 0)
        grid_scale.GetTitleTextProperty(1).SetColor(0, 0, 0)
        grid_scale.GetTitleTextProperty(2).SetColor(0, 0, 0)
        grid_scale.GetXAxesLinesProperty().SetColor(0, 0, 0)
        grid_scale.GetYAxesLinesProperty().SetColor(0, 0, 0)
        grid_scale.GetZAxesLinesProperty().SetColor(0, 0, 0)
        grid_scale.GetLabelTextProperty(0).SetColor(0, 0, 0)
        grid_scale.GetLabelTextProperty(1).SetColor(0, 0, 0)
        grid_scale.GetLabelTextProperty(2).SetColor(0, 0, 0)
        grid_scale.GetXAxesGridlinesProperty().SetColor(0, 0, 0)
        grid_scale.GetYAxesGridlinesProperty().SetColor(0, 0, 0)
        grid_scale.GetZAxesGridlinesProperty().SetColor(0, 0, 0)
        grid_scale.SetFlyModeToOuterEdges()
        grid_scale.SetXTitle("X")
        grid_scale.SetYTitle("Y")
        grid_scale.SetZTitle("Z")

        grid_scale.SetVisibility(False)
        self.set_grid_scale(grid_scale)

        renderer.AddActor(grid_scale)

        renderWindowInteractor = vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(renderWindow)
        style = vtkInteractorStyleTrackball()
        renderWindowInteractor.SetInteractorStyle(style)
        renderWindowInteractor.EnableRenderOff()
        widget = vtkOrientationMarkerWidget()
        widget.SetInteractor(renderWindowInteractor)
        widget.SetViewport(0.8, 0.0, 1, 0.2)
        axes = vtkAxesActor()
        widget.SetOrientationMarker(axes)
        widget.EnabledOn()
        widget.InteractiveOff()

        self.set_axes(axes)
        self.set_widget(widget)
        ruler = RulerPipeline()
        ruler.add_to_renderer(renderer)
        self.set_ruler(ruler)

        renderer.SetBackground([180 / 255, 180 / 255, 180 / 255])

        renderer.ResetCamera()
        return schemas.ResetVisualizationResponse()

    @typed_rpc(viewer_prefix, schemas.set_background_color_route)
    def setBackgroundColor(
        self, params: schemas.SetBackgroundColor
    ) -> schemas.SetBackgroundColorResponse:
        color = params.color
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        renderer.SetBackground([color.r / 255, color.g / 255, color.b / 255])
        return schemas.SetBackgroundColorResponse()

    @typed_rpc(viewer_prefix, schemas.reset_camera_route)
    def resetCamera(self, params: schemas.ResetCamera) -> schemas.ResetCameraResponse:
        renderWindow = self.getView("-1")
        renderWindow.GetRenderers().GetFirstRenderer().ResetCamera()
        return schemas.ResetCameraResponse()

    @typed_rpc(viewer_prefix, schemas.take_screenshot_route)
    def takeScreenshot(
        self, params: schemas.TakeScreenshot
    ) -> schemas.TakeScreenshotResponse:
        renderWindow = self.getView("-1")

        w2if = vtkWindowToImageFilter()
        include_background = params.include_background
        if not include_background:
            renderWindow.SetAlphaBitPlanes(1)
            w2if.SetInputBufferTypeToRGBA()
        else:
            renderWindow.SetAlphaBitPlanes(0)
            w2if.SetInputBufferTypeToRGB()

        renderWindow.Render()

        w2if.SetInput(renderWindow)
        w2if.ReadFrontBufferOff()
        w2if.Update()
        output_extension = params.output_extension
        writer: vtkPNGWriter | vtkJPEGWriter
        if output_extension == schemas.take_screenshot.OutputExtension.PNG:
            writer = vtkPNGWriter()
        elif output_extension == schemas.take_screenshot.OutputExtension.JPG:
            if not include_background:
                raise ValueError("output_extension not supported with background")
            writer = vtkJPEGWriter()
        else:
            raise ValueError("output_extension not supported")

        new_filename = params.filename + "." + output_extension.value
        file_path = os.path.join(self.DATA_FOLDER_PATH, new_filename)
        writer.SetFileName(file_path)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()

        with open(file_path, "rb") as file:
            file_content = file.read()

        return schemas.TakeScreenshotResponse(blob=self.addAttachment(file_content))

    @typed_rpc(viewer_prefix, schemas.update_data_route)
    def updateData(self, params: schemas.UpdateData) -> schemas.UpdateDataResponse:
        data = self.get_vtk_pipeline(params.id)
        reader = data.reader
        reader.Update()
        mapper = data.mapper
        tag: Any = reference(0)
        output = reader.GetOutputDataObject(0)
        if not isinstance(output, vtkDataSet):
            raise TypeError("Output is not a vtkDataSet")

        scalars = vtkAbstractMapper.GetAbstractScalars(
            output,
            mapper.GetScalarMode(),
            mapper.GetArrayAccessMode(),
            mapper.GetArrayId(),
            mapper.GetArrayName(),
            tag,
        )
        mapper.SetScalarRange(scalars.GetRange())
        return schemas.UpdateDataResponse()

    @typed_rpc(viewer_prefix, schemas.get_point_position_route)
    def getPointPosition(
        self, params: schemas.GetPointPosition
    ) -> schemas.GetPointPositionResponse:
        renderer = self.get_renderer()
        # If clicking on an object
        prop_picker = vtkPropPicker()
        if prop_picker.Pick(params.x, params.y, 0.0, renderer):
            ppos = prop_picker.GetPickPosition()
            return schemas.GetPointPositionResponse(x=ppos[0], y=ppos[1], z=ppos[2])
        # WorldPicker if notclicking on an object
        world_picker = vtkWorldPointPicker()
        world_picker.Pick([params.x, params.y, 0.0], renderer)
        ppos = world_picker.GetPickPosition()
        return schemas.GetPointPositionResponse(x=ppos[0], y=ppos[1], z=ppos[2])

    @typed_rpc(viewer_prefix, schemas.pick_colormap_route)
    def pickColormap(
        self, params: schemas.PickColormap
    ) -> schemas.PickColormapResponse:

        renderWindow = self.getView("-1")
        size = renderWindow.GetSize()
        nx = params.x / size[0]
        ny = 1.0 - (params.y / size[1])

        for data_id, pipeline in self.get_data_base().items():
            bar = pipeline.scalarBar
            if bar.GetVisibility() and bar.GetLookupTable() is not None:
                pos = bar.GetPositionCoordinate()
                bx, by = pos.GetValue()[0], pos.GetValue()[1]
                w, h = bar.GetWidth(), bar.GetHeight()

                # Check if click falls within the scalar bar bounding box
                if bx <= nx <= bx + w and by <= ny <= by + h:
                    return schemas.PickColormapResponse(data_id=data_id)

        return schemas.PickColormapResponse()

    def computeEpsilon(self, renderer: vtkRenderer, z: float) -> float:
        renderer.SetDisplayPoint(0, 0, z)
        renderer.DisplayToWorld()
        windowLowerLeft = renderer.GetWorldPoint()
        size = renderer.GetRenderWindow().GetSize()
        renderer.SetDisplayPoint(size[0], size[1], z)
        renderer.DisplayToWorld()
        windowUpperRight = renderer.GetWorldPoint()
        epsilon: float = 0.0
        for i in range(3):
            epsilon += (windowUpperRight[i] - windowLowerLeft[i]) * (
                windowUpperRight[i] - windowLowerLeft[i]
            )
        return math.sqrt(epsilon) * 0.0125

    @typed_rpc(viewer_prefix, schemas.picked_ids_route)
    def pickedIds(self, params: schemas.PickedIDS) -> schemas.PickedIDSResponse:
        picker = vtkCellPicker(tolerance=0.005)
        # Retrieve all actors under the clicked coordinates
        actors, flat_index = self.pick_actors_under_coordinate(
            params.ids, params.x, params.y, picker
        )
        # Filter pipeline IDs whose actors are in the picked list
        array_ids = [
            data_id
            for data_id in params.ids
            if self.get_vtk_pipeline(data_id).actor in actors
        ]
        if not array_ids:
            return schemas.PickedIDSResponse(array_ids=[])
        viewer_id = flat_index if flat_index != -1 else None
        return schemas.PickedIDSResponse(array_ids=array_ids, viewer_id=viewer_id)

    @typed_rpc(viewer_prefix, schemas.grid_scale_route)
    def toggleGridScale(self, params: schemas.GridScale) -> schemas.GridScaleResponse:
        grid_scale = self.get_grid_scale()
        if grid_scale is not None:
            grid_scale.SetVisibility(params.visibility)
        return schemas.GridScaleResponse()

    @typed_rpc(viewer_prefix, schemas.axes_route)
    def toggleAxes(self, params: schemas.Axes) -> schemas.AxesResponse:
        axes = self.get_axes()
        if axes is not None:
            axes.SetVisibility(params.visibility)
        return schemas.AxesResponse()

    @typed_rpc(viewer_prefix, schemas.update_camera_route)
    def updateCamera(
        self, params: schemas.UpdateCamera
    ) -> schemas.UpdateCameraResponse:
        camera_options = params.camera_options

        renderWindow = self.getView("-1")
        camera = renderWindow.GetRenderers().GetFirstRenderer().GetActiveCamera()

        camera.SetFocalPoint(camera_options.focal_point)
        camera.SetViewUp(camera_options.view_up)
        camera.SetPosition(camera_options.position)
        camera.SetViewAngle(camera_options.view_angle)
        camera.SetClippingRange(camera_options.clipping_range)
        ruler = self.get_ruler()
        if ruler is not None:
            ruler.update_scale(self.get_renderer())
        return schemas.UpdateCameraResponse()

    @typed_rpc(viewer_prefix, schemas.render_route)
    def renderNow(self, params: schemas.Render) -> schemas.RenderResponse:
        self.render()
        return schemas.RenderResponse()

    @typed_rpc(viewer_prefix, schemas.highlight_route)
    def setHighlight(self, params: schemas.Highlight) -> schemas.HighlightResponse:
        # Clear previous highlights
        self.clear_highlights(params.ids)
        picker = vtkCellPicker(tolerance=0.005)
        # Perform pick operation to identify clicked pipeline and primitive ID
        data_id, id_to_select = self.pick_cell_or_point(
            params.ids, params.x, params.y, params.field_type.value, picker
        )
        if not data_id or id_to_select == -1:
            self.render(-1)
            return schemas.HighlightResponse()
        # Retrieve picked composite block information
        pipeline = self.get_vtk_pipeline(data_id)
        dataset, geode_id = self.get_composite_block_info(pipeline, picker)
        # Update highlight visibility and extract attributes from the picked element
        self.update_highlight(pipeline, id_to_select, params.field_type.value, dataset)
        self.render(-1)
        data_attributes = self.extract_picked_attributes(
            pipeline, id_to_select, params.field_type.value, dataset
        )
        return schemas.HighlightResponse(
            id=data_id,
            picked_id=id_to_select,
            field_type=schemas.highlight.PickedFieldType(params.field_type.value),
            geode_id=geode_id,
            attributes=data_attributes,
        )

    @typed_rpc(viewer_prefix, schemas.clipping_planes_route)
    def setClippingPlanes(
        self, params: schemas.ClippingPlanes
    ) -> schemas.ClippingPlanesResponse:
        self.set_clipping_planes(params.ids, params.planes)
        return schemas.ClippingPlanesResponse()

    @typed_rpc(viewer_prefix, schemas.shrink_route)
    def setShrink(self, params: schemas.Shrink) -> schemas.ShrinkResponse:
        self.set_shrink(params.ids, params.shrink_factor)
        return schemas.ShrinkResponse()

    @typed_rpc(viewer_prefix, schemas.explode_route)
    def setExplode(self, params: schemas.Explode) -> schemas.ExplodeResponse:
        self.set_explode(params.ids, params.explode_factor)
        return schemas.ExplodeResponse()

    @typed_rpc(viewer_prefix, schemas.slice_route)
    def setSlice(self, params: schemas.Slice) -> schemas.SliceResponse:
        return schemas.SliceResponse(
            max_indices=self.set_slice(params.ids, params.slices)
        )

    @typed_rpc(viewer_prefix, schemas.threshold_route)
    def setThreshold(self, params: schemas.Threshold) -> schemas.ThresholdResponse:
        self.set_threshold(params.ids, params.attribute)
        return schemas.ThresholdResponse()

    @typed_rpc(viewer_prefix, schemas.set_z_scaling_route)
    def setZScaling(self, params: schemas.SetZScaling) -> schemas.SetZScalingResponse:
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        cam = renderer.GetActiveCamera()
        transform = vtkTransform()
        transform.Scale(1, 1, params.z_scale)
        cam.SetModelTransformMatrix(transform.GetMatrix())
        grid_scale = self.get_grid_scale()
        if grid_scale is not None:
            grid_scale.SetUse2DMode(True)
        return schemas.SetZScalingResponse()

    @typed_rpc(viewer_prefix, schemas.preview_points_route)
    def previewPoints(
        self, params: schemas.PreviewPoints
    ) -> schemas.PreviewPointsResponse:
        points_data = params.points
        style_name = (
            params.style.value if hasattr(params.style, "value") else params.style
        )

        if not points_data:
            if self._preview_actor is not None:
                self.get_renderer().RemoveActor(self._preview_actor)
                self._preview_actor = None
                self.render(-1)
            return schemas.PreviewPointsResponse()
        if self._preview_actor is None:
            self._preview_points = vtkPoints()
            self._preview_verts = vtkCellArray()
            self._preview_polydata = vtkPolyData()
            self._preview_polydata.SetPoints(self._preview_points)
            self._preview_polydata.SetVerts(self._preview_verts)
            self._preview_mapper = vtkDataSetMapper()
            self._preview_mapper.SetInputData(self._preview_polydata)
            self._preview_mapper.ScalarVisibilityOn()
            self._preview_mapper.SetColorModeToDirectScalars()
            self._preview_actor = vtkActor()
            self._preview_actor.SetMapper(self._preview_mapper)
            prop = self._preview_actor.GetProperty()
            prop.SetPointSize(10)
            prop.SetLineWidth(2)
            self.get_renderer().AddActor(self._preview_actor)

        self._preview_points.Reset()
        self._preview_verts.Reset()

        colors = vtkUnsignedCharArray()
        colors.SetName("Colors")
        colors.SetNumberOfComponents(3)

        for i, pt in enumerate(points_data):
            self._preview_points.InsertNextPoint(pt.x, pt.y, pt.z)
            self._preview_verts.InsertNextCell(1, [i])
            if style_name in ["curve", "surface"] and i == 0:
                colors.InsertNextTuple3(60, 153, 131)
            else:
                colors.InsertNextTuple3(102, 102, 102)

        self._preview_polydata.GetPointData().SetScalars(colors)
        self._preview_polydata.GetPointData().SetActiveScalars("Colors")

        lines = vtkCellArray()
        polys = vtkCellArray()
        if style_name == "curve":
            for i in range(len(points_data) - 1):
                lines.InsertNextCell(2, [i, i + 1])
            if params.closed and len(points_data) >= 2:
                lines.InsertNextCell(2, [len(points_data) - 1, 0])
        elif style_name == "surface":
            for i in range(len(points_data) - 1):
                lines.InsertNextCell(2, [i, i + 1])
            if len(points_data) >= 3:
                lines.InsertNextCell(2, [len(points_data) - 1, 0])
                polys.InsertNextCell(len(points_data), list(range(len(points_data))))

        self._preview_polydata.SetLines(lines)
        self._preview_polydata.SetPolys(polys)
        self._preview_polydata.Modified()
        self.render(-1)
        return schemas.PreviewPointsResponse()

    @typed_rpc(viewer_prefix, schemas.ruler_route)
    def setRuler(self, params: schemas.Ruler) -> schemas.RulerResponse:
        ruler = self.get_ruler()
        assert ruler is not None
        point1 = params.points[0]
        point2 = params.points[1] if len(params.points) > 1 else None
        distance = ruler.set_endpoints(point1, point2, renderer=self.get_renderer())
        return schemas.RulerResponse(distance=distance, point1=point1, point2=point2)

    @typed_rpc(viewer_prefix, schemas.reset_ruler_route)
    def resetRuler(self, params: schemas.ResetRuler) -> schemas.ResetRulerResponse:
        ruler = self.get_ruler()
        assert ruler is not None
        ruler.reset()
        return schemas.ResetRulerResponse()
