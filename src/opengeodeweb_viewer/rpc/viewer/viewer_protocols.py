# Standard library imports
import math
import os

# Third party imports
import vtk
from vtkmodules.vtkIOImage import vtkPNGWriter, vtkJPEGWriter
from vtkmodules.vtkRenderingCore import vtkWindowToImageFilter
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.vtk_protocol import VtkView


class VtkViewerView(VtkView):
    viewer_prefix = "opengeodeweb_viewer.viewer."
    viewer_schemas_dict = get_schemas_dict(
        os.path.join(os.path.dirname(__file__), "schemas")
    )

    def __init__(self):
        super().__init__()

    @exportRpc(viewer_prefix + viewer_schemas_dict["create_visualization"]["rpc"])
    def createVisualization(self, params):
        validate_schema(
            params, self.viewer_schemas_dict["create_visualization"], self.viewer_prefix
        )
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        renderer.SetBackground([180 / 255, 180 / 255, 180 / 255])
        renderer.ResetCamera()
        renderWindow.Render()
        self.render()

    @exportRpc(viewer_prefix + viewer_schemas_dict["set_background_color"]["rpc"])
    def setBackgroundColor(self, params):
        validate_schema(
            params, self.viewer_schemas_dict["set_background_color"], self.viewer_prefix
        )
        red, green, blue = (
            params["color"]["r"],
            params["color"]["g"],
            params["color"]["b"],
        )
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        renderer.SetBackground([red, green, blue])
        renderer.ResetCamera()
        renderWindow.Render()
        self.render()

    @exportRpc(viewer_prefix + viewer_schemas_dict["reset_camera"]["rpc"])
    def resetCamera(self, params):
        validate_schema(
            params, self.viewer_schemas_dict["reset_camera"], self.viewer_prefix
        )
        renderWindow = self.getView("-1")
        renderWindow.GetRenderers().GetFirstRenderer().ResetCamera()
        renderWindow.Render()
        self.render()

    @exportRpc(viewer_prefix + viewer_schemas_dict["take_screenshot"]["rpc"])
    def takeScreenshot(self, params):
        validate_schema(
            params, self.viewer_schemas_dict["take_screenshot"], self.viewer_prefix
        )

        filename, output_extension, include_background = (
            params["filename"],
            params["output_extension"],
            params["include_background"],
        )
        renderWindow = self.getView("-1")
        renderer = self.get_renderer()

        w2if = vtkWindowToImageFilter()

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

        if output_extension == "png":
            writer = vtkPNGWriter()
        elif output_extension in ["jpg", "jpeg"]:
            if not include_background:
                raise Exception("output_extension not supported with background")
            writer = vtkJPEGWriter()
        else:
            raise Exception("output_extension not supported")

        new_filename = filename + "." + output_extension
        file_path = os.path.join(self.DATA_FOLDER_PATH, new_filename)
        writer.SetFileName(file_path)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()

        with open(file_path, "rb") as file:
            file_content = file.read()

        return {"blob": self.addAttachment(file_content)}

    @exportRpc(viewer_prefix + viewer_schemas_dict["update_data"]["rpc"])
    def updateData(self, params):
        validate_schema(
            params, self.viewer_schemas_dict["update_data"], self.viewer_prefix
        )
        id = params["id"]

        data = self.get_object(id)
        reader = data["reader"]
        reader.Update()
        mapper = data["mapper"]
        tag = vtk.reference(0)
        scalars = vtk.vtkAbstractMapper.GetAbstractScalars(
            reader.GetOutput(),
            mapper.GetScalarMode(),
            mapper.GetArrayAccessMode(),
            mapper.GetArrayId(),
            mapper.GetArrayName(),
            tag,
        )
        mapper.SetScalarRange(scalars.GetRange())
        self.render()

    @exportRpc(viewer_prefix + viewer_schemas_dict["get_point_position"]["rpc"])
    def getPointPosition(self, params):
        validate_schema(
            params, self.viewer_schemas_dict["get_point_position"], self.viewer_prefix
        )
        x = float(params["x"])
        y = float(params["y"])
        xyz = [x, y, 0.0]
        picker = vtk.vtkWorldPointPicker()
        picker.Pick(xyz, self.get_renderer())
        ppos = picker.GetPickPosition()
        return {"x": ppos[0], "y": ppos[1], "z": ppos[2]}

    @exportRpc(viewer_prefix + viewer_schemas_dict["reset"]["rpc"])
    def reset(self, params):
        validate_schema(params, self.viewer_schemas_dict["reset"], self.viewer_prefix)
        renderWindow = self.getView("-1")
        renderWindow.GetRenderers().GetFirstRenderer().RemoveAllViewProps()

    def computeEpsilon(self, renderer, z):
        renderer.SetDisplayPoint(0, 0, z)
        renderer.DisplayToWorld()
        windowLowerLeft = renderer.GetWorldPoint()
        size = renderer.GetRenderWindow().GetSize()
        renderer.SetDisplayPoint(size[0], size[1], z)
        renderer.DisplayToWorld()
        windowUpperRight = renderer.GetWorldPoint()
        epsilon = 0
        for i in range(3):
            epsilon += (windowUpperRight[i] - windowLowerLeft[i]) * (
                windowUpperRight[i] - windowLowerLeft[i]
            )
        return math.sqrt(epsilon) * 0.0125

    @exportRpc(viewer_prefix + viewer_schemas_dict["picked_ids"]["rpc"])
    def pickedIds(self, params):
        validate_schema(
            params, self.viewer_schemas_dict["picked_ids"], self.viewer_prefix
        )
        x, y, ids = params["x"], params["y"], params["ids"]

        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        picker = vtk.vtkWorldPointPicker()
        picker.Pick([x, y, 0], renderer)
        point = picker.GetPickPosition()
        epsilon = self.computeEpsilon(renderer, point[2])
        bbox = vtk.vtkBoundingBox()
        bbox.AddPoint(point[0] + epsilon, point[1] + epsilon, point[2] + epsilon)
        bbox.AddPoint(point[0] - epsilon, point[1] - epsilon, point[2] - epsilon)

        array_ids = []
        for id in ids:
            bounds = self.get_object(id)["actor"].GetBounds()
            if bbox.Intersects(bounds):
                array_ids.append(id)

        return {"array_ids": array_ids}
