
import numpy as np

from PUtils import Utils as Utils
import PLogger as logger


class Windtunnel(object):
    """docstring for Windtunnel"""
    def __init__(self):
        super(Windtunnel, self).__init__()

    def AirfoilMesh(self, name='', contour=None, divisions=15, ratio=3.0,
                    thickness=0.04):

        # logger.log.info('Divisions %s' % (divisions))
        # logger.log.info('Ratio %s' % (ratio))
        # logger.log.info('Thickness %s' % (thickness))
        # logger.log.info('x-coo %s' % (contour[0]))

        x, y = contour

        # block mesh around airfoil contour
        block_airfoil = BlockMesh(name=name)
        block_airfoil.addLine([np.array([x, y])])
        line = block_airfoil.getLine(line=0)
        print 'Line     ', line
        block_airfoil.extrudeLine(line, length=thickness, direction=3,
                                  divisions=divisions, ratio=ratio)

        # compile first line of trailing edge block
        first = np.array(block_airfoil.getLine(line=0, direction='v'))
        last = np.array(block_airfoil.getLine(line=-1, direction='v'))
        last_reversed = last[:, ::-1]
        vec = first[:, 0] - last_reversed[:, -1]
        div_te = 3
        pte = list()
        pte.append(last_reversed)
        for i in range(1, div_te):
            line = float(i) / div_te * vec + last_reversed[:, -1]
            pte.append(line.reshape(2, 1))
        pte.append(first)
        line = np.concatenate(pte, axis=1)

        # trailing edge block mesh
        block_te = BlockMesh(name + '_TE')
        block_te.addLine(line)
        line = block_te.getULines()
        block_te.extrudeLine(line, length=0.04, direction=3, divisions=6,
                             ratio=3.0)
        block_te.distribute(direction='u', line_number=7)
        # block_te.distribute(direction='v', line_number=1)
        # block_te.distribute(direction='v', line_number=3)

        # # smooth trailing edge block
        # smooth = Smooth(block_te)
        # nodes = smooth.selectNodes(domain='interior')
        # block_te_smooth = smooth.smooth(nodes, iterations=1,
        #                                 algorithm='laplace')

        return block_airfoil, block_te


