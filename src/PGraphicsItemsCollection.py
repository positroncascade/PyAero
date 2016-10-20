from PyQt4 import QtGui, QtCore


class GraphicsCollection(object):
    def __init__(self, parent=None):

        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setColor(QtGui.QColor(0, 0, 0, 255))
        pen.setWidth(2)
        pen.setJoinStyle(QtCore.Qt.MiterJoin)
        self.pen = pen

        self.brush = QtGui.QBrush(QtGui.QColor(255, 255, 0, 255))
        self.font = QtGui.QFont('Decorative', 12)

        self.rect = QtCore.QRectF()
        self.shape = QtGui.QPainterPath()
        self.path = QtGui.QPainterPath()

        self.scale = (1, 1)
        self.tooltip = ''

        # must be method of QPainter
        self.method = ''
        self.args = []

    def Point(self, x, y):
        # add some pixels to the point rect, so that it can be selected :)
        eps = 4
        self.rect = QtCore.QRectF(x-eps/2, y-eps/2, eps, eps)
        self.shape.addRect(self.rect)
        self.method = 'drawPoint'
        self.args = [x, y]

    def Line(self, x1, y1, x2, y2):
        p1 = QtCore.QPointF(x1-1, y1-1)
        p2 = QtCore.QPointF(x2+1, y2+1)
        self.rect = QtCore.QRectF(p1, p2)
        self.shape.addRect(self.rect)
        self.method = 'drawLine'
        self.args = [x1, y1, x2, y2]

    def Circle(self, x, y, r):
        self.rect = QtCore.QRectF(x-r, y-r, 2*r, 2*r)
        self.shape.addEllipse(self.rect)
        self.method = 'drawEllipse'
        self.args = [self.rect]

    def Rectangle(self, x, y, w, h):
        self.rect = QtCore.QRectF(x, y, w, h)
        self.shape.addRect(self.rect)
        self.method = 'drawRect'
        self.args = [self.rect]

    def Polygon(self, polygon):
        """
        @polygon carries QtGui.QPolygonF() object
        which consists of QPointF tuples
        """
        self.rect = polygon.boundingRect()
        self.shape.addPolygon(polygon)
        self.method = 'drawPolygon'
        self.args = [polygon]

    def Mesh(self, mesh):
        self.method = 'drawPath'
        self.args = []

    def Path(self, path):
        rect = path.boundingRect()
        self.shape.addRect(rect)
        self.method = 'drawPath'
        self.args = [path]

    def Text(self, x, y, text, font):
        # since GraphicsView swaps already y-coordinate, text needs to be
        # flipped back
        self.scale = (1, -1)
        thetext = QtGui.QStaticText(text)
        size = thetext.size()
        self.rect = QtCore.QRectF(x, y, size.width(), size.height())
        self.font = font
        self.method = 'drawStaticText'
        self.args = [x, y, thetext]
        self.shape.addText(x, y, font, text)

    def setPen(self, pen):
        self.pen = pen

    def setBrush(self, brush):
        self.brush = brush

    def setRect(self, rect):
        self.rect = rect

    def setTooltip(self, tooltip):
        self.tooltip = tooltip
