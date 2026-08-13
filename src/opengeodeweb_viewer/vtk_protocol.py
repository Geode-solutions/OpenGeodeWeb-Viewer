# Standard library imports
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
import math
import os
from typing import Any, cast

# Third party imports
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.web import protocols as vtk_protocols
from vtkmodules.vtkWebCore import vtkWebApplication
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCellPicker,
    vtkCompositePolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
)
from vtkmodules.vtkCommonDataModel import (
    vtkBoundingBox,
    vtkDataObject,
    vtkDataSet,
    vtkImplicitBoolean,
    vtkPlane,
    vtkSelectionNode,
)
from vtkmodules.vtkFiltersExtraction import vtkExtractGeometry
from vtkmodules.vtkFiltersGeneral import vtkShrinkFilter
from vtkmodules.vtkFiltersGeometry import vtkGeometryFilter
from vtkmodules.vtkCommonCore import vtkIdTypeArray, vtkStringArray
from vtkmodules.vtkRenderingAnnotation import (
    vtkAxesActor,
    vtkCubeAxesActor,
)
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget

# Local application imports
from opengeodeweb_microservice.database.connection import get_session
from opengeodeweb_microservice.database.data import Data
from opengeodeweb_viewer.rpc.viewer.schemas.clipping_planes import Plane
from opengeodeweb_viewer.vtk_pipeline import (
    RulerPipeline,
    ViewerData,
    VtkPipeline,
)


class VtkTypingMixin:
    def getView(self, view_id: str) -> vtkRenderWindow:
        return cast(vtkRenderWindow, super().getView(view_id))  # type: ignore

    def registerVtkWebProtocol(self, protocol: Any) -> None:
        super().registerVtkWebProtocol(protocol)  # type: ignore

    def getApplication(self) -> vtkWebApplication:
        return cast(vtkWebApplication, super().getApplication())  # type: ignore


