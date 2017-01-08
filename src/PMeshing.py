
import os
import copy
import numpy as np
import scipy.interpolate as si

import PyAero
from PUtils import Utils as Utils
from PSettings import OUTPUTDATA
import PLogger as logger


class Windtunnel(object):
    """docstring for Windtunnel"""
    def __init__(self):
        super(Windtunnel, self).__init__()

        self.blocks = []

    def AirfoilMesh(self, name='', contour=None, divisions=15, ratio=3.0,
                    thickness=0.04):

        # get airfoil contour coordinates
        x, y = contour

        # make a list point tuples
        # [(x1, y1), (x2, y2), (x3, y3), ... , (xn, yn)]
        line = zip(x, y)

        # block mesh around airfoil contour
        block_airfoil = BlockMesh(name=name)
        block_airfoil.addLine(line)
        block_airfoil.extrudeLine(line, length=thickness, direction=3,
                                  divisions=divisions, ratio=ratio)

        self.block_airfoil = block_airfoil
        self.blocks.append(block_airfoil)

    def TrailingEdgeMesh(self, name='', te_divisions=3,
                         length=0.04, divisions=6, ratio=3.0):

        # compile first line of trailing edge block
        first = self.block_airfoil.getLine(number=0, direction='v')
        last = self.block_airfoil.getLine(number=-1, direction='v')
        last_reversed = copy.deepcopy(last)
        last_reversed.reverse()

        vec = np.array(first[0]) - np.array(last[0])
        line = copy.deepcopy(last_reversed)
        for i in range(1, te_divisions):
            p = last_reversed[-1] + float(i) / te_divisions * vec
            # p is type numpy.float, so convert it to float
            line.append((float(p[0]), float(p[1])))
        line += first

        # trailing edge block mesh
        block_te = BlockMesh(name=name)
        block_te.addLine(line)
        block_te.extrudeLine(line, length=length, direction=4,
                             divisions=divisions, ratio=ratio)

        # equidistant point distribution
        block_te.distribute(direction='u', number=-1)

        # make a transfinite interpolation
        # i.e., recreate pooints inside the block
        block_te.transfinite()

        self.block_te = block_te
        self.blocks.append(block_te)

    def TunnelMesh(self, name=''):
        block_tunnel = BlockMesh(name=name)

        # line composed of trailing edge and airfoil meshes
        line = self.block_te.getVLines()[-1]
        line.reverse()
        del line[-1]
        line += self.block_airfoil.getULines()[-1]
        del line[-1]
        line += self.block_te.getVLines()[0]
        block_tunnel.addLine(line)

        # line composed of upper, lower and front line segments
        p1 = np.array((block_tunnel.getULines()[0][0][0], 2.0))
        p2 = np.array((0.0, 2.0))
        p3 = np.array((0.0, -2.0))
        p4 = np.array((block_tunnel.getULines()[0][-1][0], -2.0))

        # upper line of wind tunnel
        line = list()
        vec = p2 - p1
        for t in np.linspace(0.0, 1.0, 100):
            p = p1 + t * vec
            line.append(p.tolist())
        del line[-1]
        # front half circle of wind tunnel
        r = 2.0
        for phi in np.linspace(90.0, 270.0, 200):
            phir = np.radians(phi)
            x = r * np.cos(phir)
            y = r * np.sin(phir)
            line.append((x, y))
        del line[-1]
        # lower line of wind tunnel
        vec = p4 - p3
        for t in np.linspace(0.0, 1.0, 100):
            p = p3 + t * vec
            line.append(p.tolist())

        line = np.array(line)
        tck, u = si.splprep(line.T, s=0, k=1)
        qq = 0
        if qq == 1:
            t = np.linspace(0.0, 1.0, num=len(block_tunnel.getULines()[0]))
        else:
            xx = np.linspace(-3.0, 3.0, len(block_tunnel.getULines()[0]))
            t = (np.tanh(xx) + 1.0) / 2.0
        line = si.splev(t, tck, der=0)
        line = zip(line[0].tolist(), line[1].tolist())

        block_tunnel.addLine(line)

        p5 = np.array(block_tunnel.getULines()[0][0])
        p6 = np.array(block_tunnel.getULines()[0][-1])

        # first vline
        vline1 = BlockMesh.makeLine(p5, p1, divisions=50, ratio=10.0)

        # last vline
        vline2 = BlockMesh.makeLine(p6, p4, divisions=50, ratio=10.0)

        boundary = [block_tunnel.getULines()[0],
                    block_tunnel.getULines()[-1],
                    vline1,
                    vline2]
        block_tunnel.transfinite(boundary=boundary)

        # blending between normals (inner lines) and transfinite (outer lines)
        ulines = list()
        old_ulines = block_tunnel.getULines()

        for j, uline in enumerate(block_tunnel.getULines()):

            # skip first and last line
            if j == 0 or j == len(block_tunnel.getULines())-1:
                ulines.append(uline)
                continue

            line = list()
            xo, yo = zip(*old_ulines[0])
            xo = np.array(xo)
            yo = np.array(yo)
            normals = BlockMesh.curveNormals(xo, yo)

            for i, point in enumerate(uline):

                # skip first and last point
                if i == 0 or i == len(uline)-1:
                    line.append(point)
                    continue

                pt = np.array(old_ulines[j][i])
                pto = np.array(old_ulines[0][i])
                vec = pt - pto
                # projection of vec into normal
                dist = np.dot(vec, normals[i]) / np.linalg.norm(normals[i])
                pn = pto + dist * normals[i]
                v = float(j) / float(len(block_tunnel.getULines()))
                exp = 0.6
                pnew = (1.0-v**exp) * pn + v**exp * pt
                line.append((pnew.tolist()[0], pnew.tolist()[1]))

            ulines.append(line)

        block_tunnel = BlockMesh(name=name)
        for uline in ulines:
            block_tunnel.addLine(uline)

        ij = [0, 25, 0, len(block_tunnel.getULines())-1]
        block_tunnel.transfinite(ij=ij)
        ij = [len(block_tunnel.getVLines())-26,
              len(block_tunnel.getVLines())-1,
              0,
              len(block_tunnel.getULines())-1]
        block_tunnel.transfinite(ij=ij)

        sm = 1
        if sm == 1:
            smooth = Smooth(block_tunnel)

            nodes = smooth.selectNodes(domain='interior')
            block_tunnel = smooth.smooth(nodes, iterations=1,
                                         algorithm='laplace')
            ij = [1, 25, 1, len(block_tunnel.getULines())-2]
            nodes = smooth.selectNodes(domain='ij', ij=ij)
            block_tunnel = smooth.smooth(nodes, iterations=3,
                                         algorithm='laplace')
            ij = [len(block_tunnel.getVLines())-27,
                  len(block_tunnel.getVLines())-2,
                  1,
                  len(block_tunnel.getULines())-2]
            nodes = smooth.selectNodes(domain='ij', ij=ij)
            block_tunnel = smooth.smooth(nodes, iterations=3,
                                         algorithm='laplace')

        self.block_tunnel = block_tunnel
        self.blocks.append(block_tunnel)

    def TunnelMeshBack(self, name=''):
        block_tunnel_back = BlockMesh(name=name)

        # line composed of trailing edge and block_tunnel meshes
        line = self.block_tunnel.getVLines()[-1]
        line.reverse()
        del line[-1]
        line += self.block_te.getULines()[-1]
        del line[-1]
        line += self.block_tunnel.getVLines()[0]
        block_tunnel_back.addLine(line)

        #
        p1 = np.array((0.0, 2.0))
        p4 = np.array((0.0, -2.0))
        p7 = np.array((5.0, 2.0))
        p8 = np.array((5.0, -2.0))

        upper = BlockMesh.makeLine(p7, p1, divisions=100, ratio=0.1)
        lower = BlockMesh.makeLine(p8, p4, divisions=100, ratio=0.1)
        left = line
        right = BlockMesh.makeLine(p8, p7, divisions=len(left)-1, ratio=1.0)

        boundary = [upper, lower, right, left]
        block_tunnel_back.transfinite(boundary=boundary)

        self.block_tunnel_back = block_tunnel_back

        smooth = Smooth(block_tunnel_back)
        nodes = smooth.selectNodes(domain='interior')
        block_tunnel_back = smooth.smooth(nodes, iterations=3,
                                          algorithm='laplace')

        self.block_tunnel_back = block_tunnel_back
        self.blocks.append(block_tunnel_back)


