"""
Airfoil description and plotting class
"""

import base64
from cStringIO import StringIO
import gzip

from PyQt4 import QtGui, QtCore

import PGraphicsItemsCollection as gc
import PGraphicsItem
import PLogger as logger
from PSettings import CHORDLENGTH, MH32_COMPRESSED


class Airfoil(object):
    # call constructor of Airfoil

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
            self.name = 'MH32.dat'
            # decode and unzip
            f = gzip.GzipFile(mode='rb',
                              fileobj=StringIO(base64.b64decode(
                               MH32_COMPRESSED)))
            lines = f.readlines()
        else:
            self.name = fname
            with open(fname, mode='r') as f:
                lines = f.readlines()

        data = [line for line in lines if comment not in line]
        x = [float(l.split()[0]) for l in data]
        y = [float(l.split()[1]) for l in data]
        points = [(px, py) for px, py in zip(x, y)]

        for pt in points:
            x = pt[0] * CHORDLENGTH
            y = pt[1] * CHORDLENGTH
            self.raw_contour.append(QtCore.QPointF(x, y))

        fileinfo = QtCore.QFileInfo(self.name)
        name = fileinfo.fileName()
        logger.log.info('Airfoil <b><font color="#2784CB">' + name +
                        '</b> successfully loaded')

        polygon = gc.GraphicsCollection()
        polygon.pen.setColor(self.pencolor)
        polygon.pen.setWidth(self.penwidth)
        polygon.pen.setCosmetic(True)  # no pen thickness change when zoomed
        polygon.brush.setColor(self.brushcolor)

        polygon.Polygon(self.raw_contour)

        self.item = self.parent.scene.addGraphicsItem(polygon)

        # add shadow effect to airfoil
        # shadow = QtGui.QGraphicsDropShadowEffect()
        # self.item.setGraphicsEffect(shadow)

        # for drawing raw contour points
        self.raw_contour_group = QtGui. \
            QGraphicsItemGroup(parent=self.item, scene=self.parent.scene)

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
            item = PGraphicsItem.GraphicsItem(points, self.parent.scene)

            self.raw_contour_group.addToGroup(item)

            # This stops the QGraphicsItemGroup trying to handle the event,
            # and lets the child QGraphicsItems handle them
            # setHandlesChildEvents(false)

        # create line item for the chord
        self.makeChord()

    def getCoords(self):
        x = [QtCore.QPointF(point).x() for point in self.raw_contour]
        y = [QtCore.QPointF(point).y() for point in self.raw_contour]
        return x, y

    def makeChord(self):
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
        self.raw_contour_group.addToGroup(self.chord)

    def camber(self):
        for pt in self.raw_contour:
            pass

    def setPenColor(self, r, g, b, a):
        self.pencolor = QtGui.QColor(r, g, b, a)

    def setBrushColor(self, r, g, b, a):
        self.Brushcolor = QtGui.QColor(r, g, b, a)
