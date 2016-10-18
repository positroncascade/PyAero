#!d:/python27/python -u

"""
Python implementation of a 2D airfoil contour analysis and meshing tool.

The purpose of the contour analysis tool is to be able to read airfoil
contour data and analyze them with respect to smoothness and alike properties.
Functions allow splining, refinement, smoothing, etc. in order to provide
accurate input to the subsequent meshing process.

The meshing tool provides features to be able to create 2D CFD meshes
for numerical airfoil analysis.
"""

import sys
import math
from PyQt4 import QtGui, QtCore


__author__ = 'Andreas Ennemoser'
__copyright__ = 'GPL'
__credits__ = []
__license__ = "GPL"
__version__ = "0.3"
__email__ = 'andreas.ennemoser@aon.at'
__status__ = 'Prototype'


class GraphicsItem(QtGui.QGraphicsItem):
    """
     From the QT docs:
     To write your own graphics item, you first create a subclass
     of QGraphicsItem, and then start by implementing its two pure 
     virtual public functions: boundingRect(), which returns an estimate
     of the area painted by the item, and paint(), 
     which implements the actual painting.
    """
    # call constructor of GraphicsItem
    def __init__(self, rect, pen, brush, tooltip='No tip here', parent=None):
        # call constructor of QGraphicsItem
        super(GraphicsItem, self).__init__()

        self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QtGui.QGraphicsItem.ItemIsFocusable, True)

        self.setAcceptsHoverEvents(True)

        self.pen = pen
        pw = self.pen.widthF()
        self.brush = QtGui.QBrush(QtCore.Qt.blue)
        self.brush = brush
        self.setToolTip(tooltip)
        self.parent = parent
        
        self.rect = QtCore.QRectF(rect[0], rect[1], rect[2], rect[3])
        self.focusrect = QtCore.QRectF(rect[0]-pw/2, rect[1]-pw/2,
                rect[2]+pw, rect[3]+pw)

    def mousePressEvent(self, event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
        # set item as topmost in stack
        self.setZValue(self.parent.items()[0].zValue() + 1)
        self.setSelected(True)
        # propagate event
        QtGui.QGraphicsItem.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        # propagate event
        QtGui.QGraphicsItem.mouseReleaseEvent(self, event)

    def mouseMoveEvent(self, event):
        # propagate event
        QtGui.QGraphicsItem.mouseMoveEvent(self, event)

    def boundingRect(self):
        # bounding box rect shall be set to the bounds of the item. Due to the
        # line thickness this rect is bigger than the rect of the ellipse or rect, etc.
        return self.focusrect

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.drawEllipse(self.rect)
        if self.isSelected():
            self.drawFocusRect(painter)
            self.setFlag(QtGui.QGraphicsItem.ItemIsMovable, True)

    def drawFocusRect(self, painter):
        self.focusbrush = QtGui.QBrush()
        self.focuspen = QtGui.QPen(QtCore.Qt.DotLine)
        self.focuspen.setColor(QtCore.Qt.black)
        self.focuspen.setWidthF(1.5)
        painter.setBrush(self.focusbrush)
        painter.setPen(self.focuspen)
        painter.drawRect(self.focusrect)

    def hoverEnterEvent(self, event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        self.pen.setStyle(QtCore.Qt.DotLine)
        # propagate event
        QtGui.QGraphicsItem.hoverEnterEvent(self, event)

    def hoverLeaveEvent(self, event):
        self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.pen.setStyle(QtCore.Qt.SolidLine)
        # propagate event
        QtGui.QGraphicsItem.hoverLeaveEvent(self, event)


class GraphicsScene (QtGui.QGraphicsScene):
    # call constructor of GraphicsScene
    def __init__ (self, parent=None):
        # call constructor of QGraphicsScene
        super(GraphicsScene, self).__init__(parent)

        self.parent = parent
        self.setSceneRect(-200, -200, 400, 400)

    def mousePressEvent(self, event):
        self.clearSelection()
        # propagate event
        super(GraphicsScene, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # propagate event
        super(GraphicsScene, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        super(GraphicsScene, self).mouseMoveEvent(event)

    def addGraphicsItem(self, rect, pw, pc, bc, tooltip):
        pen = QtGui.QPen(QtCore.Qt.SolidLine)
        pen.setColor(QtGui.QColor(pc[0], pc[1], pc[2], 255))
        pen.setWidth(pw)
        brush = QtGui.QBrush(QtGui.QColor(bc[0], bc[1], bc[2], 255))
        self.item = GraphicsItem(rect, pen, brush, tooltip, self)
        self.parent.scene.addItem(self.item)


class GraphicsView (QtGui.QGraphicsView):
    # call constructor of GraphicsView
    def __init__(self, parent=None):
        # call constructor of QGraphicsView
        super(GraphicsView, self).__init__(parent)

        # set QGraphicsView attributes
        self.setRenderHints(QtGui.QPainter.Antialiasing |
                QtGui.QPainter.HighQualityAntialiasing)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # save home position
        self.home = self.matrix()

        # set background style
        self.viewstyle = \
            'background-color:QLinearGradient(  \
            x1: 0.0, y1: 0.0, x2: 0.0, y2: 1.0,  \
            stop: 0.3 white,  \
            stop: 1.0 blue); \
            '
        self.setStyleSheet(self.viewstyle)

    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Escape:
            sys.exit(QtGui.qApp.quit())
        elif key == QtCore.Qt.Key_Plus:
            self.scaleView(1.2)
        elif key == QtCore.Qt.Key_Minus:
            self.scaleView(1 / 1.2)
        elif key == QtCore.Qt.Key_Home:
            self.setMatrix(self.home)
        else:
            # propagate event
            super(GraphicsView, self).keyPressEvent(event)

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.delta() / 500.0))
        # propagate event
        super(GraphicsView, self).wheelEvent(event)

    def scaleView(self, factor):
        f = self.matrix().scale(factor, factor). \
                    mapRect(QtCore.QRectF(0, 0, 1, 1)).width()
        if f < 0.05 or f > 50:
            return
        self.scale(factor, factor)


class CentralWidget(QtGui.QWidget):
    # call constructor of CentralWidget
    def __init__(self, parent=None):
        # call constructor of QWidget
        super(CentralWidget, self).__init__(parent)

        self.parent = parent

        # create toolbox widget for left side of splitter
        self.toolBox = QtGui.QToolBox()

        self.item1 = self.toolBox.addItem(QtGui.QWidget(), "Item 1")
        self.item2 = self.toolBox.addItem(QtGui.QWidget(), "Item 2")
        self.item3 = self.toolBox.addItem(QtGui.QWidget(), "Item 3")
        self.item4 = self.toolBox.addItem(QtGui.QWidget(), "Item 4")
        self.toolBox.setItemToolTip(0, 'Mal sehn ... aus Item 1')
        icon = QtGui.QIcon('icons/document-open.png')
        self.toolBox.setItemIcon(2, icon)
        self.toolBox.setCurrentIndex(3)

        # split main window horizontally into two panes
        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.toolBox)
        self.splitter.addWidget(self.parent.view)
        self.splitter.setStretchFactor(0, 1) # 0 ... left pane, 1 ... fraction of split
        self.splitter.setStretchFactor(1, 4) # 1 ... right pane, 4 ... fraction of split

        # put splitter in a layout box
        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))


