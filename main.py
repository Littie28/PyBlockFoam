"""
The idea is to create a set of classes representing blocks, vertices and
related structures from the blockMesh utility. At first it should be possible
to create simple blocks with:
    - 8 vertices
    - 6 faces
    - 12 edges

The structuring of a block should be always the same. Maybe substructures
should be addressed by namings like:
    - xx, xy, ...
    - north, east, ...
    - usw

Example of a simple block

                           7 o--------------------o 6
                            /|                   /|
                           / |                  / |
                          /  |                 /  |
                         /   |                /   |
                      4 o--------------------o 5  |
                        |    |               |    |
                        |  3 o---------------|----o 2
                        |   /                |   /
                        |  /                 |  /
                        | /                  | /
                        |/                   |/
                      0 o--------------------o 1

The blockMeshDict is build up from different sections:
    1. Header
    2. Geometry
    3. Vertices
    4. Blocks
    5. Edges
    6. Faces
    7. Patches
    8. mergePatchPairs
    9. Footer

The most important part are the vertices. Vertices should map to each block
they belong and vice versa. Currently a defaultdict creating empty lists where
each block is appended is used. The vertices are returned if the block is in
the block list of the respective vertex. I currently don't know how good this
will scale but it is working right now.

Does it make sense to introduce a Mesh Class handling vertices, blocks and
the rendering of the actual blockMeshDict file
"""
from pprint import pprint
import collections
import itertools
import functools
import typing


def permutate_neasted_iterable(
    iterable: typing.Iterable[typing.Iterable],
) -> itertools.chain:
    """Takes a single neasted iterable and returns all permutations of its
    items.

    Example:

    [(0, 1), (5, 6), (8, 3)] -> [(0, 1), (1, 0), (5, 6), (6, 5), (8, 3), (3, 8)]

    """
    return itertools.chain.from_iterable(
        [itertools.permutations(item) for item in iterable]
    )


block_vertex: collections.namedtuple = collections.namedtuple(
    "block_local_vertex_id", "block local_vertex_id"
)

block_cells: collections.namedtuple = collections.namedtuple(
    "block_cells", "x1 x2 x3"
)

vertex_local_id: collections.namedtuple = collections.namedtuple(
    "vertex_local_id", "vertex local_id"
)

FLOAT_FORMAT_STRING: str = "{:12.6f}"
INT_FORMAT_STRING: str = "{:6d}"


class Vertex:
    """The Vertex Class defines locations in 3d cartesian space. Vertices are
    used to form blocks, faces and edges.
    """

    count: int = 0
    vertex_dict: collections.defaultdict = collections.defaultdict(
        list[block_vertex]
    )

    @staticmethod
    def print_dict() -> None:
        pprint(Vertex.vertex_dict)

    @staticmethod
    def get_vertices() -> dict.keys:
        return Vertex.vertex_dict.keys()

    def __init__(self, x: float, y: float, z: float) -> None:
        """Initializes a new Vertex instance. Instances get an 'hopefully'
        unique id used for identification.

        Args:
            x (float): x coordinate in cartesian space
            y (float): y coordinate in cartesian space
            z (float): z coordinate in cartesian space
        """
        self.id = type(self).count
        type(self).count += 1

        self.x: float = float(x)
        self.y: float = float(y)
        self.z: float = float(z)

    @property
    def id(self) -> int:
        """Unique id of the vertex instance"""
        return self._id

    @id.setter
    def id(self, value):
        if getattr(self, "id", None):
            raise ValueError("id already set")
        self._id = int(value)

    @property
    def global_id(self) -> int:
        """Returns the index of the vertex in the global vertex dict"""
        return dict(
            [(vertex, i) for i, vertex in enumerate(Vertex.get_vertices())]
        ).get(self)

    @property
    def is_inner_vertex(self) -> bool:
        """Returns true if a vertex is surrounded by other vertices (inner
        vertex) and false otherwise

            inner node:         outer nodes:

                x x                 x x             x
                |/                  |/              |
            x---o---x           x---o---x           o---x
               /|                                  /
              x x                                 x

        Returns:
            bool: is_inner_node flag
        """
        return len(self.connected_to) == 6

    @property
    def connected_to(self) -> set:
        """Returns a set of all vertices connected to this vertex"""
        return set(
            [
                block.vertices[vertex_id_in_block]
                for block, vert_id in Vertex.vertex_dict.get(self, [])
                for vertex_id_in_block in block.vertex_connection_map.get(
                    vert_id
                )
            ]
        )

    @property
    def blockMesh_format(self):
        pad, digits = 12, 6
        x = FLOAT_FORMAT_STRING.format(self.x)
        y = FLOAT_FORMAT_STRING.format(self.y)
        z = FLOAT_FORMAT_STRING.format(self.z)
        index = INT_FORMAT_STRING.format(self.global_id)
        return f"( {x} {y} {z} ) // {index}"

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"-{self.id}(x={self.x!r},y={self.y!r},z={self.z!r})"
        )

    def __str__(self) -> str:
        return str(tuple(self.x, self.y, self.z)) + f" if-{self.global_id}"

    def __hash__(self):
        return hash((type(self), self.id))


