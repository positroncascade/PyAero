from PyQt4 import QtGui


class GraphicsScene(QtGui.QGraphicsScene):
    """The graphics scene manages all items which are drawn in the graphics view
    The coordinates in the scene are the "logical" coordinates. These are the
    real object coordinates. E.g., an airfoil typically is described in an
    x-range from 0 to 1 (no units are given for that). So when PyAero loads an
    airfoil, the GraphicsView provides a view on that graphics item. The
    "fitallinview" after loading, scales the view so that the airfoil is fully
    fitting the graphics view which is in pixels or "physical" coordinates.

    Attributes:
        parent (TYPE): Description
    """
    def __init__(self,  parent=None):
        # call constructor of QGraphicsScene
        super(GraphicsScene, self).__init__(parent)

        self.parent = parent

        # set scene to large size so that scrollbars are small (if shown)
        self.setSceneRect(-5000, -5000, 10000, 10000)

    def mousePressEvent(self, event):
        """Re-implement QGraphicsView's mousePressEvent handler"""

        self.clearSelection()

        # call original implementation of QGraphicsView mousePressEvent handler
        super(GraphicsScene, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Re-implement QGraphicsView's mousePressEvent handler"""

        # call original implementation of QGraphicsView
        # mouseReleaseEvent handler
        super(GraphicsScene, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        """Re-implement QGraphicsView's mousePressEvent handler"""

        # call original implementation of QGraphicsView mouseMoveEvent handler
        super(GraphicsScene, self).mouseMoveEvent(event)
