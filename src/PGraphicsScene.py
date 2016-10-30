from PyQt4 import QtGui, QtCore

import PGraphicsItem


class GraphicsScene(QtGui.QGraphicsScene):
    # call constructor of GraphicsScene
    def __init__(self,  parent=None):
        # call constructor of QGraphicsScene
        super(GraphicsScene, self).__init__(parent)

        self.parent = parent

        # set scene to large size so that scrollbars are small (if shown)
        self.setSceneRect(-5000, -5000, 10000, 10000)

    def mousePressEvent(self, event):
        self.clearSelection()
        # handle event
        super(GraphicsScene, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # handle event
        super(GraphicsScene, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        # handle event
        super(GraphicsScene, self).mouseMoveEvent(event)
