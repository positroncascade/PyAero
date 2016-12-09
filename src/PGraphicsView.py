import math
from PyQt4 import QtGui, QtCore

from PSettings import ZOOMANCHOR, SCROLLBARS, SCALEINC, MINZOOM, MAXZOOM, \
                      MARKERSIZE, MARKERPENWIDTH
import PLogger as logger


class GraphicsView(QtGui.QGraphicsView):
    """The graphics view is the canvas where airfoils are drawn upon
    Its coordinates are in pixels or "physical" coordinates.

    Attributes:
        CTRL (bool): store
        parent (TYPE): Description
        sceneview (TYPE): Description
    """
    def __init__(self, parent=None):
        """Constructor of the GraphicsView window

        Args:
            parent (QMainWindow object, optional): class MainWindow
        """
        super(GraphicsView, self).__init__(parent)

        self.parent = parent

        self.rubberband = RubberBand(QtGui.QRubberBand.Rectangle, self)
        self.rubberband.setStyle

        # make view being not interactive by default
        # nothing can be selected by clicking or rubberbanddrag
        self.setInteractive(False)

        # set QGraphicsView attributes
        self.setRenderHints(QtGui.QPainter.Antialiasing |
                            QtGui.QPainter.HighQualityAntialiasing |
                            QtGui.QPainter.TextAntialiasing)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        # view behaviour when zooming
        if ZOOMANCHOR == 'mouse':
            # point under mouse pointer stays fixed during zoom
            self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        else:
            # view center stays fixed during zoom
            self.setTransformationAnchor(QtGui.QGraphicsView.AnchorViewCenter)

        if SCROLLBARS:
            self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        else:
            self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # normally (0, 0) is upperleft corner of view
        # swap y-axis in order to make (0, 0) lower left
        # and y-axis pointing upwards
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
        """Re-implement QGraphicsView's resizeEvent handler"""

        # call original implementation of QGraphicsView resizeEvent handler
        super(GraphicsView, self).resizeEvent(event)

        # scrollbars need to be switched off when calling fitinview from
        # within resize event otherwise strange recursion can occur
        self.fitInView(self.sceneview, mode=QtCore.Qt.KeepAspectRatio)

    def mousePressEvent(self, event):
        """Re-implement QGraphicsView's mousePressEvent handler"""

        # call original implementation of QGraphicsView mousePressEvent handler
        super(GraphicsView, self).mousePressEvent(event)

        # initiate rubberband origin and size (zero at first)
        self.origin = event.pos()
        self.rubberband.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()

        # returns the current state of the modifier keys on the keyboard
        # modifiers = QtGui.QApplication.keyboardModifiers()

    def mouseMoveEvent(self, event):
        """Re-implement QGraphicsView's mouseMoveEvent handler"""

        # call original implementation of QGraphicsView mouseMoveEvent handler
        super(GraphicsView, self).mouseMoveEvent(event)

        # if a mouse event happens in the graphics view
        # put the keyboard focus to the view as well
        self.setFocus()

        # returns the current state of the modifier keys on the keyboard
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            pass

        if self.rubberband.isVisible():
            self.rubberband.setGeometry(
                QtCore.QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        """Re-implement QGraphicsView's mouseReleaseEvent handler"""

        # call original implementation of QGraphicsView
        # mouseReleaseEvent handler
        super(GraphicsView, self).mouseReleaseEvent(event)

        if self.rubberband.isVisible():
            self.rubberband.hide()
            rect = self.rubberband.geometry()
            rectf = self.mapToScene(rect).boundingRect()
            # zoom the selected rectangle
            self.fitInView(rectf, mode=QtCore.Qt.KeepAspectRatio)

            # rescale markers during zoom
            # i.e. keep them constant size
            self.adjustMarkerSize()

    def keyPressEvent(self, event):
        """Re-implement QGraphicsView's keyPressEvent handler"""

        key = event.key()

        # call original implementation of QGraphicsView keyPressEvent handler
        super(GraphicsView, self).keyPressEvent(event)

        modifiers = QtGui.QApplication.keyboardModifiers()

        # check if CTRL+SHIFT is pressed simultaneously
        if (modifiers & QtCore.Qt.ControlModifier) and \
                (modifiers & QtCore.Qt.ShiftModifier):
            pass

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
            pass
            # self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
            # self.setInteractive(False)

    def keyReleaseEvent(self, event):
        """Re-implement QGraphicsView's keyReleaseEvent handler"""

        # call original implementation of QGraphicsView keyReleaseEvent handler
        super(GraphicsView, self).keyReleaseEvent(event)

        # if self.dragMode() == QtGui.QGraphicsView.ScrollHandDrag:
        #     self.setDragMode(QtGui.QGraphicsView.NoDrag)
        #     self.setInteractive(True)
        #     # cache view to be able to keep it during resize
        #     self.getSceneFromView()

    def wheelEvent(self, event):
        """Re-implement QGraphicsView's wheelEvent handler"""

        f = SCALEINC
        if math.copysign(1, event.delta()) > 0:
            f = 1.0 / SCALEINC

        self.scaleView(f)

        # rescale markers during zoom
        # i.e. keep them constant size
        self.adjustMarkerSize()

        # DO NOT CONTINUE HANDLING EVENTS HERE!!!
        # this would destroy the mouse anchor
        # call original implementation of QGraphicsView wheelEvent handler
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

    def adjustMarkerSize(self):
        """Adjust marker size during zoom. Marker items are circles
        which are otherwise affected by zoom.
        """
        # markers are drawn in PGraphicsItem using scene coordinates
        # in order to keep them constant size, also when zooming
        # a fixed pixel size is mapped to scene coordinates
        # depending on the zoom, this leads to always different scene
        # coordinates
        # map a square with side length of MARKERSIZE to the scene coords
        poly = self.mapToScene(QtCore.QRect(0, 0, MARKERSIZE+1, MARKERSIZE+1))
        pw = self.mapToScene(QtCore.QRect(0, 0, MARKERPENWIDTH,
                             MARKERPENWIDTH))
        rect = poly.boundingRect()
        pw_mapped = pw.boundingRect()
        r = rect.width() / 2.

        for airfoil in self.parent.airfoils:
            if hasattr(airfoil, 'markers'):
                markers = airfoil.markers.childItems()
                x, y = airfoil.raw_coordinates
                for i, marker in enumerate(markers):
                    # in case of circle, args is a QRectF
                    marker.args = [QtCore.QRectF(x[i]-r, y[i]-r, 2.*r, 2.*r)]
                    marker.penwidth = pw_mapped

    def getSceneFromView(self):
        """Cache view to be able to keep it during resize"""

        # map view rectangle to scene coordinates
        polygon = self.mapToScene(self.rect())

        # sceneview describes the rectangle which is currently
        # being viewed in scene coordinates
        # this is needed during resizing to be able to keep the view
        self.sceneview = QtCore.QRectF(polygon[0], polygon[2])

    def updateListWidget(self):

        selected = False
        for airfoil in self.parent.airfoils:
            if airfoil.contour_item.isSelected():
                selected = True
        # if at least one airfoil ist selected in the view
        # then give focus to the listwidget to highlight selections
        if selected:
            mainwindow = QtCore.QCoreApplication.instance().mainwindow
            centralwidget = mainwindow.centralWidget()
            centralwidget.tools.listwidget.setFocus()

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


class RubberBand(QtGui.QRubberBand):
    """Custom rubberband
    from: http://stackoverflow.com/questions/25642618
    """

    def __init__(self, *arg, **kwargs):

        super(RubberBand, self).__init__(*arg, **kwargs)

        # set style selectively for the rubberband like that
        # see: http://stackoverflow.com/questions/25642618
        self.setStyle(QtGui.QStyleFactory.create('windowsvista'))

    def paintEvent(self, QPaintEvent):

        painter = QtGui.QPainter(self)

        # set pen
        pen = QtGui.QPen(QtCore.Qt.darkBlue)
        pen.setWidth(6)
        painter.setPen(pen)

        # set brush
        color = QtGui.QColor(QtCore.Qt.darkGray)
        painter.setBrush(QtGui.QBrush(color))

        # set opacity
        painter.setOpacity(0.3)

        # draw rectangle
        painter.drawRect(QPaintEvent.rect())
