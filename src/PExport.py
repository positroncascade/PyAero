import numpy as np
import scipy.spatial as ssp


class Export(object):
    """docstring for Export"""
    def __init__(self, blocks):
        super(Export, self).__init__()
        self.blocks = blocks

    def getNearestNeighbours(set1, set2, radius):
        """Nearest neighbour search. Get all indices of points in d1
        which are within distance radius to d2.

        Args:
            set1 (list): Points in set1 [(x1, y1), (x2, y2), ...]
            set2 (list): Points in set2 [(x1, y1), (x2, y2), ...]
            radius (float): Search radius

        Return (list): List with indices of set1 which are within a distance
                       less than radius to set2
        """
        tree_1 = ssp.cKDTree(set1)
        tree_2 = ssp.cKDTree(set2)
        idx = tree_2.query_ball_tree(tree_1, radius, p=2., eps=0)

        indices = [e[0] for e in idx if e]

        return indices

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

        for block in len(self.blocks()):

