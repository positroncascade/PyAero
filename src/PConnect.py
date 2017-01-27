import scipy.spatial as ssp


class Connect(object):
    """docstring for Export"""
    def __init__(self):
        super(Connect, self).__init__()

    def getNearestNeighbours(self, set1, set2, radius=0.001):
        """Nearest neighbour search using KD-trees. Get all indices of
        points in set1 which are within distance radius to set2.
        And vice versa.

        Args:
            set1 (list): Points in set1 [(x1, y1), (x2, y2), ...]
            set2 (list): Points in set2 [(x1, y1), (x2, y2), ...]
            radius (float): Search radius

        Return (list): List with indices of set1 which are within a distance
                       less than radius to set2
        """
        tree_1 = ssp.cKDTree(set1)
        tree_2 = ssp.cKDTree(set2)
        id1 = tree_2.query_ball_tree(tree_1, radius, p=2., eps=0)
        id2 = tree_1.query_ball_tree(tree_2, radius, p=2., eps=0)

        indices_1 = [e[0] for e in id1 if e]
        indices_2 = [e[0] for e in id2 if e]

        return indices_1, indices_2

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
        vp = V + 1
        for i in range(U):
            for j in range(V):
                p1 = j * up + i + 1
                p2 = (vp + j) * up + i + 1
                p3 = p2 - 1
                p4 = p1 - 1
                p5 = (j + 1) * up + i + 1
                p6 = (vp + j + 1) * up + i + 1
                p7 = p6 - 1
                p8 = p5 - 1
                connectivity.append((p1, p2, p3, p4, p5, p6, p7, p8))

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

        # indices of vertices_1 within radius to vertices_2 and vice versa
        nn_12, nn_21 = self.getNearestNeighbours(vertices_1, vertices_2,
                                                 radius=radius)
        nn_21 = [vertex+lv1 for vertex in nn_21]

        connectivity_2 = list()
        for cell in connectivity_2mod:
            new_cell = list()
            for vertex in cell:
                new_vertex = vertex
                if vertex in nn_21:
                    idx = nn_21.index(vertex)
                    new_vertex = nn_12[idx]
                new_cell.append(new_vertex)
            connectivity_2.append(new_cell)

        connectivity = connectivity_1 + connectivity_2
        return (vertices, connectivity)

    def writeFLMATest(self, vertices, connectivity):

        with open('test_Connect.flma', 'w') as f:

            depth = 0.1
            numvertex = '8'

            # write number of points to FLMA file (*2 for z-direction)
            f.write(str(2 * len(vertices)) + '\n')

            signum = -1.

            # write x-, y- and z-coordinates to FLMA file
            # loop 1D direction (symmetry)
            for j in range(2):
                for vertex in vertices:
                    f.write(str(vertex[0]) + ' ' + str(vertex[1]) +
                            ' ' + str(signum * depth / 2.0) + ' ')
                signum = 1.

            # write number of cells to FLMA file
            cells = len(connectivity)
            f.write('\n' + str(cells) + '\n')

            # write cell connectivity to FLMA file
            for cell in connectivity:
                connectivity = str(cell[0]) + ' ' + str(cell[1]) + ' ' + \
                    str(cell[2]) + ' ' + str(cell[3]) + ' ' + str(cell[4]) + \
                    ' ' + str(cell[5]) + ' ' + str(cell[6]) + ' ' + \
                    str(cell[7]) + '\n'

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
