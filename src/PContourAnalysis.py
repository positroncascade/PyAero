import copy

from PyQt4 import QtGui

from matplotlib.backends.backend_qt4agg \
    import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg \
    import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import scipy.interpolate as si
import scipy.linalg as la

import PLogger as logger


class Contour(QtGui.QFrame):

    def __init__(self, parent=None):
        super(Contour, self).__init__(parent)

        self.parent = parent

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

    def refine(self, xo, yo, tol=170.0, spline_pts=300):
        """Recursive contour refinement with respect to angle
        criterion (tol). I.e., if the angle between two adjacent polygon
        elements is smaller than tol insert a new point in each of the two
        polygon segments.

        The inserted points are placed on a spline interpolated through the
        initial contour. Due to the recursive nature of the algorithm, it runs
        until tol is met for every adjacent polygon segment pair.

        Args:
            xo (float): List of x-ccordinates for the spline
            yo (float): List of y-ccordinates for the spline
            tol (float, optional): Angle criterion that triggers refinement
            spline_pts (int, optional): Number of points useed by the spline

        Return:
            x, y (float): Refined contour coordinates
        """

        x = copy.deepcopy(xo)
        y = copy.deepcopy(yo)

        # do recursive refinement therby using the splined contour
        coo, u, t, tck, gradient, radius, xc, yc, curvature = \
            self.spline(xo, yo, spline_pts)

        for i in range(len(x)-2):
            a = np.array([x[i]-x[i+1], y[i]-y[i+1]])
            b = np.array([x[i+2]-x[i+1], y[i+2]-y[i+1]])
            ang = self.angle_degree(a, b)
            if ang < tol:
                p1 = si.splev((u[i+1]+u[i])/2, tck, der=0)
                p2 = si.splev((u[i+2]+u[i+1])/2, tck, der=0)
                x.insert(i+1, p1[0])
                y.insert(i+1, p1[1])
                x.insert(i+3, p2[0])
                y.insert(i+3, p2[1])
                return self.refine(x, y, tol)
        return x, y

    def spline(self, x, y, num=300, ev=False):
        """Interpolate spline through given points

        Args:
            x (float): List of x-coordinates of points to be interpolated
            y (float): List of y-coordinates of points to be interpolated
            num (int, optional): Number of points on newly created spline
            ev (bool, optional): If "True", spline is evaluated only at given
                    points x, y. When set to "False" (default), "num" points
                    are evaluated.

        Return:
            coo (float): 2D NumPy array carrying x, y coordinates
            u (float): array of the spline parameters for the points
                    given in x, y
            t (float): array of the spline parameters for all new points;
                    t has length "num"
            tck (float): tuple (t,c,k) containing the vector of knots
            gradient (float): array carrying the gradient to the spline in
                    each spline point (coo)
            radius (float): array carrying the radius of curvature in each
                    spline point (coo)
            xc, yc (float): array carrying center points of circle of curvature
            curvature (float): array carrying the curvature in each point (coo)
        """

        # interpolate B-spline through data points
        # returns knots of control polygon
        # tck ... tuple (t,c,k) containing the vector of knots,
        # the B-spline coefficients, and the degree of the spline
        # u ... array of the parameters, each referring to one point x, y
        tck, u = si.splprep([x, y], s=0, k=3)

        # number of points on interpolated B-spline (parameter t)
        t = np.linspace(0.0, 1.0, num)
        # in this case spline is only evaluated at the points (x, y)
        # instead of "num" points otherwise
        if ev:
            t = u

        # evaluate B-spline at given parameters
        # der=0: returns point coordinates
        coo = si.splev(t, tck, der=0)

        # evaluate 1st derivative at given parameters
        # der=1 ==> (dx/dt, dy/dt)
        der1 = si.splev(t, tck, der=1)
        dxdt, dydt = der1[0], der1[1]

        # evaluate 2nd derivative at given parameters
        # der=2 ==> (d2x/dt2, d2y/dt2)
        der2 = si.splev(t, tck, der=2)
        d2xdt2, d2ydt2 = der2[0], der2[1]

        # gradient: dy/dx = dy/dt / dx/dt
        gradient = dydt / dxdt

        # radius of curvature for a parametric curve
        numerator = dxdt**2 + dydt**2
        denominator = dxdt*d2ydt2-dydt*d2xdt2
        radius = numerator**(3./2.) / abs(denominator)

        # curvature
        curvature = denominator / numerator**(3./2.)

        # coordinates of curvature-circle center points
        xc = coo[0] - dydt * numerator / denominator
        yc = coo[1] - dxdt * numerator / denominator

        return coo, u, t, tck, gradient, radius, xc, yc, curvature

    def angle_degree(self, a, b):
        """Return angle between two vectors in degrees

        Args:
            a (float): NumPy array of 1st vector
            b (float): NumPy array of 2nd vector

        Return:
            ang (float): Angle between vectors a, b in degrees
        """
        dot = np.dot(a, b)
        na = la.norm(a)
        nb = la.norm(b)
        cosinus = dot / (na * nb)
        ang = np.arccos(cosinus) * 180.0 / np.pi

        return ang

    def analyze(self, tolerance, spline_points):
        """Plot airfoil, refinement of the contour and derivatives

        Args:
            tolerance (float): Angle criterion that triggers refinement
            spline_points (int): Number of points on newly created spline
        """

        x, y = self.parent.airfoil.getCoords()
        xo = copy.deepcopy(x)
        yo = copy.deepcopy(y)
        logger.log.info('Tolerance %s' % (tolerance))
        logger.log.info('Points %s' % (spline_points))

        # refine initial contour data with angle criterion
        xref, yref = self.refine(xo, yo, tolerance)

        # interpolate spline through refined contour polygon
        coo, u, t, tck, gradient, radius, xc, yc, curvature = \
            self.spline(xref, yref, spline_points, False)

        # nose radius
        mg1 = max(gradient)
        img1 = np.where(gradient == mg1)
        img = img1[0][0]+1
        xg = coo[0][img1]  # leading edge
        yg = coo[1][img1]
        xr = xc[img1]
        yr = yc[img1]
        r = radius[img1]
        circle = patches.Circle((xr, yr), r, edgecolor='y', facecolor='None',
                                linewidth=3, zorder=10, ls='solid')

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
        # ax2.set_ylim(-2., 2)

        # ax3.plot(coo[0], radius, 'mo-', linewidth=3)
        # ax3.set_title('Radius of curvature', fontsize=14)
        # ax3.set_xlim(-10.0, 110.0)
        # ax3.set_ylim(0.0, 100.)

        # ax4.plot(coo[0], curvature, 'ro-', linewidth=3)
        # ax4.set_title('Curvature', fontsize=14)
        # ax4.set_xlim(-10.0, 110.00)
        # ax4.set_ylim(0.0, 40.0)

        # refresh canvas
        self.canvas.draw()