class BlockMesh(object):

    def __init__(self, name='block'):
        self.name = name
        self.ULines = list()

    def addLine(self, line):
        # line is a list of (x, y) tuples
        self.ULines.append(line)

    def getULines(self):
        return self.ULines

    def getVLines(self):
        vlines = list()
        U, V = self.getDivUV()

        # loop over all u-lines
        for i in range(U + 1):
            # prepare new v-line
            vline = list()
            # collect i-th point on each u-line
            for uline in self.getULines():
                vline.append(uline[i])
            vlines.append(vline)

        return vlines

    def getLine(self, number=0, direction='u'):
        if direction.lower() == 'u':
            lines = self.getULines()
        if direction.lower() == 'v':
            lines = self.getVLines()
        return lines[number]

    def getDivUV(self):
        u = len(self.getULines()[0]) - 1
        v = len(self.getULines()) - 1
        return u, v

    def getNodeCoo(self, node):
        I, J = node[0], node[1]
        uline = self.getULines()[J]
        point = uline[I]
        return np.array(point)

    def setNodeCoo(self, node, new_pos):
        I, J = node[0], node[1]
        uline = self.getULines()[J]
        uline[I] = new_pos
        return

    @staticmethod
    def makeLine(p1, p2, divisions=1, ratio=1.0):
        vec = p2 - p1
        dist = np.linalg.norm(vec)
        spacing = BlockMesh.spacing(divisions=divisions,
                                    ratio=ratio, thickness=dist)
        line = list()
        line.append((p1.tolist()[0], p1.tolist()[1]))
        for i in range(1, len(spacing)):
            p = p1 + spacing[i] * Utils.unit_vector(vec)
            line.append((p.tolist()[0], p.tolist()[1]))
        del line[-1]
        line.append((p2.tolist()[0], p2.tolist()[1]))
        return line

    def extrudeLine(self, line, direction=0, length=0.1, divisions=1,
                    ratio=1.00001, constant=False):
        x, y = zip(*line)
        x = np.array(x)
        y = np.array(y)
        if constant and direction == 0:
            x.fill(length)
            line = zip(x.tolist(), y.tolist())
            self.addLine(line)
        elif constant and direction == 1:
            y.fill(length)
            line = zip(x.tolist(), y.tolist())
            self.addLine(line)
        elif direction == 3:
            spacing = self.spacing(divisions=divisions,
                                   ratio=ratio,
                                   thickness=length)
            normals = self.curveNormals(x, y)
            for i in range(1, len(spacing)):
                xo = x + spacing[i] * normals[:, 0]
                yo = y + spacing[i] * normals[:, 1]
                line = zip(xo.tolist(), yo.tolist())
                self.addLine(line)
        elif direction == 4:
            spacing = self.spacing(divisions=divisions,
                                   ratio=ratio,
                                   thickness=length)
            normals = self.curveNormals(x, y)
            normalx = normals[:, 0].mean()
            normaly = normals[:, 1].mean()
            for i in range(1, len(spacing)):
                xo = x + spacing[i] * normalx
                yo = y + spacing[i] * normaly
                line = zip(xo.tolist(), yo.tolist())
                self.addLine(line)

    def distribute(self, direction='u', number=0, type='constant'):

        if direction == 'u':
            line = np.array(self.getULines()[number])
        elif direction == 'v':
            line = np.array(self.getVLines()[number])

        # interpolate B-spline through data points
        # here, a linear interpolant is derived "k=1"
        # splprep returns:
        # tck ... tuple (t,c,k) containing the vector of knots,
        #         the B-spline coefficients, and the degree of the spline.
        #   u ... array of the parameters for each given point (knot)
        tck, u = si.splprep(line.T, s=0, k=1)

        if type == 'constant':
            t = np.linspace(0.0, 1.0, num=len(line))
        if type == 'transition':
            first = np.array(self.getULines()[0])
            last = np.array(self.getULines()[-1])
            tck_first, u_first = si.splprep(first.T, s=0, k=1)
            tck_last, u_last = si.splprep(last.T, s=0, k=1)
            if number < 0.0:
                number = len(self.getVLines())
            v = float(number) / float(len(self.getVLines()))
            t = (1.0 - v) * u_first + v * u_last

        # evaluate function at any parameter "0<=t<=1"
        line = si.splev(t, tck, der=0)
        line = zip(line[0].tolist(), line[1].tolist())
        self.getULines()[number] = line

    def connect(self, block_1, block_2):
        pass

    @staticmethod
    def spacing(divisions=10, ratio=1.0, thickness=1.0):
        """Calculate point distribution on a line

        Args:
            divisions (int, optional): Number of subdivisions
            ratio (float, optional): Ratio of last to first subdivision size
            thickness (float, optional): length of line

        Returns:
            TYPE: Description
        """

        if divisions == 1:
            sp = [0.0, 1.0]
            return np.array(sp)

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

    def mapLines(self, line_1, line_2):
        """Map the distribution of points from one line to another line

        Args:
            line_1 (LIST): Source line (will be mapped)
            line_2 (LIST): Destination line (upon this line_1 is mapped)
        """
        pass

    @staticmethod
    def curveNormals(x, y, closed=False):
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

    def transfinite(self, boundary=[], ij=[]):
        """Make a transfinite interpolation.

        http://en.wikipedia.org/wiki/Transfinite_interpolation

                       upper
                --------------------
                |                  |
                |                  |
           left |                  | right
                |                  |
                |                  |
                --------------------
                       lower

        Example input for the lower boundary:
            lower = [(0.0, 0.0), (0.1, 0.3),  (0.5, 0.4)]
        """

        self.ULines_Save = copy.deepcopy(self.getULines())

        if boundary:
            lower = boundary[0]
            upper = boundary[1]
            left = boundary[2]
            right = boundary[3]
        elif ij:
            lower = self.getULines()[ij[2]][ij[0]:ij[1]+1]
            upper = self.getULines()[ij[3]][ij[0]:ij[1]+1]
            left = self.getVLines()[ij[0]][ij[2]:ij[3]+1]
            right = self.getVLines()[ij[1]][ij[2]:ij[3]+1]
        else:
            lower = self.getULines()[0]
            upper = self.getULines()[-1]
            left = self.getVLines()[0]
            right = self.getVLines()[-1]

        # FIXME
        # FIXME left and right need to swapped from input
        # FIXME
        # FIXME like: left, right = right, left
        # FIXME

        lower = np.array(lower)
        upper = np.array(upper)
        left = np.array(left)
        right = np.array(right)

        # interpolate B-spline through data points
        # here, a linear interpolant is derived "k=1"
        # splprep returns:
        # tck ... tuple (t,c,k) containing the vector of knots,
        #         the B-spline coefficients, and the degree of the spline.
        #   u ... array of the parameters for each given point (knot)
        tck_lower, u_lower = si.splprep(lower.T, s=0, k=1)
        tck_upper, u_upper = si.splprep(upper.T, s=0, k=1)
        tck_left, u_left = si.splprep(left.T, s=0, k=1)
        tck_right, u_right = si.splprep(right.T, s=0, k=1)

        # evaluate function at any parameter "0<=t<=1"
        def eta_left(t):
            return np.array(si.splev(t, tck_left, der=0))

        def eta_right(t):
            return np.array(si.splev(t, tck_right, der=0))

        def xi_lower(t):
            return np.array(si.splev(t, tck_lower, der=0))

        def xi_upper(t):
            return np.array(si.splev(t, tck_upper, der=0))

        nodes = np.zeros((len(u_left) * len(u_lower), 2))

        # corner points
        c1 = xi_lower(0.0)
        c2 = xi_upper(0.0)
        c3 = xi_lower(1.0)
        c4 = xi_upper(1.0)

        for i, xi in enumerate(u_lower):
            xi_u = u_upper[i]
            for j, eta in enumerate(u_left):
                eta_r = u_right[j]

                node = i * len(u_left) + j

                # formula for the transinite interpolation
                point = (1.0 - xi) * eta_left(eta) + xi * eta_right(eta_r) + \
                    (1.0 - eta) * xi_lower(xi) + eta * xi_upper(xi_u) - \
                    ((1.0 - xi) * (1.0 - eta) * c1 + (1.0 - xi) * eta * c2 +
                     xi * (1.0 - eta) * c3 + xi * eta * c4)

                nodes[node, 0] = point[0]
                nodes[node, 1] = point[1]

        vlines = list()
        vline = list()
        i = 0
        for node in nodes:
            i += 1
            vline.append(node)
            if i % len(left) == 0:
                vlines.append(vline)
                vline = list()

        vlines.reverse()

        if ij:
            ulines = self.makeUfromV(vlines)
            n = -1
            for k in range(ij[2], ij[3]+1):
                n += 1
                self.ULines[k][ij[0]:ij[1]+1] = ulines[n]
        else:
            self.ULines = self.makeUfromV(vlines)

        return

    @staticmethod
    def makeUfromV(vlines):
        ulines = list()
        uline = list()
        for i in range(len(vlines[0])):
            for vline in vlines:
                x, y = vline[i][0], vline[i][1]
                uline.append((x, y))
            ulines.append(uline[::-1])
            uline = list()
        return ulines

    def getRotationAngle(self, node, n, degree=True):

        before = n - 1
        if before == 0:
            before = 8
        after = n + 1
        if after == 9:
            after = 1

        b = np.array([graph.node[neighbours[before]]['pos'][0],
                      graph.node[neighbours[before]]['pos'][1]])
        a = np.array([graph.node[neighbours[after]]['pos'][0],
                      graph.node[neighbours[after]]['pos'][1]])
        c = np.array([graph.node[node]['pos'][0], graph.node[node]['pos'][1]])
        s = np.array([graph.node[neighbours[n]]['pos'][0],
                      graph.node[neighbours[n]]['pos'][1]])
        u = b - s
        v = a - s
        w = c - s
        alpha2 = Utils.angle_between(u, w, degree=degree) * (-1.0) * \
            np.sign(np.cross(u, w))
        alpha1 = Utils.angle_between(w, v, degree=degree) * (-1.0) * \
            np.sign(np.cross(w, v))
        beta = (alpha2 - alpha1) / 2.0

        return beta

    def writeFLMA(self, name='', depth=0.1):

        folder = OUTPUTDATA + '/'
        nameroot, extension = os.path.splitext(str(name))
        filename = nameroot + '_' + self.name + '.flma'
        fullname = folder + filename

        logger.log.info('FIRE mesh <b><font color=%s> %s</b> saved to output folder'
                        % ('#005511', filename))

        U, V = self.getDivUV()
        points = (U + 1) * (V + 1)

        with open(fullname, 'w') as f:

            numvertex = '8'

            # write number of points to FLMA file (*2 for z-direction)
            f.write(str(2 * points) + '\n')

            signum = -1.

            # write x-, y- and z-coordinates to FLMA file
            # loop 1D direction (symmetry)
            for j in range(2):
                for uline in self.getULines():
                    for i in range(len(uline)):
                        f.write(str(uline[i][0]) + ' ' + str(uline[i][1]) +
                                ' ' + str(signum * depth / 2.0) + ' ')
                signum = 1.

            # write number of cells to FLMA file
            cells = U * V
            f.write('\n' + str(cells) + '\n')

            # write cell connectivity to FLMA file
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

                    connectivity = str(p1) + ' ' + str(p2) + ' ' + str(p3) + \
                        ' ' + str(p4) + ' ' + str(p5) + ' ' + str(p6) + \
                        ' ' + str(p7) + ' ' + str(p8) + '\n'

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

    def writeSU2(self, name=''):

        folder = OUTPUTDATA + '/'
        nameroot, extension = os.path.splitext(str(name))
        filename = nameroot + '_' + self.name + '.su2'
        fullname = folder + filename

        U, V = self.getDivUV()
        up = U + 1
        vp = V + 1

        # element type is SU2 quadrilateral
        el_type = '9'

        with open(fullname, 'w') as f:
            f.write('%\n')
            f.write('% Airfoil contour: ' + nameroot + ' \n')
            f.write('%\n')
            f.write('% File created with ' + PyAero.__appname__ + '.\n')
            f.write('% Version: ' + PyAero.__version__ + '\n')
            f.write('% Author: ' + PyAero.__author__ + '\n')
            f.write('%\n')
            # dimension of the problem
            f.write('% Problem dimension\n')
            f.write('%\n')
            # number of interior elements
            f.write('NDIME= 2\n')
            f.write('%\n')
            # element connectivity
            f.write('% Inner element connectivity\n')
            f.write('%\n')
            # number of elements
            f.write('NELEM= %s\n' % (U*V))
            k = -1
            for i in range(U):
                for j in range(V):
                    # vertex number
                    k += 1

                    p1 = j * up + i
                    p2 = p1 + 1
                    p4 = p1 + up
                    p3 = p4 + 1

                    connectivity = el_type + ' ' + str(p1) + ' ' + str(p2) + \
                        ' ' + str(p3) + ' ' + str(p4) + str(k) + '\n'

                    f.write(connectivity)

            # number of vertices
            f.write('NPOIN=%s\n' % (up*vp))

            # x- and y-coordinates
            node = -1
            for uline in self.getULines():
                for i in range(len(uline))[::-1]:
                    node += 1
                    x, y = uline[i][0], uline[i][1]
                    f.write(' {:24.16e} {:24.16e} {:} \n'.format(x, y, node))

        logger.log.info('SU2 mesh <b><font color=%s> %s</b> saved to output folder'
                        % ('#CC5511', filename))

    def writeGMESH(self, name=''):

        folder = OUTPUTDATA + '/'
        nameroot, extension = os.path.splitext(str(name))
        filename = nameroot + '_' + self.name + '.msh'
        fullname = folder + filename

        U, V = self.getDivUV()
        up = U + 1
        vp = V + 1

        # element type is GMESH quadrilateral
        el_type = '3'

        with open(fullname, 'w') as f:

            f.write('$Information\n')
            f.write(' Airfoil contour: ' + nameroot + ' \n')
            f.write('\n')
            f.write(' File created with ' + PyAero.__appname__ + '.\n')
            f.write(' Version: ' + PyAero.__version__ + '\n')
            f.write(' Author: ' + PyAero.__author__ + '\n')
            f.write('\n')
            f.write('$EndInformation')

            f.write(2*'\n')

            f.write('$MeshFormat\n')
            f.write('2.2 0 8\n')
            f.write('$EndMeshFormat\n\n')

            f.write('$Nodes\n')
            f.write('%s\n' % (up*vp))
            # x- and y-coordinates
            node = 0
            for uline in self.getULines():
                for i in range(len(uline))[::-1]:
                    node += 1
                    x, y = uline[i][0], uline[i][1]
                    f.write(' {:} {:16.8} {:16.8} 0.0\n'.format(node, x, y))
            f.write('$EndNodes')
            f.write('\n\n')
            f.write('$Elements\n')
            f.write('%s\n' % (U*V))
            k = 0
            for i in range(U):
                for j in range(V):
                    # vertex number
                    k += 1

                    p1 = j * up + i
                    p2 = p1 + 1
                    p4 = p1 + up
                    p3 = p4 + 1

                    connectivity = ' ' + str(k) + ' ' + el_type + ' ' + \
                        str(p1) + ' ' + str(p2) + ' ' + str(p3) + ' ' + \
                        str(p4) + '\n'

                    f.write(connectivity)
            f.write('$EndElements\n')

        logger.log.info('GMESH mesh <b><font color=%s> %s</b> saved to output folder'
                        % ('#224CCC', filename))


