#!c:/python27/python

"""
PyAero is an airfoil CFD meshing (2D) and contour analysis tool.

The meshing tool provides features to be able to create 2D CFD meshes
for numerical airfoil analysis (virtual wind tunnel).

The purpose of the contour analysis tool is to be able to read airfoil contour
data and analyze them with respect to smoothness and similar properties.
Functions allow splining, refinement, smoothing, etc. in order to provide
accurate input to the subsequent meshing process.
"""

import sys
import datetime

from PyQt4 import QtGui, QtCore

import PMenusTools as GUI
import PGraphicsView
import PGraphicsScene
import PContourAnalysis
import PGuiSlots
import PVtkView
import PToolBox
from PSettings import *
import PLogger as logger


__appname__ = 'PyAero'
__author__ = 'Andreas Ennemoser'
__credits__ = 'Stackoverflow and its contributors'
__copyright__ = '2014-' + str(datetime.date.today().strftime("%Y")) + \
                ' ' + __author__
__license__ = 'MIT'
__version__ = '0.5.1'
__email__ = 'andreas.ennemoser@gmail.com'
__status__ = 'Prototype'


class MainWindow(QtGui.QMainWindow):
    """PyAero's main QT window"""
    # call constructor of MainWindow
    def __init__(self, parent=None):
        # call constructor of QMainWindow
        super(MainWindow, self).__init__(parent)

        self.parent = parent

        self.kit = ['Windows', 'WindowsXP', 'WindowsVista', 'Motif',
                    'CDE', 'Plastique', 'Cleanlooks']
        # QtGui.QApplication.setStyle(QtGui.QStyleFactory.create(self.kit[2]))

        self.airfoil = None

        self.bgview = VIEWSTYLE

        self.view = PGraphicsView.GraphicsView(self)
        self.scene = PGraphicsScene.GraphicsScene(self)
        self.view.setScene(self.scene)

        # prepare additional views for tabs in right splitter window
        self.contourview = PContourAnalysis.Contour(self)
        self.meshingview = PGraphicsView.GraphicsView(self)
        self.postview = PVtkView.VtkWindow(self)

        # create slots (i.e. handlers or callbacks)
        self.slots = PGuiSlots.Slots(self)

        # set central widget for the application
        self.centralwidget = CentralWidget(self)
        self.setCentralWidget(self.centralwidget)

        # setup user interface and menus
        self.initUI()

        # prepare logger so that it logs to
        # dock message window using HTML strings
        # messageWritten emits a signal including the message
        logger.LogStream.stdout().messageWritten.connect(self.slots.onMessage)
        logger.LogStream.stderr().messageWritten.connect(self.slots.onMessage)

        # toggle for graphics test items (CTRL+t)
        self.testitems = False

    def initUI(self):

        # window size, position and title
        self.setGeometry(700, 100, 1200, 900)
        self.setWindowTitle(__appname__ +
                            ' - Airfoil Contour Analysis and CFD Meshing')

        # create widgets of main window
        gui = GUI.MenusTools(self)
        gui.createMenus()
        gui.createTools()
        gui.createStatusBar()
        gui.createDocks()

        # show the GUI :)
        self.show()

    # ********************************
    # slots which are not in PGuiSlots
    # ********************************

    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Escape:
            sys.exit(QtGui.qApp.quit())
        else:
            # handle event
            super(MainWindow, self).keyPressEvent(event)


class CentralWidget(QtGui.QWidget):
    # call constructor of CentralWidget
    def __init__(self, parent=None):
        # call constructor of QWidget
        super(CentralWidget, self).__init__(parent)

        self.parent = parent

        # split main window horizontally into two panes
        self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

        # add QToolBox widget to the left pane
        self.tools = PToolBox.Toolbox(self.parent)
        self.splitter.addWidget(self.tools.toolBox)

        # add QGraphicsView widget to the right pane
        self.tabs = QtGui.QTabWidget()

        self.tabs.addTab(self.parent.view, 'Airfoil')
        self.tabs.addTab(self.parent.contourview, 'Contour Analysis')
        self.tabs.addTab(self.parent.meshingview, 'Meshing')
        self.tabs.addTab(self.parent.postview, 'Post Processing')

        # connect tab changed signal to slot
        self.tabs.currentChanged.connect(self.parent.slots.onTabChanged)

        self.splitter.addWidget(self.tabs)

        self.splitter.setSizes([100, 400])  # initial hint for splitter spacing

        # put splitter in a layout box
        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)


def main():
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(ICONS+'app_image.png'))

    window = MainWindow()
    window.showMaximized()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
