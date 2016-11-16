import math
from PyQt4 import QtGui, QtCore

from PSettings import ZOOMANCHOR, SCROLLBARS, SCALEINC, MINZOOM, MAXZOOM


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

        # set QGraphicsView attributes
        self.setRenderHints(QtGui.QPainter.Antialiasing |
                            QtGui.QPainter.HighQualityAntialiasing)
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

        # handle event
        super(GraphicsView, self).resizeEvent(event)

    def mousePressEvent(self, event):
        # keep track of click position
        self.lastPoint = event.pos()

        # handle event
        super(GraphicsView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # handle event
        super(GraphicsView, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.setFocus()

        point = event.pos()

        # boolean to trigger weather to restrict it horizontally
        if self.moveVertical:
            x = 0
            y = self.lastPoint.y() - point.y()
            if self.parent.airfoil.item.isSelected():
                self.parent.airfoil.item.setPos(QtCore.QPointF(x, y))
            self.lastPoint.y = point.y
        elif self.moveHorizontal:
            x = point.x()
            y = self.lastPoint.y()
            if self.parent.airfoil.item.isSelected():
                self.parent.airfoil.item.setPos(QtCore.QPointF(x, y))

        # handle event
        super(GraphicsView, self).mouseMoveEvent(event)

    def keyPressEvent(self, event):
        key = event.key()

        modifiers = QtGui.QApplication.keyboardModifiers()

        # check if CTRL+SHIFT is pressed simultaneously
        if (modifiers & QtCore.Qt.ControlModifier) and \
                (modifiers & QtCore.Qt.ShiftModifier):
            self.moveVertical = True
            return

        if key == QtCore.Qt.Key_Plus:
            f = SCALEINC
            self.scaleView(f)
        elif key == QtCore.Qt.Key_Minus:
            f = 1.0 / SCALEINC
            self.scaleView(f)
        elif key == QtCore.Qt.Key_Home:
            self.parent.slots.onViewAll()
        elif modifiers == QtCore.Qt.ControlModifier:
            self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
            self.setInteractive(False)

        # handle event
        super(GraphicsView, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):

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
        # DO NOT HANDLE EVENT HERE !!! destroys mouse anchor
        # super(GraphicsView, self).wheelEvent(event)

    def scaleView(self, factor):
        f = self.matrix().scale(factor, factor). \
            mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        # logger.log.info('Scalefactor %s, f = %s' % (factor, f))
        # logger.log.info('MINZOOM %s, MAXZOOM = %s' % (MINZOOM, MAXZOOM))
        if f < MINZOOM or f > MAXZOOM:
            return
        self.scale(factor, factor)

        # cache view to be able to keep it during resize
        self.getSceneFromView()

    def getSceneFromView(self):
        """ cache view to be able to keep it during resize"""

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
        # FIXME
        # FIXME keyboard shortcut does not work
        # FIXME
        # delitems.setShortcut('CTRL+r')

        menu.addSeparator()

        togglebg = menu.addAction('Toggle background')
        togglebg.setShortcut('CTRL+b')

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == togglebg:
            self.parent.slots.onBackground()
        elif action == fitairfoil:
            self.parent.slots.fitAirfoilInView()
        elif action == fitall:
            self.parent.slots.onViewAll()
        # remove all selected items from the scene
        elif action == delitems:
            self.parent.slots.removeGraphicsItem()
