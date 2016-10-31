# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

import PGraphicsItemsCollection as gc
import PGraphicsItem
import PLogger as logger
from PSettings import LOGCOLOR


class Airfoil(object):
    """Class to read airfoil data from file (or use predefined airfoil)

    The Airfoil object carries several graphics items:
        e.g. raw data, chord, camber, etc.

    Attributes:
        brushcolor (QColor): fill color for airfoil
        chord (QGraphicsItem): Description
        contour_group (TYPE): Description
        item (QGraphicsItem): graphics item derived from QPolygonF object
        markers (QGraphicsItem): color for airoil outline points
        name (str): airfoil name
        parent (QMainWindow): MainWindow instance
        pencolor (QColor): color for airoil outline
        penwidth (float): thickness of airfoil outline
        raw_contour (list of QPointF): list of contour points
    """

    def __init__(self, scene):

        self.scene = scene
        self.name = None
        self.item = None
        self.raw_contour = QtGui.QPolygonF()
        self.pencolor = QtGui.QColor(0, 0, 0, 255)
        self.penwidth = 2.5
        self.brushcolor = QtGui.QColor(150, 150, 150, 255)
        self.home = None

    def readContour(self, filename, comment='#'):

        self.name = filename

        try:
            with open(filename, mode='r') as f:
                lines = f.readlines()
        except IOError as e:
            logger.log.info('%s: Unable to open file %s.' % (e, filename))
            return

        data = [line for line in lines if comment not in line]
        x = [float(l.split()[0]) for l in data]
        y = [float(l.split()[1]) for l in data]
        points = [(px, py) for px, py in zip(x, y)]

        # store contour points as type QPointF
        for pt in points:
            x = pt[0]
            y = pt[1]
            self.raw_contour.append(QtCore.QPointF(x, y))

        # add airfoil points as GraphicsItem to the scene
        self.addContour()
        # create a group of items that carries contour, markers, etc.
        self.createItemsGroup()
        # add the markers to the group
        self.addMarkers(type='circle')
        # add the chord to the group
        self.addChord()

        fileinfo = QtCore.QFileInfo(self.name)
        name = fileinfo.fileName()
        logger.log.info('Airfoil <b><font color=%s>' % (LOGCOLOR) + name +
                        '</b> loaded')

    def addContour(self):
        """Add airfoil points as GraphicsItem to the scene"""

        # instantiate a graphics item
        contour = gc.GraphicsCollection()
        # make it polygon type and populate its points
        contour.Polygon(self.raw_contour)
        # set its properties
        contour.pen.setColor(self.pencolor)
        contour.pen.setWidth(self.penwidth)
        contour.pen.setCosmetic(True)  # no pen thickness change when zoomed
        contour.brush.setColor(self.brushcolor)

        # add contour as a GraphicsItem to the scene
        # these are the objects which are drawn in the GraphicsView
        self.item = PGraphicsItem.GraphicsItem(contour, self.scene)
        self.scene.addItem(self.item)

        # store home position of contour
        self.home = self.item.pos()

    def createItemsGroup(self):
        """Container that treats a group of items as a single item
        One item is the contour itself
        Other items are chord, camber, point markers, etc.
        """
        self.contour_group = QtGui.QGraphicsItemGroup(parent=self.item,
                                                      scene=self.scene)

        # This stops the QGraphicsItemGroup trying to handle the event,
        # and lets the child QGraphicsItems handle them
        # self.contour_group.setHandlesChildEvents(false)

    def addMarkers(self, type='circle'):
        """Create marker for polygon contour"""
        # FIXME
        # FIXME make more marker types in PGraphicsCollection
        # FIXME and fix also scaling behaviour of markers
        # FIXME
        # FIXME the pen width influences the bounding rect of
        # FIXME so that zoom home (i.e. fitallinView is affected)
        # FIXME
        # FIXME markers should be replaced by images/icons
        # FIXME
        for point in self.raw_contour:
            x = QtCore.QPointF(point).x()
            y = QtCore.QPointF(point).y()

            # put airfoil contour points as graphicsitem
            points = gc.GraphicsCollection()
            # be careful with the penwidth as it affects bounding rect
            points.pen.setWidth(0.0001)
            points.pen.setColor(QtGui.QColor(90, 90, 90, 255))
            points.brush.setColor(QtGui.QColor(255, 0, 0, 255))
            points.pen.setCosmetic(True)  # no pen thickness change when zoomed

            if type == 'circle':
                points.Circle(x, y, 0.003)

            self.markers = PGraphicsItem.GraphicsItem(points,
                                                      self.scene)
            # self.markers.setFlag(QtGui.QGraphicsItem.
            #                      ItemIgnoresTransformations, True)
            self.contour_group.addToGroup(self.markers)

    def addChord(self):
        line = gc.GraphicsCollection()
        color = QtGui.QColor(70, 70, 70, 255)
        line.pen.setColor(color)
        line.pen.setWidth(1.)
        line.pen.setCosmetic(True)  # no pen thickness change when zoomed
        line.pen.setJoinStyle(QtCore.Qt.RoundJoin)
        line.pen.setStyle(QtCore.Qt.CustomDashLine)
        # pattern is 1px dash, 4px space, 7px dash, 4px
        line.pen.setDashPattern([1, 4, 10, 4])
        line.Line(0.0, 0.0, 1.0, 0.0)

        self.chord = PGraphicsItem.GraphicsItem(line, self.scene)
        self.contour_group.addToGroup(self.chord)

    def camber(self):
        pass

    def setPenColor(self, r, g, b, a):
        self.pencolor = QtGui.QColor(r, g, b, a)

    def setBrushColor(self, r, g, b, a):
        self.brushcolor = QtGui.QColor(r, g, b, a)
