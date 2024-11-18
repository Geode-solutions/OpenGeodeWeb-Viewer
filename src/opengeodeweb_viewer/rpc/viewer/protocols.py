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

    @exportRpc(schemas_dict["create_visualization"]["rpc"])
    def create_visualization(self, params):
        validate_schema(params, schemas_dict["create_visualization"])
        renderWindow = super().getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        renderer.SetBackground([180 / 255, 180 / 255, 180 / 255])
        renderer.ResetCamera()
        renderWindow.Render()
        super().render()

    @exportRpc(schemas_dict["set_viewer_background_color"]["rpc"])
    def set_viewer_background_color(self, params):
        validate_schema(params, schemas_dict["set_viewer_background_color"])
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
    def reset_camera(self, params):
        print(f"{params=}", flush=True)
        validate_schema(params, schemas_dict["reset_camera"])
        renderWindow = super().getView("-1")
        renderWindow.GetRenderers().GetFirstRenderer().ResetCamera()
        renderWindow.Render()
        super().render()

    @exportRpc(schemas_dict["create_object_pipeline"]["rpc"])
    def create_object_pipeline(self, params):
        validate_schema(params, schemas_dict["create_object_pipeline"])
        try:
            id = params["id"]
            file_name = params["file_name"]
            FOLDER_PATH = os.path.dirname(__file__)

            actor = vtk.vtkActor()
            if ".vtm" in file_name:
                reader = vtk.vtkXMLMultiBlockDataReader()
                filter = vtk.vtkGeometryFilter()
                filter.SetInputConnection(reader.GetOutputPort())
                mapper = vtk.vtkCompositePolyDataMapper()
                mapper.SetInputConnection(filter.GetOutputPort())
            else:
                reader = vtk.vtkXMLGenericDataObjectReader()
                filter = {}
                mapper = vtk.vtkDataSetMapper()
                mapper.SetInputConnection(reader.GetOutputPort())
                
            super().register_object(id, reader, filter, actor, mapper, {})

            reader.SetFileName(os.path.join(super().DATA_FOLDER_PATH, file_name))

            actor.SetMapper(mapper)
            mapper.SetColorModeToMapScalars()
            mapper.SetResolveCoincidentTopologyLineOffsetParameters(1, -0.1)
            mapper.SetResolveCoincidentTopologyPolygonOffsetParameters(2, 0)
            mapper.SetResolveCoincidentTopologyPointOffsetParameter(-2)

            renderWindow = super().getView("-1")
            renderer = renderWindow.GetRenderers().GetFirstRenderer()
            renderer.AddActor(actor)
            renderer.ResetCamera()
            renderWindow.Render()
            super().render()
        except Exception as e:
            print("error : ", str(e), flush=True)

    @exportRpc(schemas_dict["delete_object_pipeline"]["rpc"])
    def delete_object_pipeline(self, params):
        validate_schema(params, schemas_dict["delete_object_pipeline"])
        print(f"{params=}", flush=True)
        id = params["id"]
        object = super().get_object(id)
        actor = object["actor"]
        renderWindow = super().getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        renderer.RemoveActor(actor)
        print(f"{object=}", flush=True)
        super().deregister_object(id)
        super().render()

    @exportRpc(schemas_dict["toggle_object_visibility"]["rpc"])
    def toggle_object_visibility(self, params):
        validate_schema(params, schemas_dict["toggle_object_visibility"])
        print(f"{params=}", flush=True)
        id = params["id"]
        is_visible = params["is_visible"]
        object = super().get_object(id)
        actor = object["actor"]
        actor.SetVisibility(is_visible)
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
        file_path = os.path.join(super().DATA_FOLDER_PATH, new_filename)
        writer.SetFileName(file_path)
        writer.SetInputConnection(w2if.GetOutputPort())
        writer.Write()

        with open(file_path, "rb") as file:
            file_content = file.read()

        return {"blob": super().addAttachment(file_content)}


    

    @exportRpc(schemas_dict["apply_textures"]["rpc"])
    def apply_textures(self, params):
        validate_schema(params, schemas_dict["apply_textures"])
        print(f"{params=}", flush=True)
        id = params["id"]
        textures = params["textures"]
        textures_array = []
        images_reader_array = []

        data = super().get_object(id)
        mapper = data["mapper"]
        actor = data["actor"]
        reader = data["reader"]

        polydata_mapper = mapper.GetPolyDataMapper()
        poly_data = reader.GetPolyDataOutput()

        for index, value in enumerate(textures):
            texture_name = value["texture_name"]
            texture_file_name = value["texture_file_name"]
            print(f"{texture_name=} {texture_file_name=}", flush=True)

            new_texture = vtk.vtkTexture()
            image_reader = vtk.vtkXMLImageDataReader()
            image_reader.SetFileName(
                os.path.join(super().DATA_FOLDER_PATH, texture_file_name)
            )

            shader_texture_name = f"VTK_TEXTURE_UNIT_{index}"
            polydata_mapper.MapDataArrayToMultiTextureAttribute(
                shader_texture_name,
                texture_name,
                vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
            )

            if index == 0:
                new_texture.SetBlendingMode(
                    vtk.vtkTexture.VTK_TEXTURE_BLENDING_MODE_REPLACE
                )
            else:
                new_texture.SetBlendingMode(
                    vtk.vtkTexture.VTK_TEXTURE_BLENDING_MODE_ADD
                )

            images_reader_array.append(image_reader)
            new_texture.SetInputConnection(image_reader.GetOutputPort())

            actor.GetProperty().SetTexture(shader_texture_name, new_texture)

            textures_array.append(new_texture)
            images_reader_array.append(image_reader)

        super().render()

    @exportRpc(schemas_dict["update_data"]["rpc"])
    def update_data(self, params):
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
    def get_point_position(self, params):
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

    @exportRpc(schemas_dict["set_opacity"]["rpc"])
    def set_opacity(self, params):
        validate_schema(params, schemas_dict["set_opacity"])
        id = params["id"]
        opacity = float(params["opacity"])
        actor = super().get_object(id)["actor"]
        actor.GetProperty().SetOpacity(opacity)
        super().render()

    @exportRpc(schemas_dict["toggle_edge_visibility"]["rpc"])
    def setEdgeVisibility(self, params):
        validate_schema(params, schemas_dict["toggle_edge_visibility"])
        print(f"{params=}", flush=True)
        id = str(params["id"])
        visibility = bool(params["visibility"])
        actor = super().get_object(id)["actor"]
        actor.GetProperty().SetEdgeVisibility(visibility)
        super().render()

    @exportRpc(schemas_dict["toggle_point_visibility"]["rpc"])
    def setPointVisibility(self, params):
        validate_schema(params, schemas_dict["toggle_point_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        actor = super().get_object(id)["actor"]
        actor.GetProperty().SetVertexVisibility(visibility)
        super().render()

    @exportRpc(schemas_dict["set_point_size"]["rpc"])
    def setPointSize(self, params):
        validate_schema(params, schemas_dict["set_point_size"])
        id = params["id"]
        size = float(params["size"])
        print(f"{size=}", flush=True)
        actor = super().get_object(id)["actor"]
        actor.GetProperty().SetPointSize(size)
        super().render()

    @exportRpc(schemas_dict["set_color"]["rpc"])
    def setColor(self, params):
        validate_schema(params, schemas_dict["set_color"])
        id = params["id"]
        red = params["red"]
        green = params["green"]
        blue = params["blue"]
        super().get_object(id)["mapper"].ScalarVisibilityOff()
        actor = super().get_object(id)["actor"]
        actor.GetProperty().SetColor(red, green, blue)
        super().render()