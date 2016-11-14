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
from PSettings import VIEWSTYLE, ICONS, LOCALE, STYLE
import PLogger as logger


__appname__ = 'PyAero'
__author__ = 'Andreas Ennemoser'
__credits__ = 'Internet and open source'
__copyright__ = '2014-' + str(datetime.date.today().strftime("%Y")) + \
                ' ' + __author__
__license__ = 'MIT'
__version__ = '0.6'
__email__ = 'andreas.ennemoser@aon.at'
__status__ = 'Prototype'


class MainWindow(QtGui.QMainWindow):
    """PyAero's main QT window"""
    # call constructor of MainWindow
    def __init__(self, style, parent=None):
        # call constructor of QMainWindow
        super(MainWindow, self).__init__(parent)

        self.parent = parent

        # to get a list of available styles
        # for style in QtGui.QStyleFactory.keys():
        #     print style
        self.style = style

        QtGui.QApplication.setStyle(QtGui.QStyleFactory.create(style))

        self.airfoil = None

        self.bgview = VIEWSTYLE

        # From the PyQt docs:
        # QGraphicsView can be used to visualize a whole scene, or only parts
        # of it. The visualized area is by default detected automatically when
        # the view is displayed for the first time
        # by calling QGraphicsScene.itemsBoundingRect()
        # To set the visualized area rectangle yourself, you
        # can call setSceneRect().
        self.view = PGraphicsView.GraphicsView(self)
        self.scene = PGraphicsScene.GraphicsScene(self)
        # tell the view on which scene it works on
        self.view.setScene(self.scene)

        # prepare additional views for tabs in right splitter window
        self.contourview = PContourAnalysis.ContourAnalysis(self)
        self.meshingview = PGraphicsView.GraphicsView(self)
        self.postview = PVtkView.VtkWindow(self)

        # create slots (i.e. handlers or callbacks)
        self.slots = PGuiSlots.Slots(self)

        # set central widget for the application
        self.centralwidget = CentralWidget(self)

        # shortcut for message window toggle
        QtGui.QShortcut(QtGui.QKeySequence('Alt+m'), self,
                        self.slots.toggleLogDock)

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

        # show the GUI
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

        self.tabs = QtGui.QTabWidget()
        self.tabs.addTab(self.parent.view, 'Airfoil')
        self.tabs.addTab(self.parent.contourview, 'Contour Analysis')
        self.tabs.addTab(self.parent.meshingview, 'Meshing')
        self.tabs.addTab(self.parent.postview, 'Post Processing')

        # connect tab changed signal to slot
        self.tabs.currentChanged.connect(self.parent.slots.onTabChanged)

        # add Tabs to the right pane of the splitter
        self.splitter.addWidget(self.tabs)

        self.splitter.setSizes([100, 400])  # initial hint for splitter spacing

        # put splitter in a layout box
        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(self.splitter)
        self.setLayout(hbox)


def main():
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(ICONS+'app_image.png'))

    if LOCALE == 'C':
        # set default local to C, so that decimal separator is a
        # dot in spin boxes, etc.
        QtCore.QLocale.setDefault(QtCore.QLocale.c())

    # window style set in PSettings
    window = MainWindow(STYLE)
    window.showMaximized()
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
