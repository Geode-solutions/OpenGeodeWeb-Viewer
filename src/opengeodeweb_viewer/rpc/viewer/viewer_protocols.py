# Standard library imports
import math
import os
from typing import cast, Any

# Third party imports
from wslink import register as exportRpc  # type: ignore
from vtkmodules.vtkIOImage import vtkPNGWriter, vtkJPEGWriter
from vtkmodules.vtkRenderingAnnotation import vtkCubeAxesActor, vtkAxesActor
from vtkmodules.vtkRenderingCore import (
    vtkWindowToImageFilter,
    vtkRenderer,
    vtkRenderWindowInteractor,
    vtkAbstractMapper,
    vtkWorldPointPicker,
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackball
from vtkmodules.vtkCommonCore import reference
from vtkmodules.vtkCommonDataModel import vtkBoundingBox, vtkDataSet
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from opengeodeweb_microservice.schemas import get_schemas_dict

# Local application imports
from opengeodeweb_viewer.utils_functions import (
    validate_schema,
    RpcParams,
)
from opengeodeweb_viewer.vtk_protocol import VtkView
from . import schemas


class VtkViewerView(VtkView):
    viewer_prefix = "opengeodeweb_viewer.viewer."
    viewer_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self) -> None:
        super().__init__()

    @exportRpc(viewer_prefix + viewer_schemas_dict["reset_visualization"]["rpc"])
    def resetVisualization(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.viewer_schemas_dict["reset_visualization"],
            self.viewer_prefix,
        )
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

        renderer.SetBackground([180 / 255, 180 / 255, 180 / 255])

        renderer.ResetCamera()

    @exportRpc(viewer_prefix + viewer_schemas_dict["set_background_color"]["rpc"])
    def setBackgroundColor(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params,
            self.viewer_schemas_dict["set_background_color"],
            self.viewer_prefix,
        )
        params = schemas.SetBackgroundColor.from_dict(rpc_params)
        color = params.color
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        renderer.SetBackground([color.r / 255, color.g / 255, color.b / 255])

    @exportRpc(viewer_prefix + viewer_schemas_dict["reset_camera"]["rpc"])
    def resetCamera(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.viewer_schemas_dict["reset_camera"], self.viewer_prefix
        )
        renderWindow = self.getView("-1")
        renderWindow.GetRenderers().GetFirstRenderer().ResetCamera()

    @exportRpc(viewer_prefix + viewer_schemas_dict["take_screenshot"]["rpc"])
    def takeScreenshot(self, rpc_params: RpcParams) -> dict[str, str | bytes]:
        validate_schema(
            rpc_params, self.viewer_schemas_dict["take_screenshot"], self.viewer_prefix
        )
        params = schemas.TakeScreenshot.from_dict(rpc_params)
        renderWindow = self.getView("-1")
        renderer = self.get_renderer()

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
        if output_extension == schemas.OutputExtension.PNG:
            writer = vtkPNGWriter()
        elif output_extension == schemas.OutputExtension.JPG:
            if not include_background:
                raise Exception("output_extension not supported with background")
            writer = vtkJPEGWriter()
        else:
            raise Exception("output_extension not supported")

        new_filename = params.filename + "." + output_extension.value
        file_path = os.path.join(self.DATA_FOLDER_PATH, new_filename)
        writer.SetFileName(file_path)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()

        with open(file_path, "rb") as file:
            file_content = file.read()

        return {"blob": self.addAttachment(file_content)}

    @exportRpc(viewer_prefix + viewer_schemas_dict["update_data"]["rpc"])
    def updateData(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.viewer_schemas_dict["update_data"], self.viewer_prefix
        )
        params = schemas.UpdateData.from_dict(rpc_params)
        data = self.get_object(params.id)
        reader = data.reader
        reader.Update()
        mapper = data.mapper
        tag: Any = reference(0)
        output = reader.GetOutputDataObject(0)
        if not isinstance(output, vtkDataSet):
            raise Exception("Output is not a vtkDataSet")

        scalars = vtkAbstractMapper.GetAbstractScalars(
            output,
            mapper.GetScalarMode(),
            mapper.GetArrayAccessMode(),
            mapper.GetArrayId(),
            mapper.GetArrayName(),
            tag,
        )
        mapper.SetScalarRange(scalars.GetRange())

    @exportRpc(viewer_prefix + viewer_schemas_dict["get_point_position"]["rpc"])
    def getPointPosition(self, rpc_params: RpcParams) -> dict[str, float]:
        validate_schema(
            rpc_params,
            self.viewer_schemas_dict["get_point_position"],
            self.viewer_prefix,
        )
        params = schemas.GetPointPosition.from_dict(rpc_params)
        xyz = [params.x, params.y, 0.0]
        picker = vtkWorldPointPicker()
        picker.Pick(xyz, self.get_renderer())
        ppos = picker.GetPickPosition()
        return {"x": ppos[0], "y": ppos[1], "z": ppos[2]}

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

    @exportRpc(viewer_prefix + viewer_schemas_dict["picked_ids"]["rpc"])
    def pickedIds(self, rpc_params: RpcParams) -> dict[str, list[str]]:
        validate_schema(
            rpc_params, self.viewer_schemas_dict["picked_ids"], self.viewer_prefix
        )
        params = schemas.PickedIDS.from_dict(rpc_params)
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        picker = vtkWorldPointPicker()
        picker.Pick([params.x, params.y, 0], renderer)
        point = picker.GetPickPosition()
        epsilon = self.computeEpsilon(renderer, point[2])
        bbox = vtkBoundingBox()
        bbox.AddPoint(point[0] + epsilon, point[1] + epsilon, point[2] + epsilon)
        bbox.AddPoint(point[0] - epsilon, point[1] - epsilon, point[2] - epsilon)

        array_ids = []
        for id in params.ids:
            bounds = self.get_object(id).actor.GetBounds()
            bounds_box = vtkBoundingBox(bounds)
            if bbox.Intersects(bounds_box):
                array_ids.append(id)

        return {"array_ids": array_ids}

    @exportRpc(viewer_prefix + viewer_schemas_dict["grid_scale"]["rpc"])
    def toggleGridScale(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.viewer_schemas_dict["grid_scale"], self.viewer_prefix
        )
        params = schemas.GridScale.from_dict(rpc_params)
        grid_scale = self.get_grid_scale()
        if grid_scale is not None:
            grid_scale.SetVisibility(params.visibility)

    @exportRpc(viewer_prefix + viewer_schemas_dict["axes"]["rpc"])
    def toggleAxes(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.viewer_schemas_dict["axes"], self.viewer_prefix
        )
        params = schemas.Axes.from_dict(rpc_params)
        axes = self.get_axes()
        if axes is not None:
            axes.SetVisibility(params.visibility)

    @exportRpc(viewer_prefix + viewer_schemas_dict["update_camera"]["rpc"])
    def updateCamera(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.viewer_schemas_dict["update_camera"], self.viewer_prefix
        )
        params = schemas.UpdateCamera.from_dict(rpc_params)
        camera_options = params.camera_options

        renderWindow = self.getView("-1")
        camera = renderWindow.GetRenderers().GetFirstRenderer().GetActiveCamera()

        camera.SetFocalPoint(camera_options.focal_point)
        camera.SetViewUp(camera_options.view_up)
        camera.SetPosition(camera_options.position)
        camera.SetViewAngle(camera_options.view_angle)
        camera.SetClippingRange(camera_options.clipping_range)

    @exportRpc(viewer_prefix + viewer_schemas_dict["render"]["rpc"])
    def renderNow(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.viewer_schemas_dict["render"], self.viewer_prefix
        )
        self.render()

    @exportRpc(viewer_prefix + viewer_schemas_dict["set_z_scaling"]["rpc"])
    def setZScaling(self, rpc_params: RpcParams) -> None:
        validate_schema(
            rpc_params, self.viewer_schemas_dict["set_z_scaling"], self.viewer_prefix
        )
        params = schemas.SetZScaling.from_dict(rpc_params)
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        cam = renderer.GetActiveCamera()
        transform = vtkTransform()
        transform.Scale(1, 1, params.z_scale)
        cam.SetModelTransformMatrix(transform.GetMatrix())
        grid_scale = self.get_grid_scale()
        if grid_scale is not None:
            grid_scale.SetUse2DMode(True)
