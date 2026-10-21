# Local application imports
from opengeodeweb_viewer.vtk_protocol import VtkView

from .mesh.cells.attribute.cell.cells_attribute_cell_protocols import VtkMeshCellsAttributeCellView
from .mesh.cells.attribute.vertex.cells_attribute_vertex_protocols import (
    VtkMeshCellsAttributeVertexView,
)
from .mesh.cells.cells_protocols import VtkMeshCellsView
from .mesh.edges.attribute.edge.edges_attribute_edge_protocols import VtkMeshEdgesAttributeEdgeView
from .mesh.edges.attribute.vertex.edges_attribute_vertex_protocols import (
    VtkMeshEdgesAttributeVertexView,
)
from .mesh.edges.edges_protocols import VtkMeshEdgesView
from .mesh.points.attribute.vertex.points_attribute_vertex_protocols import (
    VtkMeshPointsAttributeVertexView,
)
from .mesh.points.points_protocols import VtkMeshPointsView
from .mesh.polygons.attribute.polygon.polygons_attribute_polygon_protocols import (
    VtkMeshPolygonsAttributePolygonView,
)
from .mesh.polygons.attribute.vertex.polygons_attribute_vertex_protocols import (
    VtkMeshPolygonsAttributeVertexView,
)
from .mesh.polygons.polygons_protocols import VtkMeshPolygonsView
from .mesh.polyhedra.attribute.polyhedron.polyhedra_attribute_polyhedron_protocols import (
    VtkMeshPolyhedraAttributePolyhedronView,
)
from .mesh.polyhedra.attribute.vertex.polyhedra_attribute_vertex_protocols import (
    VtkMeshPolyhedraAttributeVertexView,
)
from .mesh.polyhedra.polyhedra_protocols import VtkMeshPolyhedraView
from .model.blocks.attribute.polyhedron.blocks_attribute_polyhedron_protocols import (
    VtkModelBlocksAttributePolyhedronView,
)
from .model.blocks.attribute.vertex.blocks_attribute_vertex_protocols import (
    VtkModelBlocksAttributeVertexView,
)
from .model.blocks.edges.attribute.vertex.blocks_edges_attribute_vertex_protocols import (
    VtkModelBlocksEdgesAttributeVertexView,
)
from .model.blocks.edges.model_blocks_edges_protocols import VtkModelBlocksEdgesView
from .model.blocks.model_blocks_protocols import VtkModelBlocksView
from .model.blocks.points.attribute.vertex.blocks_points_attribute_vertex_protocols import (
    VtkModelBlocksPointsAttributeVertexView,
)
from .model.blocks.points.model_blocks_points_protocols import VtkModelBlocksPointsView
from .model.corners.attribute.vertex.corners_attribute_vertex_protocols import (
    VtkModelCornersAttributeVertexView,
)
from .model.corners.model_corners_protocols import VtkModelCornersView
from .model.edges.model_edges_protocols import VtkModelEdgesView
from .model.lines.attribute.edge.lines_attribute_edge_protocols import (
    VtkModelLinesAttributeEdgeView,
)
from .model.lines.attribute.vertex.lines_attribute_vertex_protocols import (
    VtkModelLinesAttributeVertexView,
)
from .model.lines.model_lines_protocols import VtkModelLinesView
from .model.lines.points.attribute.vertex.lines_points_attribute_vertex_protocols import (
    VtkModelLinesPointsAttributeVertexView,
)
from .model.lines.points.model_lines_points_protocols import VtkModelLinesPointsView
from .model.points.model_points_protocols import VtkModelPointsView
from .model.surfaces.attribute.polygon.surfaces_attribute_polygon_protocols import (
    VtkModelSurfacesAttributePolygonView,
)
from .model.surfaces.attribute.vertex.surfaces_attribute_vertex_protocols import (
    VtkModelSurfacesAttributeVertexView,
)
from .model.surfaces.edges.attribute.vertex.surfaces_edges_attribute_vertex_protocols import (
    VtkModelSurfacesEdgesAttributeVertexView,
)
from .model.surfaces.edges.model_surfaces_edges_protocols import VtkModelSurfacesEdgesView
from .model.surfaces.model_surfaces_protocols import VtkModelSurfacesView
from .model.surfaces.points.attribute.vertex.surfaces_points_attribute_vertex_protocols import (
    VtkModelSurfacesPointsAttributeVertexView,
)
from .model.surfaces.points.model_surfaces_points_protocols import VtkModelSurfacesPointsView

MESH_PROTOCOLS: tuple[type[VtkView], ...] = (
    VtkMeshPointsView,
    VtkMeshPointsAttributeVertexView,
    VtkMeshEdgesView,
    VtkMeshEdgesAttributeVertexView,
    VtkMeshEdgesAttributeEdgeView,
    VtkMeshCellsView,
    VtkMeshCellsAttributeVertexView,
    VtkMeshCellsAttributeCellView,
    VtkMeshPolygonsView,
    VtkMeshPolygonsAttributeVertexView,
    VtkMeshPolygonsAttributePolygonView,
    VtkMeshPolyhedraView,
    VtkMeshPolyhedraAttributeVertexView,
    VtkMeshPolyhedraAttributePolyhedronView,
)

MODEL_PROTOCOLS: tuple[type[VtkView], ...] = (
    VtkModelEdgesView,
    VtkModelPointsView,
    VtkModelCornersView,
    VtkModelLinesView,
    VtkModelSurfacesView,
    VtkModelBlocksView,
    VtkModelCornersAttributeVertexView,
    VtkModelLinesAttributeVertexView,
    VtkModelLinesAttributeEdgeView,
    VtkModelSurfacesAttributeVertexView,
    VtkModelSurfacesAttributePolygonView,
    VtkModelBlocksAttributeVertexView,
    VtkModelBlocksAttributePolyhedronView,
    VtkModelLinesPointsView,
    VtkModelSurfacesPointsView,
    VtkModelBlocksPointsView,
    VtkModelLinesPointsAttributeVertexView,
    VtkModelSurfacesPointsAttributeVertexView,
    VtkModelBlocksPointsAttributeVertexView,
    VtkModelSurfacesEdgesView,
    VtkModelBlocksEdgesView,
    VtkModelSurfacesEdgesAttributeVertexView,
    VtkModelBlocksEdgesAttributeVertexView,
)
