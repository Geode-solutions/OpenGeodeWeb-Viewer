# Local application imports
import VtkView from "./vtk_protocol.py"

schemas = os.path.join(os.path.dirname(__file__), "rpc/schemas")

with open(os.path.join(schemas, "display_vertex_attribute.json"), "r") as file:
    display_vertex_attribute_json = json.load(file)


@exportRpc(display_vertex_attribute_json["rpc"])
    def setVertexAttribute(self, params):
        validate_schemas(params, display_vertex_attribute_json)
        print(f"{params=}", flush=True)
        id = params["id"]
        name = params["name"]
        mapper = self.get_object(id)["mapper"]
        mapper.SelectColorArray(name)
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUsePointFieldData()
        self.render()

    @exportRpc("opengeode.attribute.polygon")
    def setPolygonAttribute(self, id, name):
        store = self.getObject(id)
        cpp = store["cpp"]
        print(cpp.nb_polygons())
        cells = store["vtk"].GetCellData()
        print(store["vtk"].GetNumberOfCells())
        manager = cpp.polygon_attribute_manager()
        if not manager.attribute_exists(name):
            return
        if not cells.HasArray(name):
            data = self.computeAttributeData(manager, name)
            cells.AddArray(data)
        cells.SetActiveScalars(name)
        mapper = store["mapper"]
        mapper.ScalarVisibilityOn()
        mapper.SetScalarModeToUseCellData()
        mapper.SetScalarRange(cells.GetScalars().GetRange())
        self.render()