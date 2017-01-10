#! /usr/bin/env python

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
# import PHtmlView
import PToolBox
from PSettings import VIEWSTYLE, ICONS, LOCALE, STYLE, EXITONESCAPE, \
                      STYLESPECIAL
import PLogger as logger
import PShortCuts

try:
    import PVtkView
    VTK_installed = True
except ImportError:
    VTK_installed = False


__appname__ = 'PyAero'
__author__ = 'Andreas Ennemoser'
__credits__ = 'Internet and open source'
__copyright__ = '2014-' + str(datetime.date.today().strftime("%Y")) + \
                ' ' + __author__
__license__ = 'MIT'
__version__ = '1.0'
__email__ = 'andreas.ennemoser@aon.at'
__status__ = 'Release'


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

        self.airfoils = list()

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
        if VTK_installed:
            self.postview = PVtkView.VtkWindow(self)
        # self.htmlview = PHtmlView.HtmlView(self)

        # create slots (i.e. handlers or callbacks)
        self.slots = PGuiSlots.Slots(self)

        # set central widget for the application
        self.centralwidget = CentralWidget(self)

        self.setCentralWidget(self.centralwidget)

        # add a shortcut for toggling the message window
        sc = PShortCuts.PShortCuts(self)
        sc.addShortcut('ALT+m', 'toggleLogDock')

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
        # self.setGeometry(700, 100, 1200, 900)
        self.showMaximized()
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
        """Catch keypress events in main window

        Args:
            event (QKeyEvent): key event sent to the widget with
            keyboard input focus
        """
        key = event.key()

        if key == QtCore.Qt.Key_Escape and EXITONESCAPE:
            sys.exit(QtGui.qApp.quit())
        elif key == QtCore.Qt.Key_Home:
            # logger.log.info('Home hit in mainwindow')
            self.slots.onViewAll()
        else:
            # progress event
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
        if VTK_installed:
            self.tabs.addTab(self.parent.postview, 'Post Processing')
        # self.tabs.addTab(self.parent.htmlview, 'HTML View')

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
    # main application (contains the main event loop)
    app = QtGui.QApplication(sys.argv)

    # set icon for the application ( upper left window icon and taskbar icon)
    # and add specialization icons per size
    # (needed depending on the operating system)
    app_icon = QtGui.QIcon(ICONS+'app_image.png')
    app_icon.addFile(ICONS+'app_image_16x16.png', QtCore.QSize(16, 16))
    app_icon.addFile(ICONS+'app_image_24x24.png', QtCore.QSize(24, 24))
    app_icon.addFile(ICONS+'app_image_32x32.png', QtCore.QSize(32, 32))
    app_icon.addFile(ICONS+'app_image_48x48.png', QtCore.QSize(48, 48))
    app_icon.addFile(ICONS+'app_image_256x256.png', QtCore.QSize(256, 256))
    app.setWindowIcon(app_icon)

    if LOCALE == 'C':
        # set default local to C, so that decimal separator is a
        # dot in spin boxes, etc.
        QtCore.QLocale.setDefault(QtCore.QLocale.c())

    # window style set in PSettings
    window = MainWindow(STYLE)
    window.show()

    # set application wide attributes
    # access via "QtCore.QCoreApplication.instance().xxx"
    # helps to overcome nested usage of "parent"
    app.mainwindow = window

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
