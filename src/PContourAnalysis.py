import copy

from matplotlib.backends.backend_qt4agg \
    import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg \
    import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import scipy.interpolate as si

from PyQt4 import QtGui
import PUtils as Utils

import PLogger as logger


class Contour(QtGui.QFrame):

    def __init__(self, parent=None):
        super(Contour, self).__init__(parent)

        self.parent = parent
        self.raw_coordinates = self.parent.airfoil.raw_coordinates
        self.coordinates = None
        self.spline = None

        # a figure instance to plot on
        self.figure = plt.figure(figsize=(20, 30))
        r, g, b = 100./255., 100./255., 100./255.
        self.figure.patch.set_facecolor(color=(r, g, b))

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def spline(self, points=200, degree=2, evaluate=False):
        """Interpolate spline through given points

        Args:
            spline (int, optional): Number of points on the spline
            degree (int, optional): Degree of the spline
            evaluate (bool, optional): If True, evaluate spline just at
                                       the coordinates of the knots
        """

        x = self.raw_coordinates[0]
        y = self.raw_coordinates[1]

        # interpolate B-spline through data points
        # returns knots of control polygon
        # tck ... tuple (t,c,k) containing the vector of knots,
        # the B-spline coefficients, and the degree of the spline.
        # u ... array of the parameters
        tck, u = si.splprep([x, y], s=0, k=degree)

        # number of points on interpolated B-spline (parameter t)
        t = np.linspace(0.0, 1.0, points)

        # if True, evaluate spline just at the coordinates of the knots
        if evaluate:
            t = u

        # evaluate B-spline at given parameters
        # der=0: returns point coordinates
        coo = si.splev(t, tck, der=0)

        # evaluate 1st derivative at given parameters
        der1 = si.splev(t, tck, der=1)

        # evaluate 2nd derivative at given parameters
        der2 = si.splev(t, tck, der=2)

        self.spline = [coo, u, t, der1, der2, tck]
        self.coordinates = coo

        return coo, u, t, der1, der2, tck

    def refine(self, tol=170.0, recursions=0, verbose=False):
        """Recursive refinement with respect to angle criterion (tol).
        If angle between two adjacent line segments is less than tol,
        a recursive refinement of the contour is performed until
        tol is met.

        Args:
            xo (TYPE): Description
            yo (TYPE): Description
            tol (float, optional): Description
            spline_pts (int, optional): Description
        """

        xx = self.spline[0][0]
        yy = self.spline[0][1]
        t = self.spline[2]
        tck = self.spline[5]

        if verbose:
            print '\nPoints before refining: %s' % (len(xx))

        xn = copy.deepcopy(xx)
        yn = copy.deepcopy(yy)
        tn = copy.deepcopy(t)

        j = 0
        refinements = 0
        first = True
        refined = dict()

        for i in range(len(xx) - 2):
            refined[i] = False

            a = np.array([xx[i], yy[i]])
            b = np.array([xx[i + 1], yy[i + 1]])
            c = np.array([xx[i + 2], yy[i + 2]])
            t1 = (t[i] + t[i + 1]) / 2.
            t2 = (t[i + 1] + t[i + 2]) / 2.
            p1 = si.splev(t1, tck, der=0)
            p2 = si.splev(t2, tck, der=0)
            angle = Utils.angle_between(a - b, c - b, degree=True)
            if angle < tol:
                refined[i] = True
                refinements += 1

                if first and recursions > 0:
                    if verbose:
                        print 'Recursion level: ', recursions
                    first = False

                if verbose:
                    print 'Refining between points', i, i + 1, t1, t2, \
                        tol, angle

                # add points to polygon
                if i > 0 and not refined[i - 1]:
                    xn = np.insert(xn, i + 1 + j, p1[0])
                    yn = np.insert(yn, i + 1 + j, p1[1])
                    tn = np.insert(tn, i + 1 + j, t1)
                    j += 1
                xn = np.insert(xn, i + 2 + j, p2[0])
                yn = np.insert(yn, i + 2 + j, p2[1])
                tn = np.insert(tn, i + 2 + j, t2)
                j += 1

        if verbose:
            print 'Points after refining: %s' % (len(xn))

        self.spline[0] = (xn, yn)
        self.spline[2] = tn
        self.coordinates = (xn, yn)

        # recursive refinement
        if refinements > 0:

            self.refine(tol, recursions + 1, verbose)

        # stopping from recursion if no refinements done in this recursion
        else:

            if verbose:
                print 'No more refinements.'
                print '\nTotal number of recursions: ', recursions - 1
            return

    def analyze(self, tolerance, spline_points):

        self.spline(points=spline_points, degree=2, evaluate=False)
        self.refine(tol=tolerance, verbose=False)

    def drawContour(self):

        # create an axis
        ax1 = self.figure.add_subplot(211, frame_on=False)
        ax2 = self.figure.add_subplot(212, frame_on=False)
        # ax3 = self.figure.add_subplot(413, frame_on=False)
        # ax4 = self.figure.add_subplot(414, frame_on=False)

        # plot data
        r, g, b = 39./255., 40./255., 34./255.
        ax1.plot(x, y, ls='o', color=(r, g, b), linewidth=3)
        ax1.plot(coo[0], coo[1], 'go', zorder=20)  # leading edge
        ax1.plot(xg, yg, 'mo', zorder=30)  # leading edge
        ax1.plot(xr, yr, 'yo', zorder=30)  # curvature circle center
        ax1.add_patch(circle)
        ax1.set_title('Contour', fontsize=14)
        ax1.set_xlim(-10.0, 110.0)
        # ax1.set_ylim(-10.0, 14.0)
        r, g, b = 249./255., 38./255., 114./255.
        ax1.fill(x, y, color=(r, g, b))
        ax1.set_aspect('equal')

        ax2.plot(coo[0], gradient, 'go-', linewidth=3)
        ax2.set_title('Gradient', fontsize=14)
        ax2.set_xlim(-10.0, 110.0)

        # refresh canvas
        self.canvas.draw()
