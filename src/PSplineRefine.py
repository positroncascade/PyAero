import copy

import numpy as np
import scipy.interpolate as si

from PyQt4 import QtGui, QtCore

from PUtils import Utils
import PLogger as logger


class SplineRefine(object):

    def __init__(self, id):
        self.id = id

        # get MainWindow instance here (overcomes handling parents)
        self.mainwindow = QtCore.QCoreApplication.instance().mainwindow

    def doSplineRefine(self, tolerance=172.0, points=150):

        # get raw coordinates
        x, y = self.mainwindow.airfoils[self.id].raw_coordinates
        logger.log.info('Coordinates %s' % (x[0]))

        # interpolate a spline through the raw contour points
        self.spline_data = self.spline(x, y, points=points, degree=2)

        # refine the contour in order to meet the tolerance
        spline_data = copy.deepcopy(self.spline_data)
        self.refine(spline_data, tolerance=tolerance, verbose=True)

        # redo spline on refined contour
        # spline only evaluated at refined contour points (evaluate=True)
        coo, u, t, der1, der2, tck = self.spline_data
        x, y = coo
        self.spline_data = self.spline(x, y, points=points, degree=2,
                                       evaluate=True)

        # add spline data to airfoil object
        self.mainwindow.airfoils[self.id].spline_data = self.spline_data

        # add splined and refined contour to the airfoil contour_group
        for airfoil in self.mainwindow.airfoils:
            if airfoil.contour_item.isSelected():
                # self.spline_data = [coo, u, t, der1, der2, tck]
                airfoil.addContourSpline(self.spline_data[0])

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

        spline_data = [coo, u, t, der1, der2, tck]

        return spline_data

    def refine(self, spline_data, tolerance=170.0, recursions=0,
               verbose=False):
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
        xx, yy = spline_data[0]
        t = spline_data[2]
        tck = spline_data[5]

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
            angle = Utils.angle_between(a - b, c - b, degree=True)

            if angle < tolerance:

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
                                    % (i, i + 1, tolerance, angle))

        if verbose:
            logger.log.info('Points after refining: %s' % (len(xn)))

        # update coordinate array, including inserted points
        spline_data[0] = (xn, yn)
        # update parameter array, including parameters of inserted points
        spline_data[2] = tn

        # this is the recursion :)
        if refinements > 0:
            self.refine(spline_data, tolerance, recursions + 1, verbose)

        # stopping from recursion if no refinements done in this recursion
        else:

            # update derivatives, including inserted points
            spline_data[3] = si.splev(tn, tck, der=1)
            spline_data[4] = si.splev(tn, tck, der=2)

            if verbose:
                logger.log.info('No more refinements.')
                logger.log.info('\nTotal number of recursions: %s'
                                % (recursions - 1))

            # due to recursive call to refine, here no object can be returned
            # instead use self to transfer data to the outer world :)
            self.spline_data = copy.deepcopy(spline_data)
            return

    def writeContour(self):

        xr = self.raw_coordinates[0]
        xc = self.coordinates[0]
        yc = self.coordinates[1]
        s = '# Spline with {0} points based on initial contour'.format(len(xc))
        s1 = '({0} points)\n'.format(len(xr))
        info = s + s1

        with open(self.name + '_spline_' + str(len(xc)) + '.dat', 'w') as f:
            f.write('#\n')
            f.write('# Airfoil: ' + self.name + '\n')
            f.write('# Created from ' + self.filename + '\n')
            f.write(info)
            f.write('#\n')
            for i in range(len(xc)):
                data = '{:10.8f} {:10.8f} \n'.format(xc[i], yc[i])
                f.write(data)
