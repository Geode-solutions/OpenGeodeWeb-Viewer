from vtk.web import protocols as vtk_protocols
from wslink import register as exportRpc

import vtk


class VtkView(vtk_protocols.vtkWebProtocol):
    def __init__(self):
        self.DataReader = vtk.vtkXMLPolyDataReader()
        self.ImageReader = vtk.vtkXMLImageDataReader()

    @exportRpc("create_visualization")
    def create_visualization(self):
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        renderer.SetBackground([180 / 255, 180 / 255, 180 / 255])

        renderer.ResetCamera()
        renderWindow.Render()

        return self.reset_camera()

    @exportRpc("reset_camera")
    def reset_camera(self):
        renderWindow = self.getView("-1")
        renderWindow.GetRenderers().GetFirstRenderer().ResetCamera()
        renderWindow.Render()

        return -1

    @exportRpc("create_object_pipeline")
    def create_object_pipeline(self, params):
        try:
            print(f"{params=}", flush=True)
            id = params["id"]
            file_name = params["file_name"]

            actor = vtk.vtkActor()
            mapper = vtk.vtkDataSetMapper()
            actor.SetMapper(mapper)
            if ".vtm" in file_name:
                reader = vtk.vtkXMLMultiBlockDataReader()
                filter = vtk.vtkCompositeDataGeometryFilter()
                filter.SetInputConnection(reader.GetOutputPort())
                mapper.SetInputConnection(filter.GetOutputPort())
                self.register_object(id, reader, filter, actor, mapper, {})
            else:
                reader = vtk.vtkXMLGenericDataObjectReader()
                mapper.SetInputConnection(reader.GetOutputPort())
                self.register_object(id, reader, {}, actor, mapper, {})

            reader.SetFileName(f"/data/{file_name}")

            mapper.SetColorModeToMapScalars()
            mapper.SetResolveCoincidentTopologyLineOffsetParameters(1, -0.1)
            mapper.SetResolveCoincidentTopologyPolygonOffsetParameters(2, 0)
            mapper.SetResolveCoincidentTopologyPointOffsetParameter(-2)

            renderWindow = self.getView("-1")
            renderer = renderWindow.GetRenderers().GetFirstRenderer()
            renderer.AddActor(actor)

            renderer.ResetCamera()

            self.render()
        except Exception as e:
            print("error : ", str(e), flush=True)

    @exportRpc("toggle_object_visibility")
    def toggle_object_visibility(self, params):
        print(f"{params=}", flush=True)
        id = params["id"]
        is_visible = params["is_visible"]
        object = self.get_object(id)
        actor = object["actor"]
        actor.SetVisibility(is_visible)
        self.render()

    @exportRpc("apply_textures")
    def apply_textures(self, params):
        print(f"{params=}", flush=True)
        id = params["id"]
        textures = params["textures"]
        textures_array = []
        images_reader_array = []

        data = self.get_object(id)
        mapper = data["mapper"]
        actor = data["actor"]
        reader = data["reader"]

        polydata_mapper = mapper.GetPolyDataMapper()
        poly_data = reader.GetPolyDataOutput()

        for index, value in enumerate(textures):
            texture_name = value["texture_name"]["value"]
            texture_file_name = value["texture_file_name"]["value"]

            new_texture = vtk.vtkTexture()
            image_reader = vtk.vtkXMLImageDataReader()
            image_reader.SetFileName(f"/data/{texture_file_name}")

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

        self.render()

    @exportRpc("update_data")
    def update_data(self, params):
        print(f"{params=}", flush=True)
        id = params["id"]

        data = self.get_object(id)
        reader = data["reader"]
        reader.Modified()

        self.render()

    @exportRpc("get_point_position")
    def get_point_position(self, params):
        x = float(params["x"])
        y = float(params["y"])
        print(f"{x=}", flush=True)
        print(f"{y=}", flush=True)
        xyz = [x, y, 0.0]
        picker = vtk.vtkWorldPointPicker()
        picker.Pick(xyz, self.get_renderer())
        ppos = picker.GetPickPosition()
        return {"x": ppos[0], "y": ppos[1], "z": ppos[2]}

    @exportRpc("reset")
    def reset(self):
        renderWindow = self.getView("-1")
        renderWindow.GetRenderers().GetFirstRenderer().RemoveAllViewProps()
        print("reset")

    @exportRpc("toggle_edge_visibility")
    def setEdgeVisibility(self, params):
        print(f"{params=}", flush=True)
        id = params["id"]
        visibility = bool(params["visibility"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetEdgeVisibility(visibility)
        self.render()

    @exportRpc("toggle_point_visibility")
    def setPointVisibility(self, params):
        id = params["id"]
        visibility = bool(params["visibility"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetVertexVisibility(visibility)
        self.render()

    @exportRpc("point_size")
    def setPointSize(self, params):
        id = params["id"]
        size = float(params["size"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetPointSize(size)
        self.render()

    def getProtocol(self, name):
        for p in self.coreServer.getLinkProtocols():
            if type(p).__name__ == name:
                return p

    def render(self, view=-1):
        self.getProtocol("vtkWebPublishImageDelivery").imagePush({"view": view})

    def get_data_base(self):
        return self.getSharedObject("db")

    def get_renderer(self):
        return self.getSharedObject("renderer")

    def get_object(self, id):
        return self.get_data_base()[id]

    def get_protocol(self, name):
        for p in self.coreServer.getLinkProtocols():
            if type(p).__name__ == name:
                return p

    def render(self, view=-1):
        self.getProtocol("vtkWebPublishImageDelivery").imagePush({"view": view})

    def register_object(self, id, reader, filter, actor, mapper, textures):
        self.get_data_base()[id] = {
            "reader": reader,
            "filter": filter,
            "actor": actor,
            "mapper": mapper,
            "textures": textures,
        }
