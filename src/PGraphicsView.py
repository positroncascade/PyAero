import math
from PyQt4 import QtGui, QtCore

from PSettings import ZOOMANCHOR, SCROLLBARS, SCALEINC, MINZOOM, MAXZOOM
import PLogger as logger


class GraphicsView(QtGui.QGraphicsView):
    """This is the main window in the GUI where items are drawn upon.
    The class is derived from QtGui.QGraphicsView.
    """

    def __init__(self, parent=None):
        """Construcor of the GraphicsView window

        Args:
            parent (QMainWindow object, optional): class MainWindow
        """
        super(GraphicsView, self).__init__(parent)

        self.parent = parent

        self.moveHorizontal = False
        self.moveVertical = False
        self.CTRL = False

        # set QGraphicsView attributes
        self.setRenderHints(QtGui.QPainter.Antialiasing |
                            QtGui.QPainter.HighQualityAntialiasing |
                            QtGui.QPainter.TextAntialiasing)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        # view behaviour when zooming
        # point under mouse pointer stays fixed during zoom
        if ZOOMANCHOR == 'mouse':
            self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        # view center stays fixed during zoom
        else:
            self.setTransformationAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        if SCROLLBARS:
            self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        else:
            self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # swap y-axis for natural coordinate system
        self.scale(1, -1)

        # cache view to be able to keep it during resize
        self.getSceneFromView()

        # set background color for view
        self.setBackground(self.parent.bgview)

    def setBackground(self, styletype):
        """Switches between gradient and simple background using style sheets.
        border-color (in HTML) works only if border-style is set.
        """

        if styletype == 'gradient':
            style = ("""
            QGraphicsView {border-style:solid; border-color: lightgrey; \
            border-width: 1px; background-color: QLinearGradient( \
            x1: 0.0, y1: 0.0, x2: 0.0, y2: 1.0, \
            stop: 0.4 white, stop: 1.0 blue); } """)
        else:
            style = ("""
            QGraphicsView { border-style:solid; border-color: lightgrey; \
            border-width: 1px; background-color: white } """)

        self.setStyleSheet(style)

    def resizeEvent(self, event):
        # scrollbars need to be switched off when calling fitinview from
        # within resize event otherwise strange recursion can occur
        self.fitInView(self.sceneview, mode=QtCore.Qt.KeepAspectRatio)

        # continue handling events
        super(GraphicsView, self).resizeEvent(event)

    def mousePressEvent(self, event):

        if not self.CTRL:
            self.setDragMode(QtGui.QGraphicsView.RubberBandDrag)

        # keep track of click position
        self.lastPoint = event.pos()

        # continue handling events
        super(GraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # continue handling events
        super(GraphicsView, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.setFocus()

        point = event.pos()

        # FIXME
        # FIXME both horizontal and vertical don't work yet
        # FIXME
        # boolean to trigger movement restriction
        if self.moveVertical:
            x = 0
            y = self.lastPoint.y() - point.y()
            for airfoil in self.parent.airfoils:
                if airfoil.contour_item.isSelected():
                    airfoil.contour_item.setPos(QtCore.QPointF(x, y))
            self.lastPoint.y = point.y
        elif self.moveHorizontal:
            x = point.x()
            y = self.lastPoint.y()
            for airfoil in self.parent.airfoils:
                if airfoil.contour_item.isSelected():
                    airfoil.contour_item.setPos(QtCore.QPointF(x, y))

        selected = False
        for airfoil in self.parent.airfoils:
            if airfoil.contour_item.isSelected():
                selected = True
        # if at least one airfoil ist selected in the view
        # then give focus to the listwidget with its name
        if selected:
            mainwindow = QtCore.QCoreApplication.instance().mainwindow
            centralwidget = mainwindow.centralWidget()
            centralwidget.tools.listwidget.setFocus()

        # continue handling mouse move events
        super(GraphicsView, self).mouseMoveEvent(event)

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = QtGui.QApplication.keyboardModifiers()

        # check if CTRL+SHIFT is pressed simultaneously
        if (modifiers & QtCore.Qt.ControlModifier) and \
                (modifiers & QtCore.Qt.ShiftModifier):
            # FIXME
            # FIXME don't do anything until above code is fixed
            # FIXME in the mouse move event
            # self.moveVertical = True
            return

        if key == QtCore.Qt.Key_Plus:
            f = SCALEINC
            self.scaleView(f)
        elif key == QtCore.Qt.Key_Minus:
            f = 1.0 / SCALEINC
            self.scaleView(f)
        elif key == QtCore.Qt.Key_Home:
            self.parent.slots.onViewAll()
        elif key == QtCore.Qt.Key_Delete:
            self.parent.slots.removeAirfoil()
        elif modifiers == QtCore.Qt.ControlModifier:
            self.CTRL = True
            self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
            self.setInteractive(False)

        # continue handling other key press events
        super(GraphicsView, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            self.CTRL = False

        self.moveHorizontal = False
        self.moveVertical = False

        if self.dragMode() == QtGui.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtGui.QGraphicsView.NoDrag)
            self.setInteractive(True)
            # cache view to be able to keep it during resize
            self.getSceneFromView()

        # handle event
        super(GraphicsView, self).keyReleaseEvent(event)

    def wheelEvent(self, event):
        f = SCALEINC
        if math.copysign(1, event.delta()) > 0:
            f = 1.0 / SCALEINC

        self.scaleView(f)

        # rescale markers during zoom
        # i.e. keep them constant size
        # self.adjustMarkerSize(f)

        # DO NOT CONTINUE HANDLING EVENTS HERE!!!
        # this would destroy the mouse anchor
        # super(GraphicsView, self).wheelEvent(event)

    def scaleView(self, factor):

        # m = self.matrix()
        # logger.log.info('Matrix scalex, scaley: %s %s' % (m.m11(), m.m22()))
        # logger.log.info('Matrix dx, dy: %s %s' % (m.dx(), m.dy()))

        f = self.matrix().scale(factor, factor). \
            mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if f < MINZOOM or f > MAXZOOM:
            return
        self.scale(factor, factor)

        # cache view to be able to keep it during resize
        self.getSceneFromView()

    def adjustMarkerSize(self, f):
        """Adjust marker size during zoom. Marker items are circles
        which are affected by zoom.
        """
        for airfoil in self.parent.airfoils:
            if hasattr(airfoil, 'markers'):
                markers = airfoil.markers.childItems()
                for marker in markers:
                    # in case of circle, args is a QRectF
                    rect = marker.args[0]
                    r = rect.width() / 2.
                    x = rect.left() + r
                    y = rect.top() + r
                    r /= f
                    marker.args = [QtCore.QRectF(x-r, y-r, 2.*r, 2.*r)]

    def getSceneFromView(self):
        """Cache view to be able to keep it during resize"""

        # map view rectangle to scene coordinates
        polygon = self.mapToScene(self.rect())

        # sceneview describes the rectangle which is currently
        # being viewed in scene coordinates
        # this is needed during resizing to be able to keep the view
        self.sceneview = QtCore.QRectF(polygon[0], polygon[2])

    def contextMenuEvent(self, event):
        """creates popup menu for the graphicsview"""

        menu = QtGui.QMenu(self)

        fitairfoil = menu.addAction('Fit airfoil in view')
        fitairfoil.setShortcut('CTRL+f')

        fitall = menu.addAction('Fit all items in view')
        fitall.setShortcut('CTRL+SHIFT+f')

        menu.addSeparator()

        delitems = menu.addAction('Delete selected')
        delitems.setShortcut('Del')

        menu.addSeparator()

        togglebg = menu.addAction('Toggle background')
        togglebg.setShortcut('CTRL+b')

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == togglebg:
            self.parent.slots.onBackground()
        elif action == fitairfoil:
            for id, airfoil in enumerate(self.parent.airfoils):
                if airfoil.contour_item.isSelected():
                    self.parent.slots.fitAirfoilInView(id)
        elif action == fitall:
            self.parent.slots.onViewAll()
        # remove all selected items from the scene
        elif action == delitems:
            self.parent.slots.removeAirfoil()

        # continue handling events
        super(GraphicsView, self).contextMenuEvent(event)