class BlockMesh(object):

    def __init__(self, name='block'):
        self.name = name
        self.ULines = list()
        self.block = dict()

    def addLine(self, line):
        # u is list of tuples representing one mesh line
        self.ULines.append(line)
        self.updateBlock()

    def updateBlock(self):
        node = 0
        for j, line in enumerate(self.getULines()):
            for i, point in enumerate(line):
                node += 1
                self.block[(i, j)] = (node, point)

    def getULines(self):
        return self.ULines

    def getVLines(self):
        lines = list()
        U, V = self.getDivUV()
        logger.log.info('U, V %s %s' % (U, V))
        for i in range(U + 1):
            vx = list()
            vy = list()
            for u in self.getULines():
                logger.log.info('u %s' % (u))
                vx.append(u[0][i])
                vy.append(u[1][i])
            lines.append((vx, vy))

        return lines

    def getLine(self, line=0, direction='u'):
        if direction.lower() == 'u':
            lines = self.getULines()
        if direction.lower() == 'v':
            lines = self.getVLines()
        return lines[line]

    def getDivUV(self):
        u = len(self.ULines[0][0]) - 1
        v = len(self.ULines) - 1
        return u, v

    def extrudeLine(self, line, direction=0, length=0.1, divisions=1,
                    ratio=1.00001, constant=False):
        x = np.copy(line[0][0])
        y = np.copy(line[0][1])
        if constant and direction == 0:
            x.fill(length)
            self.addLine((x, y))
        elif constant and direction == 1:
            y.fill(length)
            self.addLine((x, y))
        elif direction == 3:
            spacing = self.spacing(divisions=divisions, ratio=ratio,
                                   thickness=length)
            normals = self.curveNormals(x, y)
            for i in range(1, len(spacing)):
                xo = x + spacing[i] * normals[:, 0]
                yo = y + spacing[i] * normals[:, 1]
                self.addLine((xo, yo))

    def distribute(self, direction='u', line_number=1):

        U, V = self.getDivUV()

        div = {'u': U, 'v': V}

        if direction == 'u':
            line = self.ULines[line_number - 1]
        elif direction == 'v':
            line = self.getVLines()[line_number - 1]

        p1 = np.array((line[0][0], line[1][0]))
        p2 = np.array((line[0][-1], line[1][-1]))
        vec = p2 - p1

        for i in range(1, div[direction]):
            delta = p1 + i * vec / div[direction]
            line[0][i] = delta[0]
            line[1][i] = delta[1]

    def spacing(self, divisions=10, ratio=1.0, thickness=1.0):
        """Calculate point distribution on a line

        Args:
            divisions (int, optional): Number of subdivisions
            ratio (float, optional): Ratio of last to first subdivision size
            thickness (float, optional): length of line

        Returns:
            TYPE: Description
        """
        ratio = 1.0 / ratio

        if divisions == 1:
            sp = [0.0, 1.0]
            return sp

        growth = ratio**(1.0 / (float(divisions) - 1.0))

        if growth == 1.0:
            growth = 1.0 + 1.0e-10

        s0 = 1.0
        s = [s0]
        for i in range(1, divisions + 1):
            app = s0 * growth**i
            s.append(app)
        sp = np.array(s)
        sp -= sp[0]
        sp /= sp[-1]
        sp *= thickness
        return sp

    def curveNormals(self, x, y, closed=False):
        istart = 0
        iend = 0
        n = list()

        for i, dummy in enumerate(x):

            if closed:
                if i == len(x) - 1:
                    iend = -i - 1
            else:
                if i == 0:
                    istart = 1
                if i == len(x) - 1:
                    iend = -1

            a = np.array([x[i + 1 + iend] - x[i - 1 + istart],
                          y[i + 1 + iend] - y[i - 1 + istart]])
            e = Utils.unit_vector(a)
            n.append([e[1], -e[0]])
            istart = 0
            iend = 0
        return np.array(n)

    def connectBlock(self, block):
        pass

    def writeFLMA(self, filename, depth=0.1):

        u, v = self.getDivUV()
        points = (u + 1) * (v + 1)

        with open(filename, 'w') as f:

            numvertex = '8'

            # number of points (*2 for z-direction)
            f.write(str(2 * points) + '\n')

            signum = -1.

            # loop 1D direction (symmetry)
            for j in range(2):
                # point coordinates
                for ul in self.getULines():
                    for i in range(len(ul[0])):
                        f.write(str(ul[0][i]) + ' ' + str(ul[1][i]) + ' ' +
                                str(signum * depth / 2.0) + ' ')
                signum = 1.

            # number of cells
            cells = u * v
            f.write('\n' + str(cells) + '\n')

            # cell connectivity
            up = u + 1
            vp = v + 1
            for i in range(u):
                for j in range(v):

                    p1 = j * up + i + 1
                    p2 = (vp + j) * up + i + 1
                    p3 = p2 - 1
                    p4 = p1 - 1
                    p5 = (j + 1) * up + i + 1
                    p6 = (vp + j + 1) * up + i + 1
                    p7 = p6 - 1
                    p8 = p5 - 1

                    connectivity = str(p1) + ' ' + str(p2) + ' ' + str(p3) + \
                        ' ' + str(p4) + ' ' + str(p5) + ' ' + str(p6) + \
                        ' ' + str(p7) + ' ' + str(p8) + '\n'

                    f.write(numvertex + '\n')
                    f.write(connectivity)

            # write FIRE element type (FET)
            fetHEX = '5'
            f.write('\n' + str(cells) + '\n')
            for i in range(cells):
                f.write(fetHEX + ' ')
            f.write('\n\n')

            # FIRE selctions
            f.write('0')
