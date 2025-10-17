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
        resetCamara = True
        for registered_actor in renderer.GetActors():
            if registered_actor.visibility == True:
                resetCamara = False
        renderer.AddActor(actor)
        if resetCamara:
            renderer.ResetCamera()

    def deregisterObject(self, data_id: str) -> None:
        actor = self.get_object(data_id)["actor"]
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        renderer.RemoveActor(actor)
        self.deregister_object(data_id)

    def SetVisibility(self, data_id: str, visibility: bool) -> None:
        actor = self.get_object(data_id)["actor"]
        actor.SetVisibility(visibility)

    def SetOpacity(self, data_id: str, opacity: float) -> None:
        actor = self.get_object(data_id)["actor"]
        actor.GetProperty().SetOpacity(opacity)

    def SetColor(self, data_id: str, red: int, green: int, blue: int) -> None:
        mapper = self.get_object(data_id)["mapper"]
        mapper.ScalarVisibilityOff()
        actor = self.get_object(data_id)["actor"]
        actor.GetProperty().SetColor([red / 255, green / 255, blue / 255])

    def SetEdgesVisibility(self, data_id: str, visibility: bool) -> None:
        actor = self.get_object(data_id)["actor"]
        max_dimension = self.get_object(data_id)["max_dimension"]
        if max_dimension == "edges":
            self.SetVisibility(data_id, visibility)
        else:
            actor.GetProperty().SetEdgeVisibility(visibility)

    def SetEdgesWidth(self, data_id: str, width: float) -> None:
        actor = self.get_object(data_id)["actor"]
        actor.GetProperty().SetEdgeWidth(width)

    def SetEdgesColor(self, data_id: str, red: int, green: int, blue: int) -> None:
        actor = self.get_object(data_id)["actor"]
        max_dimension = self.get_object(data_id)["max_dimension"]
        if max_dimension == "edges":
            self.SetColor(data_id, red, green, blue)
        else:
            actor.GetProperty().SetEdgeColor([red / 255, green / 255, blue / 255])

    def SetPointsVisibility(self, data_id: str, visibility: bool) -> None:
        actor = self.get_object(data_id)["actor"]
        max_dimension = self.get_object(data_id)["max_dimension"]
        if max_dimension == "points":
            self.SetVisibility(data_id, visibility)
        else:
            actor.GetProperty().SetVertexVisibility(visibility)

    def SetPointsSize(self, data_id: str, size: float) -> None:
        actor = self.get_object(data_id)["actor"]
        actor.GetProperty().SetPointSize(size)

    def SetPointsColor(self, data_id: str, red: int, green: int, blue: int) -> None:
        actor = self.get_object(data_id)["actor"]
        max_dimension = self.get_object(data_id)["max_dimension"]
        if max_dimension == "points":
            self.SetColor(data_id, red, green, blue)
        else:
            actor.GetProperty().SetVertexColor([red / 255, green / 255, blue / 255])

    def SetBlocksVisibility(
        self, data_id: str, block_ids: list[int], visibility: bool
    ) -> None:
        mapper = self.get_object(data_id)["mapper"]
        for block_id in block_ids:
            mapper.SetBlockVisibility(block_id, visibility)

    def SetBlocksColor(
        self, data_id: str, block_ids: list[int], red: int, green: int, blue: int
    ) -> None:
        mapper = self.get_object(data_id)["mapper"]
        for block_id in block_ids:
            mapper.SetBlockColor(block_id, [red / 255, green / 255, blue / 255])

    def clearColors(self, data_id: str) -> None:
        db = self.get_object(data_id)
        mapper = db["mapper"]
        reader = db["reader"]
        reader.GetOutput().GetPointData().SetActiveScalars("")
        reader.GetOutput().GetCellData().SetActiveScalars("")
        mapper.ScalarVisibilityOff()
