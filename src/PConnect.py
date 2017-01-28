import numpy as np
import scipy.spatial as ssp


class Connect(object):
    """docstring for Export"""
    def __init__(self):
        super(Connect, self).__init__()

    def getNearestNeighbours(self, vertices, radius=0.001):
        V = np.array(vertices)
        tree = ssp.cKDTree(V)
        pairs = tree.query_pairs(radius, p=2., eps=0)
        return pairs

    def getBlockVertices(self, block):
        vertices = list()
        for uline in block.getULines():
            vertices += uline
        return vertices

    def block2VC(self, block):

        vertices = self.getBlockVertices(block)
        connectivity = list()

        U, V = block.getDivUV()
        up = U + 1
        for u in range(U):
            for v in range(V):
                p1 = v * up + u
                p2 = p1 + up
                p3 = p2 + 1
                p4 = p1 + 1
                connectivity.append((p1, p2, p3, p4))

        return (vertices, connectivity)

    def connectBlocks(self, block_1, block_2, radius=0.001):

        vertices_1, connectivity_1 = block_1
        vertices_2, connectivity_2 = block_2
        vertices = vertices_1 + vertices_2
        lv1 = len(vertices_1)

        connectivity_2mod = list()
        for cell in connectivity_2:
            new_cell = [vertex+lv1 for vertex in cell]
            connectivity_2mod.append(new_cell)

        pairs = self.getNearestNeighbours(vertices, radius=radius)
        pairs = list(pairs)
        I, J = zip(*pairs)

        connectivity_2_new = list()
        for cell in connectivity_2mod:
            new_cell = list()
            for vertex in cell:
                new_vertex = vertex
                if vertex in J:
                    new_vertex = I[J.index(vertex)]
                new_cell.append(new_vertex)
            connectivity_2_new.append(new_cell)

        connectivity = connectivity_1 + connectivity_2_new

        return (vertices, connectivity)

    def writeFLMATest(self, name, vertices, connectivity):

        with open(name, 'w') as f:

            number_of_vertices_2D = len(vertices)

            depth = 0.1
            numvertex = '8'

            # write number of points to FLMA file (*2 for z-direction)
            f.write(str(2 * number_of_vertices_2D) + '\n')

            signum = -1.

            # write x-, y- and z-coordinates to FLMA file
            # loop 1D direction (symmetry)
            for _ in range(2):
                for vertex in vertices:
                    f.write(str(vertex[0]) + ' ' + str(vertex[1]) +
                            ' ' + str(signum * depth / 2.0) + ' ')
                signum = 1.

            # write number of cells to FLMA file
            cells = len(connectivity)
            f.write('\n' + str(cells) + '\n')

            # write cell connectivity to FLMA file
            for cell in connectivity:
                connectivity = str(cell[0]) + ' ' + \
                               str(cell[1]) + ' ' + \
                               str(cell[2]) + ' ' + \
                               str(cell[3]) + ' ' + \
                               str(cell[0]+number_of_vertices_2D) + ' ' + \
                               str(cell[1]+number_of_vertices_2D) + ' ' + \
                               str(cell[2]+number_of_vertices_2D) + ' ' + \
                               str(cell[3]+number_of_vertices_2D) + '\n'

                f.write(numvertex + '\n')
                f.write(connectivity)

            # write FIRE element type (FET) to FLMA file
            fetHEX = '5'
            f.write('\n' + str(cells) + '\n')
            for i in range(cells):
                f.write(fetHEX + ' ')
            f.write('\n\n')

            # write FIRE selections to FLMA file
            f.write('0')
