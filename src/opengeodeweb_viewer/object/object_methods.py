# Standard library imports
import os

# Third party imports
import vtk

# Local application imports
from opengeodeweb_viewer.vtk_protocol import VtkView


class VtkObjectView(VtkView):
    def __init__(self) -> None:
        super().__init__()

    def registerObject(
        self,
        id: str,
        file_name: str,
        reader: vtk.vtkDataReader,
        filter: vtk.vtkAlgorithm | None,
        mapper: vtk.vtkMapper,
    ) -> None:
        actor = vtk.vtkActor()
        self.register_object(id, reader, filter, actor, mapper, {})
        reader.SetFileName(os.path.join(self.DATA_FOLDER_PATH, id, file_name))
        actor.SetMapper(mapper)
        mapper.SetColorModeToMapScalars()
        mapper.SetResolveCoincidentTopologyLineOffsetParameters(1, -0.1)
        mapper.SetResolveCoincidentTopologyPolygonOffsetParameters(2, 0)
        mapper.SetResolveCoincidentTopologyPointOffsetParameter(-2)

        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        renderer.AddActor(actor)
        renderer.ResetCamera()
        renderWindow.Render()
        self.render()

    def deregisterObject(self, data_id: str) -> None:
        actor = self.get_object(data_id)["actor"]
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        renderer.RemoveActor(actor)
        self.deregister_object(data_id)
        self.render()

    def applyTextures(self, data_id: str, textures: list[dict[str, str]]) -> None:
        textures_array: list[vtk.vtkTexture] = []
        images_reader_array: list[vtk.vtkXMLImageDataReader] = []

        data = self.get_object(data_id)
        mapper = data["mapper"]
        actor = data["actor"]
        reader = data["reader"]

        polydata_mapper = mapper.GetPolyDataMapper()
        poly_data = reader.GetPolyDataOutput()

        for index, value in enumerate(textures):
            texture_name = value["texture_name"]
            id_texture = value["id"]
            print(f"{texture_name=} {id_texture=}", flush=True)

            new_texture = vtk.vtkTexture()
            image_reader = vtk.vtkXMLImageDataReader()
            texture_path = self.get_data_file_path(data_id, id_texture)
            image_reader.SetFileName(texture_path)

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

    def SetVisibility(self, data_id: str, visibility: bool) -> None:
        actor = self.get_object(data_id)["actor"]
        actor.SetVisibility(visibility)
        self.render()

    def SetOpacity(self, data_id: str, opacity: float) -> None:
        actor = self.get_object(data_id)["actor"]
        actor.GetProperty().SetOpacity(opacity)
        self.render()

    def SetColor(self, data_id: str, red: int, green: int, blue: int) -> None:
        mapper = self.get_object(data_id)["mapper"]
        mapper.ScalarVisibilityOff()
        actor = self.get_object(data_id)["actor"]
        actor.GetProperty().SetColor([red / 255, green / 255, blue / 255])
        self.render()

    def SetEdgesVisibility(self, data_id: str, visibility: bool) -> None:
        actor = self.get_object(data_id)["actor"]
        max_dimension = self.get_object(data_id)["max_dimension"]
        if max_dimension == "edges":
            self.SetVisibility(data_id, visibility)
        else:
            actor.GetProperty().SetEdgeVisibility(visibility)
        self.render()

    def SetEdgesWidth(self, data_id: str, width: float) -> None:
        actor = self.get_object(data_id)["actor"]
        actor.GetProperty().SetEdgeWidth(width)
        self.render()

    def SetEdgesColor(self, data_id: str, red: int, green: int, blue: int) -> None:
        actor = self.get_object(data_id)["actor"]
        max_dimension = self.get_object(data_id)["max_dimension"]
        if max_dimension == "edges":
            self.SetColor(data_id, red, green, blue)
        else:
            actor.GetProperty().SetEdgeColor([red / 255, green / 255, blue / 255])
        self.render()

    def SetPointsVisibility(self, data_id: str, visibility: bool) -> None:
        actor = self.get_object(data_id)["actor"]
        max_dimension = self.get_object(data_id)["max_dimension"]
        if max_dimension == "points":
            self.SetVisibility(data_id, visibility)
        else:
            actor.GetProperty().SetVertexVisibility(visibility)
        self.render()

    def SetPointsSize(self, data_id: str, size: float) -> None:
        actor = self.get_object(data_id)["actor"]
        actor.GetProperty().SetPointSize(size)
        self.render()

    def SetPointsColor(self, data_id: str, red: int, green: int, blue: int) -> None:
        actor = self.get_object(data_id)["actor"]
        max_dimension = self.get_object(data_id)["max_dimension"]
        if max_dimension == "points":
            self.SetColor(data_id, red, green, blue)
        else:
            actor.GetProperty().SetVertexColor([red / 255, green / 255, blue / 255])
        self.render()

    def SetBlocksVisibility(
        self, data_id: str, block_ids: list[int], visibility: bool
    ) -> None:
        mapper = self.get_object(data_id)["mapper"]
        for block_id in block_ids:
            mapper.SetBlockVisibility(block_id, visibility)
        self.render()

    def SetBlocksColor(
        self, data_id: str, block_ids: list[int], red: int, green: int, blue: int
    ) -> None:
        mapper = self.get_object(data_id)["mapper"]
        for block_id in block_ids:
            mapper.SetBlockColor(block_id, [red / 255, green / 255, blue / 255])
        self.render()

    def clearColors(self, data_id: str) -> None:
        db = self.get_object(data_id)
        mapper = db["mapper"]
        reader = db["reader"]
        reader.GetOutput().GetPointData().SetActiveScalars("")
        reader.GetOutput().GetCellData().SetActiveScalars("")
        mapper.ScalarVisibilityOff()
