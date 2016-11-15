import copy

from matplotlib.backends.backend_qt4agg \
    import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg \
    import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import scipy.interpolate as si

from PyQt4 import QtGui, QtCore
from PUtils import Utils as utils

import PLogger as logger


class ContourAnalysis(QtGui.QFrame):
    """Summary

    Attributes:
        canvas (TYPE): Description
        curvature_data (TYPE): Description
        figure (TYPE): Description
        parent (QMainWindow object): MainWindow instance
        raw_coordinates (list): contour points as tuples
        spline_data (TYPE): Description
        toolbar (TYPE): Description
    """
    def __init__(self, parent):
        super(ContourAnalysis, self).__init__(parent)

        self.parent = parent
        self.spline_data = None
        self.curvature_data = None

        # a figure instance to plot on
        self.figure_top = plt.figure(figsize=(25, 35), tight_layout=True)
        self.figure_center = plt.figure(figsize=(25, 35), tight_layout=True)
        self.figure_bottom = plt.figure(figsize=(25, 35), tight_layout=True)

        # background of figures
        r, g, b = 170./255., 170./255., 170./255.
        self.figure_top.patch.set_facecolor(color=(r, g, b))
        self.figure_center.patch.set_facecolor(color=(r, g, b))
        self.figure_bottom.patch.set_facecolor(color=(r, g, b))

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas_top = FigureCanvas(self.figure_top)
        self.canvas_center = FigureCanvas(self.figure_center)
        self.canvas_bottom = FigureCanvas(self.figure_bottom)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar_top = NavigationToolbar(self.canvas_top, self)
        self.toolbar_center = NavigationToolbar(self.canvas_center, self)
        self.toolbar_bottom = NavigationToolbar(self.canvas_bottom, self,
                                                coordinates=True)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.canvas_top)
        vbox1.addWidget(self.toolbar_top)
        widget1 = QtGui.QWidget()
        widget1.setLayout(vbox1)
        vbox2 = QtGui.QVBoxLayout()
        vbox2.addWidget(self.canvas_center)
        vbox2.addWidget(self.toolbar_center)
        widget2 = QtGui.QWidget()
        widget2.setLayout(vbox2)
        vbox3 = QtGui.QVBoxLayout()
        vbox3.addWidget(self.canvas_bottom)
        vbox3.addWidget(self.toolbar_bottom)
        widget3 = QtGui.QWidget()
        widget3.setLayout(vbox3)

        splitter = QtGui.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(widget1)
        splitter.addWidget(widget2)
        splitter.addWidget(widget3)

        # set the layout
        layout = QtGui.QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

    def reset(self):
        self.spline_data = None
        self.curvature_data = None

        # clears the current figure
        # necessary so that changing between gradient, radius, etc. works
        plt.clf()

    def spline(self, x, y, points=200, degree=2, evaluate=False):
        """Interpolate spline through given points

        Args:
            spline (int, optional): Number of points on the spline
            degree (int, optional): Degree of the spline
            evaluate (bool, optional): If True, evaluate spline just at
                                       the coordinates of the knots
        """

        # interpolate B-spline through data points
        # returns knots of control polygon
        # tck ... tuple (t,c,k) containing the vector of knots,
        # the B-spline coefficients, and the degree of the spline.
        # u ... array of the parameters for each knot
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

        return self.spline_data

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

        # self.spline_data = [coo, u, t, der1, der2, tck]
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

            # angle between two contour line segments
            a = np.array([xx[i], yy[i]])
            b = np.array([xx[i + 1], yy[i + 1]])
            c = np.array([xx[i + 2], yy[i + 2]])
            angle = utils.angle_between(a - b, c - b, degree=True)

            if angle < tol:

                refined[i] = True
                refinements += 1

                # parameters for new points
                t1 = (t[i] + t[i + 1]) / 2.
                t2 = (t[i + 1] + t[i + 2]) / 2.

                # coordinates of new points
                p1 = si.splev(t1, tck, der=0)
                p2 = si.splev(t2, tck, der=0)

                # insert points and their parameters into arrays
                if i > 0 and not refined[i - 1]:
                    xn = np.insert(xn, i + 1 + j, p1[0])
                    yn = np.insert(yn, i + 1 + j, p1[1])
                    tn = np.insert(tn, i + 1 + j, t1)
                    j += 1
                xn = np.insert(xn, i + 2 + j, p2[0])
                yn = np.insert(yn, i + 2 + j, p2[1])
                tn = np.insert(tn, i + 2 + j, t2)
                j += 1

                if first and recursions > 0:
                    if verbose:
                        logger.log.info('Recursion level: %s \n' %
                                        (recursions))
                    first = False

                if verbose:
                    logger.log.info('Refining between %s %s, Tol=%05.1f Angle=%05.1f\n'
                                    % (i, i + 1, tol, angle))

        if verbose:
            logger.log.info('Points after refining: %s' % (len(xn)))

        # update coordinate array, including inserted points
        self.spline_data[0] = (xn, yn)
        # update parameter array, including parameters of inserted points
        self.spline_data[2] = tn

        # this is the recursion :)
        if refinements > 0:
            self.refine(tol, recursions + 1, verbose)

        # stopping from recursion if no refinements done in this recursion
        else:

            # update derivatives, including inserted points
            self.spline_data[3] = si.splev(tn, tck, der=1)
            self.spline_data[4] = si.splev(tn, tck, der=2)

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

        xd = der1[0]
        yd = der1[1]
        x2d = der2[0]
        y2d = der2[1]
        n = xd**2 + yd**2
        d = xd*y2d - yd*x2d

        # gradient dy/dx = dy/du / dx/du
        gradient = der1[1] / der1[0]

        # radius of curvature
        R = n**(3./2.) / abs(d)

        # curvature
        C = d / n**(3./2.)

        # coordinates of curvature-circle center points
        xc = coo[0] - R * yd / np.sqrt(n)
        yc = coo[1] + R * xd / np.sqrt(n)

        self.curvature_data = [gradient, C, R, xc, yc]
        return  

    def analyze(self, tolerance, spline_points, plot, reset=True):

        if reset:
            # logger.stack(logger.log)
            self.reset()

        # interpolate a spline through the raw contour points

        # FIXME
        # FIXME get airfoil coordinates here from scene item
        # FIXME either selected airfoil or only loaded airfoil if any
        # FIXME

        x, y = self.parent.airfoil.raw_coordinates
        self.spline(x, y, points=spline_points, degree=2)

        # refine the contour in order to meet the tolerance
        self.refine(tol=tolerance, verbose=False)

        # redo spline on refined contour
        # spline only evaluated at refined contour points (evaluate=True)
        coo, u, t, der1, der2, tck = self.spline_data
        x, y = coo
        self.spline(x, y, points=spline_points, degree=2, evaluate=True)

        # get specific curve properties
        self.getCurvature()

        # add new attributes to airfoil instance
        self.parent.airfoil.spline_data = self.spline_data
        self.parent.airfoil.curvature_data = self.curvature_data

        self.drawContour(plot)

    def getLeRadius(self):
        """Identify leading edge radius, i.e. smallest radius of
        parametric curve

        Returns:
            FLOAT: leading edge radius and its center
        """
        radius = self.curvature_data[2]
        rc = np.min(radius)
        le_id = np.where(radius == rc)
        # leading edge curvature circle center
        xc = self.curvature_data[3][le_id]
        yc = self.curvature_data[4][le_id]

        return rc, xc, yc

    def drawContour(self, plot):

        # curvature_data --> gradient, C, R, xc, yc

        x, y = self.parent.airfoil.raw_coordinates
        xr, yr = self.spline_data[0]
        gradient = self.curvature_data[0]
        curvature = self.curvature_data[1]
        radius = self.curvature_data[2]

        # leading edge radius
        rc, xc, yc = self.getLeRadius()

        # create axes
        ax1 = self.figure_top.add_subplot(111, frame_on=False)
        ax2 = self.figure_center.add_subplot(111, frame_on=False)
        ax3 = self.figure_bottom.add_subplot(111, frame_on=False)

        # plot original contour
        r, g, b = 30./255., 30./255., 30./255.
        ax1.plot(x, y, marker='o', mfc='r', color=(r, g, b), linewidth=2)
        ax1.set_title('Original Contour', fontsize=14)
        ax1.set_xlim(-0.05, 1.05)
        # ax1.set_ylim(-10.0, 14.0)
        r, g, b = 120./255., 120./255., 120./255.
        ax1.fill(x, y, color=(r, g, b))
        ax1.set_aspect('equal')

        # plot refined contour
        r, g, b = 30./255., 30./255., 30./255.
        ax2.plot(xr, yr, marker='o', mfc='r', color=(r, g, b), linewidth=2)
        # leading edge curvature circle
        circle = patches.Circle((xc, yc), rc, edgecolor='y', facecolor='None',
                                lw=2, ls='solid', zorder=2)
        ax2.plot(xc, yc, marker='o', mfc='b', linewidth=2)
        ax2.add_patch(circle)
        ax2.set_title('Refined Contour', fontsize=14)
        ax2.set_xlim(-0.05, 1.05)
        # ax2.set_ylim(-10.0, 14.0)
        r, g, b = 90./255., 90./255., 90./255.
        ax2.fill(xr, yr, color=(r, g, b))
        ax2.set_aspect('equal')

        # select plotting variable for contour analysis
        plotvar = {1: [gradient, 'Gradient'], 2: [curvature, 'Curvature'],
                   3: [radius, 'Radius of Curvature']}

        ax3.cla()

        # plot either of three possible analysis results
        r, g, b = 30./255., 30./255., 30./255.
        ax3.plot(xr, plotvar[plot][0], marker='o', mfc='r', color=(r, g, b),
                 linewidth=2)
        ax3.set_title(plotvar[plot][1], fontsize=14)
        ax3.set_xlim(-0.05, 1.05)
        if plot == 1:
            ax3.set_ylim(-1.0, 1.0)
        r, g, b = 90./255., 90./255., 90./255.
        ax3.fill(xr, plotvar[plot][0], color=(r, g, b))

        # refresh canvas
        self.canvas_top.draw()
        self.canvas_center.draw()
        self.canvas_bottom.draw()
