import numpy as np
import scipy.spatial as ssp


class Export(object):
    """docstring for Export"""
    def __init__(self, blocks):
        super(Export, self).__init__()
        self.blocks = blocks

    def getNearestNeighbours(set1, set2, radius=0.001):
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

    def connectBlocks(self, name='', depth=0.1):

        vertices = 0
        ulines = dict()
        connectivity = dict()
        I = 0
        J = 0

        # loop over all individual mesh blocks
        for block in self.blocks:

            U, V = block.getDivUV()
            vertices += (U + 1) * (V + 1)
            ulines.setdefault(block.name, []).append(block.getULines())

            # cell connectivity
            up = U + 1
            vp = V + 1
            for i in range(U):
                for j in range(V):

                    I += i
                    J += j

                    p1 = J * up + I + 1
                    p2 = (vp + J) * up + I + 1
                    p3 = p2 - 1
                    p4 = p1 - 1
                    p5 = (J + 1) * up + I + 1
                    p6 = (vp + J + 1) * up + I + 1
                    p7 = p6 - 1
                    p8 = p5 - 1

                    connectivity.setdefault(block.name, []).append(
                        (p1, p2, p3, p4, p5, p6, p7, p8))

        number_of_blocks = len(self.blocks)
        for block in range(number_of_blocks-1):
            points_1 = self.getPoints(self.blocks[block])
            points_2 = self.getPoints(self.blocks[block+1])
            # indices of points_1 within radius to points_2 and vice versa
            nn_12, nn_21 = self.getNearestNeighbours(points_1, points_2,
                                                     radius=0.001)

    def getPoints(self, block):
        points = list()
        for uline in block.getULines:
            points.append(uline)
        return points
