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
"""
