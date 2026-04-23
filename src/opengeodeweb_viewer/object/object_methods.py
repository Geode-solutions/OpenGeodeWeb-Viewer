# Standard library imports
import os

# Third party imports
from vtkmodules.vtkIOXML import vtkXMLDataReader, vtkXMLImageDataReader
from vtkmodules.vtkCommonExecutionModel import vtkAlgorithm
from vtkmodules.vtkRenderingCore import (
    vtkMapper,
    vtkActor,
    vtkTexture,
    vtkCompositePolyDataMapper,
    vtkCompositeDataDisplayAttributes,
    vtkDataSetMapper,
)
from vtkmodules.vtkCommonDataModel import (
    vtkDataObject,
    vtkDataSet,
    vtkCompositeDataSet,
)

# Local application imports
from opengeodeweb_viewer.vtk_protocol import VtkView, VtkPipeline


class VtkObjectView(VtkView):
    def __init__(self) -> None:
        super().__init__()

    def registerObject(
        self,
        id: str,
        file_name: str,
        data: VtkPipeline,
    ) -> None:
        self.register_object(id, data)
        data.actor.SetMapper(data.mapper)
        data.mapper.SetColorModeToMapScalars()
        data.mapper.SetResolveCoincidentTopologyLineOffsetParameters(1, -0.1)
        data.mapper.SetResolveCoincidentTopologyPolygonOffsetParameters(2, 0)
        data.mapper.SetResolveCoincidentTopologyPointOffsetParameter(-2)

        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        resetCamara = True
        actors = renderer.GetActors()
        actors.InitTraversal()
        while actor := actors.GetNextItem():
            if actor.visibility == True:
                resetCamara = False
        renderer.AddActor(data.actor)
        if data.highlightActor:
            renderer.AddActor(data.highlightActor)
        if resetCamara:
            renderer.ResetCamera()

    def deregisterObject(self, data_id: str) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        renderWindow = self.getView("-1")
        renderer = renderWindow.GetRenderers().GetFirstRenderer()
        renderer.RemoveActor(pipeline.actor)
        if pipeline.highlightActor:
            renderer.RemoveActor(pipeline.highlightActor)
        self.deregister_object(data_id)

    def SetVisibility(self, data_id: str, visibility: bool) -> None:
        actor = self.get_vtk_pipeline(data_id).actor
        actor.SetVisibility(visibility)

    def SetOpacity(self, data_id: str, opacity: float) -> None:
        actor = self.get_vtk_pipeline(data_id).actor
        actor.GetProperty().SetOpacity(opacity)

    def SetColor(
        self, data_id: str, red: int, green: int, blue: int, alpha: float
    ) -> None:
        mapper = self.get_vtk_pipeline(data_id).mapper
        mapper.ScalarVisibilityOff()
        actor = self.get_vtk_pipeline(data_id).actor
        actor.GetProperty().SetColor([red / 255, green / 255, blue / 255])
        actor.GetProperty().SetOpacity(alpha)

    def SetEdgesVisibility(self, data_id: str, visibility: bool) -> None:
        if self.get_viewer_data(data_id).viewer_elements_type == "edges":
            self.SetVisibility(data_id, visibility)
        else:
            actor = self.get_vtk_pipeline(data_id).actor
            actor.GetProperty().SetEdgeVisibility(visibility)

    def SetEdgesWidth(self, data_id: str, width: float) -> None:
        actor = self.get_vtk_pipeline(data_id).actor
        if self.get_viewer_data(data_id).viewer_elements_type == "edges":
            actor.GetProperty().SetLineWidth(width)
        else:
            actor.GetProperty().SetEdgeWidth(width)

    def SetEdgesColor(
        self, data_id: str, red: int, green: int, blue: int, alpha: float
    ) -> None:
        if self.get_viewer_data(data_id).viewer_elements_type == "edges":
            self.SetColor(data_id, red, green, blue, alpha)
        else:
            actor = self.get_vtk_pipeline(data_id).actor
            actor.GetProperty().SetEdgeColor([red / 255, green / 255, blue / 255])

    def SetPointsVisibility(self, data_id: str, visibility: bool) -> None:
        if self.get_viewer_data(data_id).viewer_elements_type == "points":
            self.SetVisibility(data_id, visibility)
        else:
            actor = self.get_vtk_pipeline(data_id).actor
            actor.GetProperty().SetVertexVisibility(visibility)

    def SetPointsSize(self, data_id: str, size: float) -> None:
        actor = self.get_vtk_pipeline(data_id).actor
        actor.GetProperty().SetPointSize(size)

    def SetPointsColor(
        self, data_id: str, red: int, green: int, blue: int, alpha: float
    ) -> None:
        if self.get_viewer_data(data_id).viewer_elements_type == "points":
            self.SetColor(data_id, red, green, blue, alpha)
        else:
            actor = self.get_vtk_pipeline(data_id).actor
            actor.GetProperty().SetVertexColor([red / 255, green / 255, blue / 255])

    def SetBlocksVisibility(
        self, data_id: str, block_ids: list[int], visibility: bool
    ) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        mapper = pipeline.mapper
        if not isinstance(mapper, vtkCompositePolyDataMapper):
            raise Exception("Mapper is not a vtkCompositePolyDataMapper")
        blocks = pipeline.blockDataSets
        attributes = mapper.GetCompositeDataDisplayAttributes()
        for block_id in block_ids:
            attributes.SetBlockVisibility(blocks[block_id], visibility)

    def SetBlocksColor(
        self,
        data_id: str,
        block_ids: list[int],
        red: int,
        green: int,
        blue: int,
        alpha: float,
    ) -> None:
        pipeline = self.get_vtk_pipeline(data_id)
        mapper = pipeline.mapper
        if not isinstance(mapper, vtkCompositePolyDataMapper):
            raise Exception("Mapper is not a vtkCompositePolyDataMapper")
        blocks = pipeline.blockDataSets
        attributes = mapper.GetCompositeDataDisplayAttributes()
        for block_id in block_ids:
            attributes.SetBlockColor(
                blocks[block_id], [red / 255, green / 255, blue / 255]
            )
            attributes.SetBlockOpacity(blocks[block_id], alpha)

    def clearColors(self, data_id: str) -> None:
        db = self.get_vtk_pipeline(data_id)
        mapper = db.mapper
        reader = db.reader
        output = reader.GetOutputDataObject(0)
        if isinstance(output, vtkDataSet):
            output.GetPointData().SetActiveScalars("")
            output.GetCellData().SetActiveScalars("")
        mapper.ScalarVisibilityOff()

    def highlight(
        self, actor: vtkActor, mapper: vtkMapper, input_dataset: vtkDataObject
    ) -> None:
        mapper.SetInputDataObject(input_dataset)
        mapper.ScalarVisibilityOff()
        prop = actor.GetProperty()
        prop.SetColor(0.235, 0.6, 0.514)
        prop.SetLineWidth(5)
        prop.SetPointSize(14)
        prop.SetRenderPointsAsSpheres(True)
        prop.SetLighting(False)
        actor.SetMapper(mapper)
        actor.VisibilityOff()
