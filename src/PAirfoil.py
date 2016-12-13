
import numpy as np

from PyQt4 import QtGui, QtCore

import PGraphicsItemsCollection as gc
import PGraphicsItem
import PLogger as logger


class Airfoil(object):
    """Class to read airfoil data from file (or use predefined airfoil)

    The Airfoil object carries several graphics items:
        e.g. raw data, chord, camber, etc.

    Attributes:
        brushcolor (QColor): fill color for airfoil
        chord (QGraphicsItem): Description
        contour_group (QGraphicsItemGroup): Container for all items
            which belong to the airfoil contour
        item (QGraphicsItem): graphics item derived from QPolygonF object
        markers (QGraphicsItem): color for airoil outline points
        name (str): airfoil name (without path)
        pencolor (QColor): color for airoil outline
        penwidth (float): thickness of airfoil outline
        raw_coordinates (numpy array): list of contour points as tuples
        scene (QGraphicsScene): PyAero graphics scene
    """

    def __init__(self, scene, name):

        self.scene = scene
        self.name = name
        self.contour_item = None
        self.raw_coordinates = None
        self.pencolor = QtGui.QColor(10, 10, 20, 255)
        self.penwidth = 2.5
        self.brushcolor = QtGui.QColor()
        self.brushcolor.setNamedColor('#7c8696')

    def readContour(self, filename, comment='#'):

        try:
            with open(filename, mode='r') as f:
                lines = f.readlines()
        except IOError as error:
            logger.log.error('Unable to open file %s. Error was: %s' %
                             (filename, error))
            return False

        data = [line for line in lines if comment not in line]

        # check for correct data
        # specifically important for drag and drop
        try:
            x = [float(l.split()[0]) for l in data]
            y = [float(l.split()[1]) for l in data]
        except (ValueError, IndexError) as error:
            try:
                unicode(error, "ascii")
            except:
                logger.log.error('Unable to parse file %s. Unknown error caught.' %
                                 (filename))
                return False
            logger.log.error('Unable to parse file %s. Error was: %s' %
                             (filename, error))
            logger.log.info('Maybe not a valid airfoil file was used.')
            return False
        except:
            logger.log.error('Unable to parse file %s. Unknown error caught.' %
                             (filename))
            return False

        # store airfoil coordinates as list of tuples
        self.raw_coordinates = np.array((x, y))

        return True

    def addToScene(self):
        # add airfoil points as GraphicsItem to the scene
        self.addContour(self.raw_coordinates)
        # create a group of items that carries contour, markers, etc.
        self.createItemsGroup()
        # add the markers to the group
        self.addMarkers(type='circle')
        # add the chord to the group
        self.addChord()

    def addContour(self, coordinates):
        """Add airfoil points as GraphicsItem to the scene"""

        # instantiate a graphics item
        contour = gc.GraphicsCollection()
        # make it polygon type and populate its points
        points = [QtCore.QPointF(x, y) for x, y in zip(*coordinates)]
        contour.Polygon(QtGui.QPolygonF(points), self.name)
        # set its properties
        contour.pen.setColor(self.pencolor)
        contour.pen.setWidth(self.penwidth)
        contour.pen.setCosmetic(True)  # no pen thickness change when zoomed
        contour.brush.setColor(self.brushcolor)

        # add contour as a GraphicsItem to the scene
        # these are the objects which are drawn in the GraphicsView
        self.contour_item = PGraphicsItem.GraphicsItem(contour, self.scene)

        # add the contour as item to the scene
        self.scene.addItem(self.contour_item)

    def createItemsGroup(self):
        """Container that treats a group of items as a single item
        One item is the contour itself
        Other items are chord, camber, point markers, etc.
        """
        self.contour_group = QtGui.QGraphicsItemGroup(parent=self.contour_item,
                                                      scene=self.scene)
        self.markers = QtGui.QGraphicsItemGroup(parent=self.contour_item,
                                                scene=self.scene)

    def addMarkers(self, type='circle'):
        """Create marker for polygon contour"""
        # FIXME
        # FIXME make more marker types in PGraphicsCollection
        # FIXME and fix also scaling behaviour of markers
        # FIXME
        # FIXME the pen width influences the bounding rect of
        # FIXME so that zoom home (i.e. fitallinView is affected)
        # FIXME
        # FIXME markers could be replaced by images/icons
        # FIXME
        for x, y in zip(*self.raw_coordinates):

            # put airfoil contour points as graphicsitem
            points = gc.GraphicsCollection()
            # be careful with the penwidth as it affects bounding rect
            points.pen.setWidth(0.0001)
            points.pen.setColor(QtGui.QColor(90, 90, 90, 255))
            points.brush.setColor(QtGui.QColor(217, 63, 122, 255))
            points.pen.setCosmetic(True)  # no pen thickness change when zoomed

            if type == 'circle':
                points.Circle(x, y, 0.003, marker=True)

            marker = PGraphicsItem.GraphicsItem(points, self.scene)
            self.markers.addToGroup(marker)

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
