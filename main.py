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
    2. Geomerty
    3. Vertices
    4. Blocks
    5. Edges
    6. Faces
    7. Patches
    8. mergePatchPairs
    9. Footer
    
The most important part are the vertices. Vertices should map to each block 
they belong and vice versa. Courrently a defaultdict creating empty lists where 
each block is appended is used. The vertices are returned if the block is in 
the block list of the respective vertex. I currently don't know how good this 
will scale but it is working right now. 
"""
from pprint import pprint
import collections
import itertools
import functools

block_vertex = collections.namedtuple("block_vertex", "block vertex_id")


class Vertex:
    """The Vertex Class defines locations in 3d cartesian space. Vertices are
    used to form blocks, faces and edges.
    """

    count: int = 0
    vertex_dict: collections.defaultdict = collections.defaultdict(list[block_vertex])

    @staticmethod
    def print_dict():
        pprint(Vertex.vertex_dict)

    @staticmethod
    def vertices():
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

        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if getattr(self, "id", None):
            raise ValueError("id already set")
        self._id = int(value)

    @property
    def connected_to(self) -> set:
        """Return a list of all vertices connected to this vertex"""
        return set(
            [
                block.vertices[vertex_id_in_block]
                for block, vert_id in Vertex.vertex_dict.get(self, [])
                for vertex_id_in_block in block.vertex_connection_map.get(vert_id)
            ]
        )

    def __repr__(self):
        return (
            self.__class__.__qualname__
            + f"-{self.id}(x={self.x!r},y={self.y!r},z={self.z!r})"
        )

    def __str__(self):
        return str(tuple(self.x, self.y, self.z)) + f" if-{self.id}"

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
    face_map = dict(
        bottom=(0, 1, 2, 3),
        left=(4, 0, 3, 7),
        front=(4, 5, 1, 0),
        right=(1, 5, 6, 2),
        back=(3, 2, 6, 7),
        top=(4, 5, 6, 7),
    )

    edge_map = tuple(
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

    def __init__(self, *verts, name=None):
        assert [verts.count(vert) for vert in verts].count(1) == 8, (
            f"Need exactly 8 unique vertices to create a block, got {len(verts)}:"
            + "\n\t"
            + f"{verts}"
        )
        self.id = type(self).count
        type(self).count += 1
        self.name = name or f"Block-{self.id}"
        for i, vert in enumerate(verts):
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
        mapping = collections.defaultdict(list)
        [
            mapping[permut[0]].append(permut[1])
            for vertex_pair in Block.edge_map
            for permut in itertools.permutations(vertex_pair)
        ]
        return mapping

    @property
    def vertex_with_id_in_block(self) -> tuple[Vertex, int]:
        """Look up the vertex dict and find all vertices assigned to this
        (self) block. Return tuples containing the vertices of this block
        together with their respective position / ordering.
        """
        return [
            (vertex, block_vertex.vertex_id)
            for vertex, block_vertex_list in Vertex.vertex_dict.items()
            for block_vertex in block_vertex_list
            if block_vertex.block is self
        ]

    @property
    def vertices(self):
        """Return all vertices of this block with correct ordering according to
        their local location in the block
        """
        return [
            vert
            for vert, _ in sorted(
                self.vertex_with_id_in_block,
                key=lambda x: x[1],
            )
        ]

    @property
    def front_face(self):
        return [self.vertices[i] for i in self.face_map.get("front")]

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

v1.connected_to

print()
