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
__version__ = "0.2"
__maintainer__ = 'Andreas Ennemoser'
__email__ = 'andreas.ennemoser@aon.at'
__status__ = 'Prototype'


class MainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.initUI()

        # define extension to be filtered in file dialogs
        self.filefilter = \
            'Airfoil mesh files (*.txt *.msh);;Airfoil contour files (*.dat)'

    def initUI(self):               
  
        # window size, position and title
        self.setGeometry(700, 100, 1200, 900)
        self.setWindowTitle('Airfoil Mesher')    
        self.show()

        # create a status bar
        self.statusbar = self.statusBar()
        self.statusbar.setCursor(QtGui.QCursor(QtCore.Qt.ForbiddenCursor))
        self.statusbar.showMessage('Ready.')
        self.statusbarstyle = 'background-color:rgb(200,200,200); color:green'
        self.statusbar.setStyleSheet(self.statusbarstyle)

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
              
        # Central Widget
        self.setCentralWidget(CentralWidget(self))

    def onOpen(self):
        
        (fname, thefilter) = QtGui.QFileDialog.getOpenFileNameAndFilter(self,
                            'Open file', '.', filter=self.filefilter)
        if not fname: return
        
        with open(fname, 'r') as f:        
            self.data = f.read()

        print self.data

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
                "The <b>Famous Andi's Mesher</b> software is used for "
                "2D airfoil contour analysis and CFD mesh generation.\n\n"
                "The software is distributed as is."
                "License: GPL.")


class Canvas(QtGui.QGraphicsView):

    def __init__(self):
        super(Canvas, self).__init__()

        # set QGraphicsView attributes
        self.setRenderHints(QtGui.QPainter.Antialiasing |
                QtGui.QPainter.SmoothPixmapTransform)
        self.setResizeAnchor(QtGui.QGraphicsView.AnchorViewCenter)
        #self.setDragMode(QtGui.QGraphicsView.NoDrag)
        self.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        self.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))

        self._isPanning = False
        self._mousePressed = False

        # setup scene
        self.scene = QtGui.QGraphicsScene()

        self.text = self.scene.addText('Hello, world!')
        self.text.setPos(0, 0)
        self.text.setFont(QtGui.QFont('Arial', 18))
        # used in order to keep text not flipped by self.scale(1, -1)
        self.text.setFlag(QtGui.QGraphicsItem.ItemIgnoresTransformations, True)

        pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap, QtCore.Qt.MiterJoin)
        brush = QtGui.QBrush(QtCore.Qt.green)
        self.rect1 = self.scene.addRect(-50, -50, 30, 20, pen, brush)

        pen = QtGui.QPen(QtCore.Qt.black, 10, QtCore.Qt.SolidLine,
                QtCore.Qt.RoundCap, QtCore.Qt.MiterJoin)
        brush = QtGui.QBrush(QtCore.Qt.red)
        self.rect2 = self.scene.addRect(50, 50, 300, 200, pen, brush)

        pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(QtCore.Qt.yellow)
        self.scene.addEllipse(0, 0, 5, 5, pen, brush)

        self.width = 100000
        self.height = 100000
        self.scene.setSceneRect(-self.width/2, -self.height/2, self.width, self.height)

        # set background style
        self.canvasstyle = \
            'background-color:QLinearGradient(  \
            x1: 0.0, y1: 0.0, x2: 0.0, y2: 1.0,  \
            stop: 0.3 white,  \
            stop: 1.0 blue); \
            '
        self.setStyleSheet(self.canvasstyle)

        # invert y-coordinates for cartesian coordinate system
        self.scale(1, -1)

        self.setScene(self.scene)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._mousePressed = True
            if self._isPanning:
                QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ClosedHandCursor))
                self._dragPos = event.pos()
                event.accept()
        super(Canvas, self).mousePressEvent(event)            

    def mouseReleaseEvent(self, event):
        self._mousePressed = False
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.viewport().update()
        super(Canvas, self).mouseReleaseEvent(event)            

    def mouseMoveEvent(self, event):
        if self._mousePressed and self._isPanning:
            newPos = event.pos()
            diff = newPos - self._dragPos
            self._dragPos = newPos
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - diff.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - diff.y())
            event.accept()
        else:
            super(Canvas, self).mouseMoveEvent(event)

    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Control and not self._mousePressed:
            self._isPanning = True
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.OpenHandCursor))
        elif key == QtCore.Qt.Key_Plus:
            self.scaleView(1.2)
        elif key == QtCore.Qt.Key_Minus:
            self.scaleView(1 / 1.2)
        elif key == QtCore.Qt.Key_Escape:
            sys.exit(QtGui.qApp.quit())
        else:
            super(Canvas, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Control and not self._mousePressed:
            self._isPanning = False
            QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        else:
            super(Canvas, self).keyPressEvent(event)

    def wheelEvent(self, event):
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
        self.scaleView(math.pow(2.0, -event.delta() / 500.0))

    def scaleView(self, scaleFactor):
        factor = self.matrix().scale(scaleFactor, scaleFactor).mapRect(QtCore.QRectF(0, 0, 1, 1)).width()

        if factor < 0.1 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)


class CentralWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(CentralWidget, self).__init__(parent)

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

        # create Canvas instance for right side of splitter
        self.canvas = Canvas()

        # split main window horizontally into two panes
        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)
        self.splitter.addWidget(self.toolBox)
        self.splitter.addWidget(self.canvas)
        self.splitter.setStretchFactor(0, 1) # 0 ... left pane, 1 ... fraction of split
        self.splitter.setStretchFactor(1, 4) # 1 ... right pane, 4 ... fraction of split

        # put splitter in a layout box
        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)
        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Cleanlooks'))


def main():
    
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icons/app_image.png'))
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