class MainWindow(QtGui.QMainWindow):
    # call constructor of MainWindow
    def __init__(self, parent=None):
        # call constructor of QMainWindow
        super(MainWindow, self).__init__(parent)

        self.view = GraphicsView(self)
        self.scene = GraphicsScene(self)
        # set the scene
        self.view.setScene(self.scene)

        # add items to the scene
        self.scene.addGraphicsItem((0, 0, 250, 250), 8.0, (255, 0, 0), (0, 0, 255), 'My first item')
        self.scene.addGraphicsItem((-250, -250, 300, 200), 4.0, (0, 0, 0), (255, 0, 100), 'My 2nd item')
        self.scene.addGraphicsItem((200, -200, 200, 200), 10.0, (0, 0, 255), (0, 255, 100), 'My 3rd item')

        # set central widget for the application
        self.setCentralWidget(CentralWidget(self))

        # setup user interface and menus
        self.initUI()

    def initUI(self):               
  
        # window size, position and title
        self.setGeometry(600, 100, 1200, 900)
        self.setWindowTitle('Airfoil Mesher')    
        self.show()

        # create a status bar
        self.statusbar = self.statusBar()
        self.statusbar.setCursor(QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
        self.statusbar.showMessage('Ready.')
        self.statusbarstyle = 'background-color:rgb(200,200,200); color:black'
        self.statusbar.setStyleSheet(self.statusbarstyle)

        # define extension to be filtered in file dialogs
        self.filefilter = \
            'Airfoil mesh files (*.txt *.msh);;Airfoil contour files (*.dat)'

        # create a menu bar
        menubar = self.menuBar()

        # populate menus
        fileMenu = menubar.addMenu('&File')

        icon = QtGui.QIcon('icons/document-open.png')
        actionOpen = QtGui.QAction(icon, '&Open', self, shortcut='CTRL+o',
                statusTip='Open file ...', triggered=self.onOpen)
        f_open = fileMenu.addAction(actionOpen)

        icon = QtGui.QIcon('icons/document-save.png')
        actionSave = QtGui.QAction(icon, '&Save', self, shortcut='CTRL+s',
                statusTip='Save file ...', triggered=self.onSave)
        f_save = fileMenu.addAction(actionSave)

        icon = QtGui.QIcon('icons/system-log-out.png')
        actionExit = QtGui.QAction(icon, '&Exit', self, shortcut='CTRL+x',
                statusTip='Exit application', triggered=self.onExit)
        exit = fileMenu.addAction(actionExit)

        toolMenu = menubar.addMenu('&Tools')
        prevMenu = toolMenu.addMenu('Preferences')
        calcMenu = toolMenu.addMenu('Calculator')

        helpMenu = menubar.addMenu('&Help')
        icon = QtGui.QIcon('icons/info.png')

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                statusTip="Show the Qt library's About box",
                triggered=QtGui.qApp.aboutQt)
        qtabout = helpMenu.addAction(self.aboutQtAct)

        actionAbout = QtGui.QAction(icon, '&About', self, shortcut='',
                statusTip='Information about the software and its licensing.',
                triggered=self.onAbout)
        about = helpMenu.addAction(actionAbout)

    def onOpen(self):
        (fname, thefilter) = QtGui.QFileDialog.getOpenFileNameAndFilter(self,
                            'Open file', '.', filter=self.filefilter)
        if not fname: return
        with open(fname, 'r') as f:        
            self.data = f.read()

    def onSave(self):
        (fname, thefilter) = QtGui.QFileDialog.getSaveFileNameAndFilter(self,
                            'Save file', '.', filter=self.filefilter)
        if not fname: return
        with open(fname, 'w') as f:        
            f.write('This test worked for me ...')

    def onExit(self):
        sys.exit(QtGui.qApp.quit())

    def onAbout(self):
        QtGui.QMessageBox.about(self, "About Airfoil Mesher",
                "The <b>Airfoil Mesher</b> software is used for "
                "2D airfoil contour analysis and CFD mesh generation.<br><br>"
                "License: GPL<br><br>"
                "Copyricght (C) 2014 Andreas Ennemoser.")


def main():
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icons/app_image.png'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
