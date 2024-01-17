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

block_vertex = collections.namedtuple("block_vertex", "block vertex_id")


class Vertex:
    count: int = 0
    vertex_dict: collections.defaultdict = collections.defaultdict(list[block_vertex])

    @staticmethod
    def print_dict():
        pprint(Vertex.vertex_dict)

    def __init__(self, x, y, z):
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

    def __repr__(self):
        return self.__class__.__qualname__ + f" {self.id} "

    def __hash__(self):
        return hash((type(self), self.id))


class Block:
    count: int = 0

    def __init__(self, *verts):
        self.id = type(self).count
        type(self).count += 1

        assert len(verts) == 8

        for i, vert in enumerate(verts):
            Vertex.vertex_dict[vert].append(block_vertex(self, i))

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if getattr(self, "id", None):
            raise ValueError("id already set")
        self._id = int(value)

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
        their local location in the block"""
        return [
            vert
            for vert, _ in sorted(
                self.vertex_with_id_in_block,
                key=lambda x: x[1],
            )
        ]

    def __repr__(self):
        return self.__class__.__qualname__ + f" {self.id} "

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

print()
