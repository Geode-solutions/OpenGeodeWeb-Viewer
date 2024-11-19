# Standard library imports


# Third party imports

# Local application imports
from opengeodeweb_viewer.utils_functions import get_schemas_dict, validate_schema
from opengeodeweb_viewer.vtk_protocol import VtkView

schemas_dir = os.path.join(os.path.dirname(__file__), "schemas")
schemas_dict = get_schemas_dict(schemas_dir)


class VtkObjectView(VtkView):
    def __init__(self):
        super().__init__()

    def SetVisibility(self, params):
        validate_schema(params, schemas_dict["set_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        actor = self.get_object(id)["actor"]
        actor.SetVisibility(visibility)
        self.render()

    def SetOpacity(self, params):
        print(f"{params=}", flush=True)
        validate_schema(params, schemas_dict["set_opacity"])
        id = params["id"]
        opacity = float(params["opacity"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetOpacity(opacity)
        self.render()
    
    def SetColor(self, params):
        validate_schema(params, schemas_dict["set_color"])
        id = params["id"]
        color = params["color"]
        mapper = self.get_object(id)["mapper"]
        mapper.ScalarVisibilityOff()
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetColor(color)
        self.render()

    def SetEdgeVisibility(self, params):
        print(f"{params=}", flush=True)
        validate_schema(params, schemas_dict["set_edge_visibility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetEdgeVisibility(visibility)
        self.render()

    def SetVertexVisibility(self, params):
        print(f"{params=}", flush=True)
        validate_schema(params, schemas_dict["set_vertex_visility"])
        id = params["id"]
        visibility = bool(params["visibility"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetVertexVisibility(visibility)
        self.render()

    def SetPointSize(self, params):
        validate_schema(params, schemas_dict["set_point_size"])
        id = params["id"]
        size = float(params["size"])
        actor = self.get_object(id)["actor"]
        actor.GetProperty().SetPointSize(size)
        self.render()