# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore

import PGraphicsItemsCollection as gc
import PGraphicsItem
import PLogger as logger
from PSettings import CHORDLENGTH


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

    def __init__(self, parent):

        self.parent = parent
        self.name = None
        self.item = None
        self.raw_contour = QtGui.QPolygonF()
        self.pencolor = QtGui.QColor(0, 0, 0, 255)
        self.penwidth = 2.5
        self.brushcolor = QtGui.QColor(150, 150, 150, 255)
        # FIXME
        # FIXME work with graphicsitem.data to set key:value pairs
        # FIXME as item information
        # FIXME

    def readContour(self, fname, comment='#'):

        if fname == 'predefined':
            self.name = '"D:\Dropbox\PyAero\data\RC_Glider\mh32.dat"'
            lines = f.readlines()
        else:
            self.name = fname
            with open(fname, mode='r') as f:
                lines = f.readlines()

        data = [line for line in lines if comment not in line]
        x = [float(l.split()[0]) for l in data]
        y = [float(l.split()[1]) for l in data]
        points = [(px, py) for px, py in zip(x, y)]

        # store contour points as type QPointF
        for pt in points:
            x = pt[0] * CHORDLENGTH
            y = pt[1] * CHORDLENGTH
            self.raw_contour.append(QtCore.QPointF(x, y))

        # add airfoil points as GraphicsItem to the scene
        self.addContour()
        # create a group of items that carries conour, markers, etc.
        self.createItemsGroup()
        # add the markers to the group
        self.addMarkers()
        # add the chord to the group
        self.addChord()

        fileinfo = QtCore.QFileInfo(self.name)
        name = fileinfo.fileName()
        logger.log.info('Airfoil <b><font color="#2784CB">' + name +
                        '</b> successfully loaded')

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
        self.item = self.parent.scene.addGraphicsItem(contour)

    def createItemsGroup(self):
        """Container that treats a group of items as a single item
        One item is the contour itself
        Other items are chord, camber, point markers, etc.
        """
        self.contour_group = QtGui.QGraphicsItemGroup(parent=self.item,
                                                      scene=self.parent.scene)

        # This stops the QGraphicsItemGroup trying to handle the event,
        # and lets the child QGraphicsItems handle them
        # self.contour_group.setHandlesChildEvents(false)

    def addMarkers(self):
        for point in self.raw_contour:
            x = QtCore.QPointF(point).x()
            y = QtCore.QPointF(point).y()

            # put airfoil contour points as graphicsitem
            points = gc.GraphicsCollection()
            points.pen.setColor(QtGui.QColor(90, 90, 90, 255))
            points.pen.setWidth(1.5)
            points.pen.setCosmetic(True)  # no pen thickness change when zoomed
            points.brush.setColor(QtGui.QColor(200, 0, 0, 255))
            points.Circle(x, y, 0.3)

            self.markers = PGraphicsItem.GraphicsItem(points,
                                                      self.parent.scene)
            # self.markers.setFlag(QtGui.QGraphicsItem.
            #                      ItemIgnoresTransformations, True)
            self.contour_group.addToGroup(self.markers)

    def addChord(self):
        line = gc.GraphicsCollection()
        color = QtGui.QColor(70, 70, 70, 255)
        line.pen.setColor(color)
        line.pen.setWidth(1)
        line.pen.setCosmetic(True)  # no pen thickness change when zoomed
        line.pen.setJoinStyle(QtCore.Qt.RoundJoin)
        line.pen.setStyle(QtCore.Qt.CustomDashLine)
        # pattern is 1px dash, 4px space, 7px dash, 4px
        line.pen.setDashPattern([1, 4, 10, 4])
        line.Line(0.0, 0.0, CHORDLENGTH, 0.0)

        self.chord = PGraphicsItem.GraphicsItem(line, self.parent.scene)
        self.contour_group.addToGroup(self.chord)

    def camber(self):
        pass

    def setPenColor(self, r, g, b, a):
        self.pencolor = QtGui.QColor(r, g, b, a)

    def setBrushColor(self, r, g, b, a):
        self.brushcolor = QtGui.QColor(r, g, b, a)
