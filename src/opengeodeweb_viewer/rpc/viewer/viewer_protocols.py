# Standard library imports
import json
import os
from pathlib import Path

# Third party imports
import vtk
from vtk.web import protocols as vtk_protocols
from vtkmodules.vtkIOImage import vtkPNGWriter, vtkJPEGWriter
from vtkmodules.vtkRenderingCore import (vtkWindowToImageFilter)
from wslink import register as exportRpc

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.vtk_protocol import VtkView

schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
schemas_dict = get_schemas_dict(schemas_dir)

class VtkViewerView(VtkView):
    def __init__(self):
        super().__init__()

    @exportRpc(schemas_dict["create_visualization"]["rpc"])
    def createVisualization(self, params):
        validate_schema(params, schemas_dict["create_visualization"])
        renderWindow = super().getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        renderer.SetBackground([180 / 255, 180 / 255, 180 / 255])
        renderer.ResetCamera()
        renderWindow.Render()
        super().render()

    @exportRpc(schemas_dict["set_background_color"]["rpc"])
    def setBackgroundColor(self, params):
        validate_schema(params, schemas_dict["set_background_color"])
        renderWindow = super().getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        red = params["red"]
        green = params["green"]
        blue = params["blue"]

        renderer.SetBackground([red, green, blue])
        renderer.ResetCamera()
        renderWindow.Render()
        super().render()

    @exportRpc(schemas_dict["reset_camera"]["rpc"])
    def resetCamera(self, params):
        print(f"{params=}", flush=True)
        validate_schema(params, schemas_dict["reset_camera"])
        renderWindow = super().getView("-1")
        renderWindow.GetRenderers().GetFirstRenderer().ResetCamera()
        renderWindow.Render()
        super().render()

    @exportRpc(schemas_dict["take_screenshot"]["rpc"])
    def takeScreenshot(self, params):
        validate_schema(params, schemas_dict["take_screenshot"])
        print(f"{params=}", flush=True)
        filename = params["filename"]
        output_extension = params["output_extension"]
        include_background = params["include_background"]
        renderWindow = super().getView("-1")
        renderer = super().get_renderer()

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

        new_filename = filename + '.' + output_extension
        file_path = os.path.join(self.DATA_FOLDER_PATH, new_filename)
        writer.SetFileName(file_path)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()

        with open(file_path, "rb") as file:
            file_content = file.read()

        return {"blob": self.addAttachment(file_content)}


    @exportRpc(schemas_dict["update_data"]["rpc"])
    def updateData(self, params):
        validate_schema(params, schemas_dict["update_data"])
        print(f"{params=}", flush=True)
        id = params["id"]

        data = super().get_object(id)
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
        super().render()

    @exportRpc(schemas_dict["get_point_position"]["rpc"])
    def getPointPosition(self, params):
        validate_schema(params, schemas_dict["get_point_position"])
        x = float(params["x"])
        y = float(params["y"])
        xyz = [x, y, 0.0]
        picker = vtk.vtkWorldPointPicker()
        picker.Pick(xyz, super().get_renderer())
        ppos = picker.GetPickPosition()
        return {"x": ppos[0], "y": ppos[1], "z": ppos[2]}

    @exportRpc(schemas_dict["reset"]["rpc"])
    def reset(self, params):
        validate_schema(params, schemas_dict["reset"])
        renderWindow = super().getView("-1")
        renderWindow.GetRenderers().GetFirstRenderer().RemoveAllViewProps()