class VtkView(VtkTypingMixin, vtk_protocols.vtkWebProtocol):
    def __init__(self) -> None:
        super().__init__()
        self.DATA_FOLDER_PATH = os.getenv("DATA_FOLDER_PATH", ".")

    def get_data_base(self) -> Any:
        return self.getSharedObject("db")

    def get_vtk_pipeline(self, id: str) -> VtkPipeline:
        return cast(VtkPipeline, self.get_data_base()[id])

    def get_grid_scale(self) -> vtkCubeAxesActor | None:
        return cast(vtkCubeAxesActor | None, self.getSharedObject("grid_scale"))

    def set_grid_scale(self, grid_scale: vtkCubeAxesActor) -> None:
        self.coreServer.setSharedObject("grid_scale", grid_scale)

    def get_axes(self) -> vtkAxesActor | None:
        return cast(vtkAxesActor | None, self.getSharedObject("axes"))

    def set_axes(self, axes: vtkAxesActor) -> None:
        self.coreServer.setSharedObject("axes", axes)

    def get_widget(self) -> vtkOrientationMarkerWidget | None:
        return cast(vtkOrientationMarkerWidget | None, self.getSharedObject("widget"))

    def set_widget(self, widget: vtkOrientationMarkerWidget) -> None:
        self.coreServer.setSharedObject("widget", widget)

    def get_ruler(self) -> RulerPipeline | None:
        return cast(RulerPipeline | None, self.getSharedObject("ruler"))

    def set_ruler(self, ruler: RulerPipeline) -> None:
        self.coreServer.setSharedObject("ruler", ruler)

    def get_viewer_data(self, data_id: str) -> ViewerData:
        if Data is None:
            raise Exception("Data model not available")

        with get_session() as session:
            if not session:
                raise Exception("No database session available")

            try:
                data = session.get(Data, data_id)
                if not data:
                    raise Exception(f"Data with id {data_id} not found in database")
                return ViewerData(
                    id=data.id,
                    viewable_file=data.viewable_file,
                    viewer_object=data.viewer_object,
                    viewer_elements_type=data.viewer_elements_type,
                )
            except Exception as e:
                print(f"Error fetching data {data_id}: {e}")
                raise

    def get_data_file_path(self, data_id: str, filename: str | None = None) -> str:
        if filename is None:
            data = self.get_viewer_data(data_id)
            viewable_file = data.viewable_file
            filename = str(viewable_file) if viewable_file is not None else ""

        data_folder_path = self.DATA_FOLDER_PATH
        if data_folder_path is None:
            raise Exception("DATA_FOLDER_PATH environment variable not set")

        return os.path.join(data_folder_path, data_id, filename)

    def get_renderer(self) -> vtkRenderer:
        return cast(vtkRenderer, self.getSharedObject("renderer"))

    def reset_camera_clipping_range(self) -> None:
        renderer = self.get_renderer()
        grid_scale = self.get_grid_scale()
        if grid_scale is not None and grid_scale.GetVisibility():
            grid_scale.SetUseBounds(True)
            renderer.ResetCameraClippingRange()
        else:
            renderer.ResetCameraClippingRange()

    def setup_pipeline(self, pipeline: VtkPipeline, name: str) -> vtkDataObject | None:
        pipeline.filter.SetInputConnection(pipeline.reader.GetOutputPort())
        pipeline.filter.Update()
        geometry_output: vtkDataObject | None = pipeline.filter.GetOutputDataObject(0)
        if geometry_output:
            geometry_output.SetObjectName(name)
        if isinstance(pipeline.mapper, vtkCompositePolyDataMapper):
            pipeline.mapper.SetInputDataObject(geometry_output)
        else:
            pipeline.mapper.SetInputConnection(pipeline.filter.GetOutputPort())
        return geometry_output

    def update_highlight(
        self,
        pipeline: VtkPipeline,
        id_to_select: int,
        field_type: str,
        dataset: vtkDataObject | None = None,
    ) -> None:
        node = pipeline.highlight.selectionNode
        node.SetContentType(vtkSelectionNode.INDICES)
        node.SetFieldType(
            vtkSelectionNode.CELL if field_type == "CELL" else vtkSelectionNode.POINT
        )
        selection_list = vtkIdTypeArray()
        selection_list.SetNumberOfComponents(1)
        selection_list.InsertNextValue(id_to_select)
        node.SetSelectionList(selection_list)
        target_dataset = dataset or pipeline.mapper.GetInputDataObject(0, 0)
        pipeline.highlight.extractSelection.SetInputData(0, target_dataset)
        pipeline.highlight.extractSelection.Modified()
        pipeline.highlight.extractSelection.Update()
        pipeline.highlight.actor.VisibilityOn()

    def clear_highlights(self, data_ids: list[str]) -> None:
        for data_id in data_ids:
            pipeline = self.get_vtk_pipeline(data_id)
            pipeline.highlight.actor.VisibilityOff()

    def update_pipeline_filter(self, pipeline: VtkPipeline) -> None:
        current_input_port = pipeline.reader.GetOutputPort()
        active_filters = [
            filter_obj
            for filter_obj in (pipeline.clipping_filter, pipeline.shrink_filter)
            if filter_obj is not None
        ]
        for filter_obj in active_filters:
            filter_obj.SetInputConnection(current_input_port)
            current_input_port = filter_obj.GetOutputPort()
        pipeline.filter.SetInputConnection(current_input_port)
        pipeline.filter.Update()
        filtered_dataset = pipeline.filter.GetOutputDataObject(0)
        if isinstance(pipeline.mapper, vtkCompositePolyDataMapper):
            pipeline.sync_composite_pipeline(filtered_dataset)
            return
        pipeline.mapper.SetInputConnection(pipeline.filter.GetOutputPort())
        target_dataset = (
            cast(vtkDataSet, filtered_dataset)
            if active_filters
            else pipeline.reader.GetOutputAsDataSet()
        )
        pipeline.restore_active_scalars(target_dataset)

    def set_clipping_planes(
        self, data_ids: list[str], planes_data: list[Plane]
    ) -> None:
        for data_id in data_ids:
            pipeline = self.get_vtk_pipeline(data_id)
            if planes_data:
                clipping_filter = vtkExtractGeometry()
                implicit_boolean = vtkImplicitBoolean()
                implicit_boolean.SetOperationTypeToIntersection()
                for plane_info in planes_data:
                    plane = vtkPlane()
                    plane.SetOrigin(plane_info.origin)
                    plane.SetNormal(plane_info.normal)
                    implicit_boolean.AddFunction(plane)
                clipping_filter.SetImplicitFunction(implicit_boolean)
                pipeline.clipping_filter = clipping_filter
            else:
                pipeline.clipping_filter = None
            self.update_pipeline_filter(pipeline)

    def set_shrink(self, data_ids: list[str], shrink_factor: float) -> None:
        for data_id in data_ids:
            pipeline = self.get_vtk_pipeline(data_id)
            if shrink_factor < 1.0:
                shrink_filter = vtkShrinkFilter()
                shrink_filter.SetShrinkFactor(shrink_factor)
                pipeline.shrink_filter = shrink_filter
            else:
                pipeline.shrink_filter = None
            self.update_pipeline_filter(pipeline)

    def swap_pick_mappers(self, data_ids: list[str], use_pick_mapper: bool) -> None:
        # Swap actor mappers between the default and the pick_mapper (where hidden blocks are pruned).
        for data_id in data_ids:
            pipeline = self.get_vtk_pipeline(data_id)
            if pipeline.pick_mapper:
                mapper = pipeline.pick_mapper if use_pick_mapper else pipeline.mapper
                pipeline.actor.SetMapper(mapper)

    def pick_cell_or_point(
        self,
        data_ids: list[str],
        x: float,
        y: float,
        field_type: str,
        picker: vtkCellPicker,
    ) -> tuple[str | None, int]:
        self.swap_pick_mappers(data_ids, use_pick_mapper=True)
        try:
            picker.Pick(x, y, 0, self.get_renderer())
        finally:
            self.swap_pick_mappers(data_ids, use_pick_mapper=False)
        actor = picker.GetActor()
        # Find which pipeline owns the picked actor
        data_id = next(
            (
                current_data_id
                for current_data_id in data_ids
                if self.get_vtk_pipeline(current_data_id).actor == actor
            ),
            None,
        )
        id_to_select = (
            picker.GetCellId() if field_type == "CELL" else picker.GetPointId()
        )
        return data_id, id_to_select

    def pick_actors_under_coordinate(
        self, data_ids: list[str], x: float, y: float, picker: vtkCellPicker
    ) -> tuple[list[vtkActor], int]:
        renderer = self.get_renderer()
        self.swap_pick_mappers(data_ids, use_pick_mapper=True)
        actors = []
        viewer_id = -1
        try:
            picker.Pick(x, y, 0, renderer)
            viewer_id = picker.GetFlatBlockIndex()
            while actor := picker.GetActor():
                actors.append(actor)
                actor.SetPickable(False)
                picker.Pick(x, y, 0, renderer)
        finally:
            for actor in actors:
                actor.SetPickable(True)
            self.swap_pick_mappers(data_ids, use_pick_mapper=False)
        return actors, viewer_id

    def get_composite_block_info(
        self, pipeline: VtkPipeline, picker: vtkCellPicker
    ) -> tuple[vtkDataObject | None, str | None]:
        # Extract the specific block dataset and metadata from a picked composite flat index
        if not isinstance(pipeline.mapper, vtkCompositePolyDataMapper):
            return None, None
        flat_index = picker.GetFlatBlockIndex()
        if not (0 <= flat_index < len(pipeline.blockDataSets)):
            return None, None
        dataset = pipeline.blockDataSets[flat_index]
        geode_id = (
            pipeline.blockGeodeIds[flat_index]
            if flat_index < len(pipeline.blockGeodeIds)
            else None
        )
        return dataset, geode_id

    def get_array_values(self, array: Any, id_to_select: int) -> list[float] | float:
        components = array.GetNumberOfComponents()
        if components == 1:
            return float(array.GetComponent(id_to_select, 0))
        return [float(array.GetComponent(id_to_select, i)) for i in range(components)]

    def extract_picked_attributes(
        self,
        pipeline: VtkPipeline,
        id_to_select: int,
        field_type: str,
        dataset: vtkDataObject | None,
    ) -> dict[str, list[float] | float]:
        data_object = dataset or pipeline.mapper.GetInputDataObject(0, 0)
        if not isinstance(data_object, vtkDataSet):
            return {}
        field_data = (
            data_object.GetCellData()
            if field_type == "CELL"
            else data_object.GetPointData()
        )
        attributes = {}
        for i in range(field_data.GetNumberOfArrays()):
            array = field_data.GetArray(i)
            if array and array.GetName():
                attributes[array.GetName()] = self.get_array_values(array, id_to_select)
        if field_type == "POINT" and (coords := data_object.GetPoint(id_to_select)):
            attributes["coordinates"] = list(coords)
        return attributes

    def update_grid_scale_and_clipping_range(self) -> None:
        grid_scale = self.get_grid_scale()
        if grid_scale is not None:
            renderer = self.get_renderer()
            if not grid_scale.GetVisibility():
                bounds = vtkBoundingBox()
                props = renderer.GetViewProps()
                props.InitTraversal()
                prop = props.GetNextProp()
                while prop:
                    if (
                        prop.GetVisibility()
                        and prop.GetUseBounds()
                        and prop != grid_scale
                    ):
                        prop_bounds = prop.GetBounds()
                        if prop_bounds is not None:
                            bounds.AddBounds(prop_bounds)
                    prop = props.GetNextProp()
                if bounds.IsValid():
                    final_bounds = [0.0] * 6
                    bounds.GetBounds(final_bounds)
                    grid_scale.SetBounds(final_bounds)

            final_bounds = list(grid_scale.GetBounds())
            if final_bounds[0] <= final_bounds[1]:

                def get_dist(axis: int) -> float:
                    p1 = [final_bounds[0], final_bounds[2], final_bounds[4]]
                    p2 = list(p1)
                    p2[axis] = final_bounds[axis * 2 + 1]
                    renderer.SetWorldPoint(p1[0], p1[1], p1[2], 1.0)
                    renderer.WorldToDisplay()
                    d1 = list(renderer.GetDisplayPoint())
                    renderer.SetWorldPoint(p2[0], p2[1], p2[2], 1.0)
                    renderer.WorldToDisplay()
                    d2 = list(renderer.GetDisplayPoint())
                    return math.sqrt((d1[0] - d2[0]) ** 2 + (d1[1] - d2[1]) ** 2)

                visibility_setters = [
                    grid_scale.SetXAxisLabelVisibility,
                    grid_scale.SetYAxisLabelVisibility,
                    grid_scale.SetZAxisLabelVisibility,
                ]

                for axis in range(3):
                    dist = get_dist(axis)
                    visibility_setter = visibility_setters[axis]

                    v1 = f"{final_bounds[axis * 2]:g}"
                    v2 = f"{final_bounds[axis * 2 + 1]:g}"
                    v_mid = (
                        f"{(final_bounds[axis * 2] + final_bounds[axis * 2 + 1]) / 2:g}"
                    )

                    char_width = 8
                    len1 = len(v1) * char_width
                    len2 = len(v2) * char_width
                    len_mid = len(v_mid) * char_width

                    hide_threshold = max(len1, len2) + 15
                    two_labels_threshold = (len1 + len2) * 1.1 + 30
                    three_labels_threshold = (len1 + len2 + len_mid) * 1.2 + 45

                    if dist < hide_threshold:
                        visibility_setter(False)
                    elif dist < two_labels_threshold:
                        visibility_setter(True)
                        labels = vtkStringArray()
                        labels.InsertNextValue(v1)
                        labels.InsertNextValue(v2)
                        grid_scale.SetAxisLabels(axis, labels)
                    elif dist < three_labels_threshold:
                        visibility_setter(True)
                        labels = vtkStringArray()
                        labels.InsertNextValue(v1)
                        labels.InsertNextValue(v_mid)
                        labels.InsertNextValue(v2)
                        grid_scale.SetAxisLabels(axis, labels)
                    else:
                        visibility_setter(True)
                        grid_scale.SetAxisLabels(axis, None)
        self.reset_camera_clipping_range()

    def update_scalar_bars_layout(self) -> None:
        visible_bars: list[tuple[vtkScalarBarActor, str, str, VtkPipeline]] = []
        for data_id, pipeline in self.get_data_base().items():
            if (
                pipeline.scalarBar.GetVisibility()
                and pipeline.scalarBar.GetLookupTable() is not None
            ):
                dataset = pipeline.filter.GetOutputDataObject(0)
                scalars = (
                    dataset.GetPointData().GetScalars()
                    or dataset.GetCellData().GetScalars()
                    if isinstance(dataset, vtkDataSet)
                    else None
                )
                attr_name = scalars.GetName() if scalars else "Attribute"
                visible_bars.append((pipeline.scalarBar, attr_name, data_id, pipeline))

            for attr_name, bar in pipeline.scalar_bars.items():
                if bar.GetVisibility() and bar.GetLookupTable() is not None:
                    visible_bars.append((bar, attr_name, data_id, pipeline))

        if not visible_bars:
            return

        start_x = 0.22
        start_y = 0.04
        margin_x = 0.03
        margin_y = 0.04

        cols = 5
        actual_width = 0.10
        row_height = 0.12

        for i, (bar, attr_name, data_id, pipeline) in enumerate(visible_bars):
            dataset = pipeline.filter.GetOutputDataObject(0)
            data_name = (
                dataset.GetObjectName()
                if dataset and dataset.GetObjectName()
                else data_id
            )

            bar.UnconstrainedFontSizeOn()
            bar.GetLabelTextProperty().SetFontSize(14)
            bar.GetTitleTextProperty().SetFontSize(14)
            bar.GetLabelTextProperty().SetColor(0, 0, 0)
            bar.GetTitleTextProperty().SetColor(0, 0, 0)
            bar.GetLabelTextProperty().SetShadow(False)
            bar.GetTitleTextProperty().SetShadow(False)

            if data_name:
                if len(data_name) > 22:
                    data_name = data_name[:19] + "..."
                bar.SetTitle(f"{attr_name}\n({data_name})\n")
                bar.GetTitleTextProperty().SetVerticalJustificationToTop()
                bar.GetTitleTextProperty().SetLineOffset(0.0)
                bar.SetBarRatio(0.15)
                bar_height = 0.12
            else:
                bar.SetTitle(f"{attr_name}\n")
                bar.GetTitleTextProperty().SetVerticalJustificationToTop()
                bar.GetTitleTextProperty().SetLineOffset(0.0)
                bar.SetBarRatio(0.4)
                bar_height = 0.08

            bar.SetNumberOfLabels(2)
            bar.SetLabelFormat("%g")
            bar.SetOrientationToHorizontal()

            row = i // cols
            col = i % cols

            x = start_x + col * (actual_width + margin_x)
            y = start_y + row * (row_height + margin_y)

            bar.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
            bar.GetPositionCoordinate().SetValue(x, y)
            bar.SetWidth(actual_width)
            bar.SetHeight(bar_height)

    def render(self, view: int = -1) -> None:
        self.update_grid_scale_and_clipping_range()
        self.getSharedObject("publisher").imagePush({"view": view})

    def register_object(self, id: str, data: VtkPipeline) -> None:
        self.get_data_base()[id] = data

    def deregister_object(self, id: str) -> None:
        if id in self.get_data_base():
            del self.get_data_base()[id]
