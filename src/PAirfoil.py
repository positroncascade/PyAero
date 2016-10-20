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
from PSettings import *

# base64 encoded string representation of gzipped airfoil coordinate file
# MH32 is an airfoil for rc-gliders by Martin Hepperle
MH32_COMPRESSED = '''
H4sICIlqr1IC/21oMzJfY29udG91ci50eHQAZVM7jlRBDIx3TjHSiJCV/5+cgIRTIALE/XNc7p4E
Npmteu2yXbZfj9fzx3eVZ30mP788v/3++efX4/XgT8LfB53fB312R8rB6sCVFIvZ93uy+WINBfZ5
tzgygMVEgZnKBldr8GJPvC+vLmBhWSxUqy8jPDizc+NVuYE1yBY3I380cQKbRQKb+NZrncDe6vve
TQXYNA8uRby1nv6Cg4HNaOsLI+RTNLTYA/2rpa4/EQJ9JZY63wv9yrRlJ14RLzwNHv1Gfs48/ngZ
+mOTo+/aBczE+95q6yEYslgM+cmzt171gB5p1sZLCfKNj30wrR/ju6yfrAR9moerT96r98+88Z0/
vuIfOwmY8xJVS8hYtwRLboj5SCwxswExQ4lD1A6ZOm+IUG7XyveFTJ0goiwvkehbqKPfhK2xM8BL
7KaM81WHYIGGOpedtN0729nJdx0CDfO4WTgUhPP4fAhb++aBXEIYosHpt7lZcRDRfuqgWU1sJPfb
oCBYmpEW10LdnR6tIzrmxi69ymluCum9CpJj0LgsezZy007M3pF12J2TnruTc2dT6b1Lvpjv3b7n
6v/d9V9zm9bCAAQAAA=='''


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
        else:
            self.name = fname
            f = open(fname, 'r')

        # filter comment lines
        data = filter(lambda row: row[0] != comment, f)
        f.close()
        # slist is a nested list looking like [['1.0', '0.0'], ['0.9', '0.1'],
        # ...]
        slist = [row.strip('\n').split() for row in data]
        points = [(float(pt[0]), float(pt[1])) for pt in slist]

        for pt in points:
            x = pt[0] * AIRFOILSIZE
            y = pt[1] * AIRFOILSIZE
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

        line.Line(0.0, 0.0, AIRFOILSIZE, 0.0)

        self.chord = PGraphicsItem.GraphicsItem(line, self.parent.scene)
        self.raw_contour_group.addToGroup(self.chord)

    def camber(self):
        for pt in self.raw_contour:
            pass

    def setPenColor(self, r, g, b, a):
        self.pencolor = QtGui.QColor(r, g, b, a)

    def setBrushColor(self, r, g, b, a):
        self.Brushcolor = QtGui.QColor(r, g, b, a)
