from PyQt4 import QtGui, QtCore


class GraphicsItem(QtGui.QGraphicsItem):
    """
     From the QT docs:
     To write your own graphics item, you first create a subclass
     of QGraphicsItem, and then start by implementing its two pure
     virtual public functions: boundingRect(), which returns an estimate
     of the area painted by the item, and paint(),
     which implements the actual painting.
    """

    def __init__(self, item, scene=None):
        # call constructor of QGraphicsItem
        super(GraphicsItem, self).__init__()

        self.scene = scene

        # FIXME
        # FIXME This does not work. Possibly because mouse events are already
        # FIXME handled in the view or scene and therefore not propagated
        # FIXME
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)

        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, True)

        self.setAcceptsHoverEvents(True)

        self.method = item.method  # method of QPainter
        self.args = item.args
        self.pen = item.pen
        self.penwidth = item.pen.width()
        self.brush = item.brush
        self.rect = QtCore.QRectF(item.rect)
        self.setToolTip(item.tooltip)
        self.scale = item.scale
        self.font = item.font
        self.shape = item.shape
        self.hoverstyle = QtCore.Qt.SolidLine
        self.hoverwidth = 0.01

        self.focusrect = QtCore.QRectF(self.rect.left(), self.rect.top(),
                                       self.rect.width(), self.rect.height())

    def mousePressEvent(self, event):

        self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))

        # FIXME
        # FIXME do this only when an item is clicked
        # FIXME
        # set item as topmost in stack
        self.setZValue(self.scene.items()[0].zValue() + 1)
        self.setSelected(True)

        # handle event
        super(GraphicsItem, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        # handle event
        super(GraphicsItem, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):

        # handle event
        super(GraphicsItem, self).mouseMoveEvent(event)

    def shape(self):
        # this function may be overwritten when subclassing QGraphicsItem
        # it gives more accurate results for collision detection, etc.
        return self.shape

    def boundingRect(self):
        # this function must be overwritten when subclassing QGraphicsItem
        # bounding box rect shall be set to the bounds of the item. Due to the
        # line thickness this rect is bigger than the rect of the ellipse or
        # rect, etc.
        # rect + line thickness is size
        return self.focusrect

    def paint(self, painter, option, widget):
        # this function must be overwritten when subclassing QGraphicsItem
        painter.setBrush(self.brush)
        if self.isSelected():
            color = self.brush.color()
            color.setAlpha(80)
            brush = QtGui.QBrush(color)
            painter.setBrush(brush)
        painter.setPen(self.pen)
        painter.setFont(self.font)

        # care for difference between objects and text
        painter.scale(self.scale[0], self.scale[1])

        # call module painter with its method given by string in self.method
        # args are arguments to method
        # depending on the method a variable number of arguments is needed
        getattr(painter, self.method)(*self.args)

        if self.isSelected():
            self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)
            self.drawFocusRect(painter)

    def drawFocusRect(self, painter):
        self.focusbrush = QtGui.QBrush()
        self.focuspen = QtGui.QPen(QtCore.Qt.DotLine)
        self.focuspen.setColor(QtCore.Qt.black)
        self.focuspen.setWidthF(1.)
        self.focuspen.setCosmetic(True)  # no thickness change when zoomed
        painter.setBrush(self.focusbrush)
        painter.setPen(self.focuspen)
        if 'text' in self.method.lower():
            size = self.args[2].size()
            self.rect = QtCore.QRectF(
                self.args[0], self.args[1], size.width(), size.height())

            self.focusrect = QtCore.QRectF(
                self.rect.left() - self.penwidth / 2,
                self.rect.top() - self.penwidth / 2,
                self.rect.width() + self.penwidth,
                self.rect.height() + self.penwidth)

        painter.drawRect(self.focusrect)

    def hoverEnterEvent(self, event):
        if not self.isSelected():
            self.pen.setWidthF(self.penwidth + self.hoverwidth)
        # handle event
        super(GraphicsItem, self).hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.pen.setWidthF(self.penwidth)
        # handle event
        super(GraphicsItem, self).hoverLeaveEvent(event)
