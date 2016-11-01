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
from PUtils import Utils as utils

import PLogger as logger


class ContourAnalysis(QtGui.QFrame):

    def __init__(self, parent=None):
        super(ContourAnalysis, self).__init__(parent)

        self.parent = parent
        self.spline_data = None
        self.curvature_data = None

        # a figure instance to plot on
        self.figure = plt.figure(figsize=(25, 35))

        # background of figures
        r, g, b = 150./255., 150./255., 150./255.
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

        x, y = self.raw_coordinates

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

        self.spline_data = [coo, u, t, der1, der2, tck]

        return coo, u, t, der1, der2, tck

    def refine(self, tol=170.0, recursions=0, verbose=False):
        """Recursive refinement with respect to angle criterion (tol).
        If angle between two adjacent line segments is less than tol,
        a recursive refinement of the contour is performed until
        tol is met.

        Args:
            tol (float, optional): Angle between two adjacent contour segments
            recursions (int, optional): NO USER INPUT HERE
                                        Needed just for level information
                                        during recursions
            verbose (bool, optional): Activate logger messages
        """

        xx, yy = self.spline_data[0]
        t = self.spline_data[2]
        tck = self.spline_data[5]

        if verbose:
            logger.log.info('\nPoints before refining: %s \n' % (len(xx)))

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
            angle = utils.angle_between(a - b, c - b, degree=True)
            if angle < tol:
                refined[i] = True
                refinements += 1

                if first and recursions > 0:
                    if verbose:
                        logger.log.info('Recursion level: %s \n' %
                                        (recursions))
                    first = False

                if verbose:
                    logger.log.info('Refining between %s %s, Tol=%05.1f Angle=%05.1f\n'
                                    % (i, i + 1, tol, angle))

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
            logger.log.info('Points after refining: %s' % (len(xn)))

        # update coordinate array, including inserted points
        self.spline_data[0] = (xn, yn)
        # update parameter array, including parameters of inserted points
        self.spline_data[2] = tn
        # update derivatives, including parameters of inserted points
        self.spline_data[3] = si.splev(tn, tck, der=1)
        self.spline_data[4] = si.splev(tn, tck, der=2)

        # recursive refinement
        if refinements > 0:

            self.refine(tol, recursions + 1, verbose)

        # stopping from recursion if no refinements done in this recursion
        else:

            if verbose:
                logger.log.info('No more refinements.')
                logger.log.info('\nTotal number of recursions: %s'
                                % (recursions - 1))
            return

    def getCurvature(self):
        """Curvature and radius of curvature of a parametric curve

        der1 is dx/dt and dy/dt at each point
        der2 is d2x/dt2 and d2y/dt2 at each point

        Returns:
            float: Tuple of numpy arrays carrying gradient of the curve,
                   the curvature, radiusses of curvature circles and
                   curvature circle centers for each point of the curve
        """

        coo = self.spline_data[0]
        der1 = self.spline_data[3]
        der2 = self.spline_data[4]

        x2d = der2[0]
        y2d = der2[1]
        n = der1[0]**2 + der1[1]**2
        d = der1[0]*y2d - der1[1]*x2d

        # gradient dy/dx = dy/du / dx/du
        gradient = der1[1] / der1[0]

        # curvature
        curvature = d / n**(3./2.)

        # radius of curvature
        radius = n**(3./2.) / np.abs(d)

        # coordinates of curvature-circle center points
        xc = coo[0] - radius * der1[0] / np.sqrt(n)
        yc = coo[1] + radius * der1[1] / np.sqrt(n)

        self.curvature_data = [gradient, curvature, radius, xc, yc]
        return self.curvature_data

    def analyze(self, tolerance, spline_points):

        # raw coordinates are stored as numpy array
        # np.array( (x, y) )
        self.raw_coordinates = self.parent.airfoil.raw_coordinates

        # interpolate a spline through the raw contour points
        self.spline(points=spline_points, degree=2, evaluate=False)

        # refine the contour in order to meet the tolerance
        self.refine(tol=tolerance, verbose=False)

        # add new information to airfoil
        self.parent.airfoil.spline_data = self.spline_data
        self.parent.airfoil.curvature_data = self.curvature_data

        # get specific curve properties
        self.getCurvature()

        self.drawContour()

    def drawContour(self):

        x, y = self.raw_coordinates
        xr, yr = self.spline_data[0]
        gradient = self.curvature_data[0]
        radius = self.curvature_data[2]

        # create an axis
        ax1 = self.figure.add_subplot(311, frame_on=False)
        ax2 = self.figure.add_subplot(312, frame_on=False)
        ax3 = self.figure.add_subplot(313, frame_on=False)
        # ax4 = self.figure.add_subplot(414, frame_on=False)

        # plot data
        r, g, b = 30./255., 30./255., 30./255.
        ax1.plot(x, y, marker='o', color=(r, g, b), linewidth=2)
        ax1.set_title('Original Contour', fontsize=14)
        ax1.set_xlim(-0.05, 1.05)
        # ax1.set_ylim(-10.0, 14.0)
        r, g, b = 255./255., 100./255., 100./255.
        ax1.fill(x, y, color=(r, g, b))
        ax1.set_aspect('equal')

        r, g, b = 30./255., 30./255., 30./255.
        ax2.plot(xr, yr, marker='o', color=(r, g, b), linewidth=2)
        ax2.set_title('Refined Contour', fontsize=14)
        ax2.set_xlim(-0.05, 1.05)
        # ax2.set_ylim(-10.0, 14.0)
        r, g, b = 100./255., 255./255., 100./255.
        ax2.fill(xr, yr, color=(r, g, b))
        ax2.set_aspect('equal')

        r, g, b = 30./255., 30./255., 30./255.
        ax3.plot(xr, radius, color=(r, g, b), linewidth=2)
        ax3.set_title('Radius of Curvature', fontsize=14)
        ax3.set_xlim(-0.05, 1.05)
        ax3.set_ylim(-2.0, 40.0)
        r, g, b = 180./255., 255./255., 180./255.
        ax3.fill(xr, radius, color=(r, g, b))
        # ax3.set_aspect('equal')

        # r, g, b = 39./255., 40./255., 34./255.
        # ax4.plot(xr, gradient, color=(r, g, b), linewidth=3)
        # ax4.set_title('Gradient of Contour', fontsize=14)
        # ax4.set_xlim(-0.05, 1.05)
        # # ax4.set_ylim(-10.0, 14.0)
        # r, g, b = 249./255., 38./255., 114./255.
        # ax4.fill(xr, gradient, color=(r, g, b))
        # ax4.set_aspect('equal')

        plt.tight_layout()

        # refresh canvas
        self.canvas.draw()