class Smooth(object):

    def __init__(self, block):
        self.block = block

    def getNeighbours(self, node):
        """Get a list of neighbours around a node """

        i, j = node[0], node[1]
        neighbours = {1: (i - 1, j - 1), 2: (i, j - 1), 3: (i + 1, j - 1),
                      4: (i + 1, j), 5: (i + 1, j + 1), 6: (i, j + 1),
                      7: (i - 1, j + 1), 8: (i - 1, j)}
        return neighbours

    def smooth(self, nodes, iterations=1, algorithm='laplace'):
        """Smoothing of a square lattice mesh

        Algorithms:
           - Angle based
             Tian Zhou:
             AN ANGLE-BASED APPROACH TO TWO-DIMENSIONAL MESH SMOOTHING
           - Laplace
             Mean of surrounding node coordinates
           - Parallelogram smoothing
             Sanjay Kumar Khattri:
             A NEW SMOOTHING ALGORITHM FOR QUADRILATERAL AND HEXAHEDRAL MESHES

        Args:
            nodes (TYPE): List of (i, j) tuples for the nodes to be smoothed
            iterations (int, optional): Number of smoothing iterations
            algorithm (str, optional): Smoothing algorithm
        """

        # loop number of smoothing iterations
        for i in range(iterations):

            new_pos = list()

            # smooth a node (i, j)
            for node in nodes:
                nb = self.getNeighbours(node)

                if algorithm == 'laplace':
                    new_pos = (self.block.getNodeCoo(nb[2]) +
                               self.block.getNodeCoo(nb[4]) +
                               self.block.getNodeCoo(nb[6]) +
                               self.block.getNodeCoo(nb[8])) / 4.0

                if algorithm == 'parallelogram':

                    new_pos = (self.block.getNodeCoo(nb[1]) +
                               self.block.getNodeCoo(nb[3]) +
                               self.block.getNodeCoo(nb[5]) +
                               self.block.getNodeCoo(nb[7])) / 4.0 - \
                              (self.block.getNodeCoo(nb[2]) +
                               self.block.getNodeCoo(nb[4]) +
                               self.block.getNodeCoo(nb[6]) +
                               self.block.getNodeCoo(nb[8])) / 2.0

                if algorithm == 'angle_based':
                    pass

                self.block.setNodeCoo(node, new_pos.tolist())

        return self.block

    def selectNodes(self, domain='interior', ij=[]):
        """Generate a node index list

        Args:
            domain (str, optional): Defines the part of the domain where
                                    nodes shall be selected

        Returns:
            List: Indices as (i, j) tuples
        """
        U, V = self.block.getDivUV()
        nodes = list()

        # select all nodes except boundary nodes
        if domain == 'interior':
            istart = 1
            iend = U
            jstart = 1
            jend = V

        if domain == 'ij':
            istart = ij[0]
            iend = ij[1]
            jstart = ij[2]
            jend = ij[3]

        for i in range(istart, iend):
            for j in range(jstart, jend):
                nodes.append((i, j))

        return nodes
