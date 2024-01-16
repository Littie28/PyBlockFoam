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
    
The most important part are the vertices. Vertices should map to 
each block they belong and vice versa. Courrently a defaultdict 
creating empty lists where each block is appended is used. The 
vertices are returned if the block is in the block list of the 
respective vertex. I currently don't know how good this will 
scale but it is working right now. 
"""

from pprint import pprint
import collections


class Vertex:
    count: int = 0
    vertex_dict: collections.defaultdict = collections.defaultdict(list)

    def __init__(self):
        self.id = type(self).count
        type(self).count += 1

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

    def __init__(self, vert0, vert1):
        self.id = type(self).count
        type(self).count += 1

        Vertex.vertex_dict[vert0].append(self)
        Vertex.vertex_dict[vert1].append(self)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if getattr(self, "id", None):
            raise ValueError("id already set")
        self._id = int(value)

    @property
    def vertices(self):
        return [key for key, val in Vertex.vertex_dict.items() if self in val]

    def __repr__(self):
        return self.__class__.__qualname__ + f" {self.id} "

    def __hash__(self):
        return hash((type(self), self.id))


v0 = Vertex()
v1 = Vertex()
v2 = Vertex()
v3 = Vertex()
v4 = Vertex()
v5 = Vertex()

b0 = Block(v0, v1)
b1 = Block(v2, v3)
b2 = Block(v0, v3)

b0.vertices

print()