class Block:
    """A collection of 8 vertices

         7 o--------------------o 6
          /|                   /|
         / |                  / |
        /  |                 /  |
       /   |                /   |
    4 o--------------------o 5  |
      |    |               |    |
      |  3 o---------------|----o 2
      |   /                |   /
      |  /                 |  /
      | /                  | /
      |/                   |/
    0 o--------------------o 1

    """

    count: int = 0
    face_map = dict(  # dict defining all faces
        bottom=(0, 1, 2, 3),
        left=(4, 0, 3, 7),
        front=(4, 5, 1, 0),
        right=(1, 5, 6, 2),
        back=(3, 2, 6, 7),
        top=(4, 5, 6, 7),
    )

    edge_map = tuple(  # tuples defining all edges of the cube
        (
            (0, 1),  # 0
            (3, 2),  # 1
            (7, 6),  # 2
            (4, 5),  # 3
            (0, 3),  # 4
            (1, 2),  # 5
            (5, 6),  # 6
            (4, 7),  # 7
            (0, 4),  # 8
            (1, 5),  # 9
            (2, 6),  # 10
            (3, 7),  # 11
        )
    )

    def __init__(self, *vertices, name=None):
        if [vertices.count(vert) for vert in vertices].count(1) != 8:
            raise ValueError(
                "Need exactly 8 unique vertices to create a block, "
                + f"got {len(vertices)}:"
                + "\n\t"
                + f"{vertices}"
            )
        self.id = type(self).count
        type(self).count += 1
        self.name = name or f"Block-{self.id}"
        self.cells = block_cells(10, 10, 10)
        for i, vert in enumerate(vertices):
            Vertex.vertex_dict[vert].append(block_vertex(self, i))

    @classmethod
    def unit_cube(cls):
        vertices = (
            Vertex(-0.5, -0.5, -0.5),
            Vertex(0.5, -0.5, -0.5),
            Vertex(0.5, 0.5, -0.5),
            Vertex(-0.5, 0.5, -0.5),
            Vertex(-0.5, -0.5, 0.5),
            Vertex(0.5, -0.5, 0.5),
            Vertex(0.5, 0.5, 0.5),
            Vertex(-0.5, 0.5, 0.5),
        )
        return cls(*vertices)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if getattr(self, "id", None):
            raise ValueError("id already set")
        self._id = int(value)

    @property
    @functools.cache
    def vertex_connection_map(self):
        """Creates a mapping (dictionary) for each vertex and the vertices it
        is connected to.

        Returns:
            dict: connection map
        """
        mapping = collections.defaultdict(list)
        [
            mapping[edge_tuple[0]].append(edge_tuple[1])
            for edge_tuple in permutate_neasted_iterable(self.edge_map)
        ]
        return mapping

    @property
    def vertices_with_local_id(self) -> list[vertex_local_id]:
        """Look up the vertex dict and find all vertices assigned to this
        (self) block. Return tuples containing the vertices of this block
        together with their respective position / ordering.
        """
        return [
            vertex_local_id(vertex, block_vertex.local_vertex_id)
            for vertex, block_vertex_list in Vertex.vertex_dict.items()
            for block_vertex in block_vertex_list
            if block_vertex.block is self
        ]

    @property
    def vertices(self):
        """Return all vertices of this block with correct ordering according
        to their local location in the block
        """
        return [
            vert
            for vert, _ in sorted(
                self.vertices_with_local_id,
                key=lambda x: x.local_id,
            )
        ]

    @property
    def vertices_by_global_id(self):
        return [vertex.id for vertex in self.vertices]

    @property
    def front_face(self):
        return [self.vertices[i] for i in self.face_map.get("front")]

    @property
    def blockMesh_format(self):
        return (
            "hex ("
            + " ".join(map(str, self.vertices_by_global_id))
            + ") "
            + self.name
            + " ("
            + " ".join(map(str, self.cells))
            + ") "
            + "simpleGrading (1 1 1)"
        )

    def __repr__(self):
        return (
            self.__class__.__qualname__
            + f"-{self.id}("
            + ",".join(map(repr, self.vertices))
            + f",name={self.name}"
            + ")"
        )

    def __hash__(self):
        return hash((type(self), self.id))


v0 = Vertex(0, 0, 0)
v1 = Vertex(1, 0, 0)
v2 = Vertex(1, 1, 0)
v3 = Vertex(0, 1, 0)
v4 = Vertex(0, 0, 1)
v5 = Vertex(1, 0, 1)
v6 = Vertex(1, 1, 1)
v7 = Vertex(0, 1, 1)

v8 = Vertex(1, 2, 0)
v9 = Vertex(0, 2, 0)
v10 = Vertex(1, 2, 1)
v11 = Vertex(0, 2, 1)


b0 = Block(v0, v1, v2, v3, v4, v5, v6, v7)
b1 = Block(v1, v8, v9, v2, v5, v10, v11, v6)

b0.vertices

v1.global_id

print()
