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
        """
        Args:
            item (object): PGraphicsItemsCollection object
            scene (None, optional): the scene
        """
        super(GraphicsItem, self).__init__()

        self.scene = scene

        # FIXME
        # FIXME This does not work. Possibly because mouse events are already
        # FIXME handled in the view or scene and therefore not propagated
        # FIXME
        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, True)
        # docs: For performance reasons, these notifications
        # are disabled by default.
        # needed for : ItemScaleHasChanged
        self.setFlag(QtGui.QGraphicsItem.ItemSendsGeometryChanges, True)

        self.setAcceptsHoverEvents(True)

        # method of QPainter
        self.method = item.method
        self.args = item.args
        self.pen = item.pen
        self.penwidth = item.pen.width()
        self.brush = item.brush
        self.rect = QtCore.QRectF(item.rect)
        self.setToolTip(item.tooltip)
        self.scale = item.scale
        self.info = item.info
        self.font = item.font
        self.shape = item.shape
        self.hoverstyle = QtCore.Qt.SolidLine
        self.hoverwidth = 2.
        if hasattr(item, 'name'):
            self.name = item.name

        # FIXME
        # FIXME half penwidth needed for the correct bounding rect
        # FIXME self.focusrect is anyway calculated in drawFocusRect method
        # FIXME ???????????????
        pw = 0.0
        self.focusrect = QtCore.QRectF(self.rect.left()-pw/2,
                                       self.rect.top()-pw/2,
                                       self.rect.width()+pw,
                                       self.rect.height()+pw)

    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemSelectedHasChanged:
            # when selecting an airfoil item in the graphics view
            # select the respective item in PToolbox/MyListWidget
            # which contains a list of loaded airfoils

            # get MainWindow instance here (avoid handling parents)
            mainwindow = QtCore.QCoreApplication.instance().mainwindow
            centralwidget = mainwindow.centralWidget()
            itms = centralwidget.tools.listwidget. \
                findItems(self.name, QtCore.Qt.MatchExactly)

            if self.isSelected():
                for itm in itms:
                    centralwidget.tools.listwidget. \
                        setItemSelected(itm, True)
            else:
                for itm in itms:
                    centralwidget.tools.listwidget. \
                        setItemSelected(itm, False)
            # give focus to listwidget so that highlighting works
            # (at least for short period until mouse is moved)
            centralwidget.tools.listwidget.setFocus()

        return QtGui.QGraphicsItem.itemChange(self, change, value)

    def mousePressEvent(self, event):

        self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))

        # set item as topmost in stack
        zstack = [itm.zValue() for itm in self.scene.items()]
        zmax = max(zstack)
        self.setZValue(zmax + 1)
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
        painter.setPen(self.pen)
        painter.setFont(self.font)

        if self.isSelected():

            # draw rectangle around selected item
            self.drawFocusRect(painter)

            # make selected item opaque
            color = self.brush.color()
            # color.setAlpha(80)
            brush = QtGui.QBrush(color)
            painter.setBrush(brush)

        # care for difference between objects and text
        # i.e. normally y-coordinates go top down
        # to make a normal coordinate system y-axis is swapped in PGraphicsview
        # since PyQT does this automatically for text in the original setup
        # the text here needs to be swapped back to be printed correctly
        # scale on text items therefore in PGraphicsitemsCollection
        # gets scale (1, -1), all other items get scale (1, 1)
        painter.scale(self.scale[0], self.scale[1])

        # call module painter with its method given by string in self.method
        # args are arguments to method
        # painter is a QPainter instance
        # depending on the method a variable number of arguments is needed
        # example:
        # if self.method = 'drawEllipse'
        # and self.args = QRectF(x, y, w, h)
        # the call to painter would render as:
        # painter.drawEllipse(*self.args)
        getattr(painter, self.method)(*self.args)

    def drawFocusRect(self, painter):
        self.focusbrush = QtGui.QBrush()
        self.focuspen = QtGui.QPen(QtCore.Qt.DashLine)
        self.focuspen.setColor(QtCore.Qt.darkGray)
        self.focuspen.setWidthF(1.)
        self.focuspen.setCosmetic(True)  # no thickness change when zoomed
        painter.setBrush(self.focusbrush)
        painter.setPen(self.focuspen)

        # handle text focusrect
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
