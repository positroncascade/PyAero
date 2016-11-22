import sys

from PyQt4 import QtGui, QtCore

import PyAero
import PAirfoil
import PGraphicsTest as gt
import PIconProvider
from PSettings import DIALOGFILTER, AIRFOILDATA, LOGCOLOR, DEFAULT_CONTOUR

import PLogger as logger
from PyQt4.Qt import PYQT_VERSION_STR
from PyQt4.QtCore import QT_VERSION_STR
from sip import SIP_VERSION_STR


class Slots(object):
    """This class handles all callback routines for GUI actions

    PyQt uses signals and slots for GUI events and their respective
    handlers/callbacks.
    """

    def __init__(self, parent):
        """Constructor for Slots class

        Args:
            parent (QMainWindow object): MainWindow which emits signals
        """
        self.parent = parent

    @QtCore.pyqtSlot()
    def onOpen(self):

        dialog = QtGui.QFileDialog()

        provider = PIconProvider.IconProvider()
        dialog.setIconProvider(provider)
        dialog.setNameFilter(DIALOGFILTER)
        dialog.setNameFilterDetailsVisible(True)
        dialog.setDirectory(AIRFOILDATA)
        dialog.setFileMode(QtGui.QFileDialog.ExistingFile)

        # open custom file dialog using custom icons
        if dialog.exec_():
            filename = dialog.selectedFiles()[0]
            selfilter = dialog.selectedFilter()

        try:
            filename
        # do nothing if CANCEL button was pressed
        except NameError:
            return

        if 'stl' in selfilter.toLower():  # method of QString object
            self.parent.postview.readStl(filename)
        else:
            self.loadAirfoil(filename, comment='#')

    @QtCore.pyqtSlot()
    def onOpenPredefined(self):
        self.loadAirfoil(DEFAULT_CONTOUR, comment='#')

    def loadAirfoil(self, filename, comment='#'):
        # FIXME
        # FIXME check for multiple loaded airfoils and how to mange them
        # FIXME

        fileinfo = QtCore.QFileInfo(filename)
        name = fileinfo.fileName()

        self.parent.airfoils.append(PAirfoil.Airfoil(self.parent.scene, name))
        last = len(self.parent.airfoils) - 1
        loaded = self.parent.airfoils[last].readContour(filename, comment)
        self.parent.airfoils[last].addToScene()
        self.fitAirfoilInView(last)

        if loaded:
            logger.log.info('Airfoil <b><font color=%s>' % (LOGCOLOR) + name +
                            '</b> loaded')

            self.parent.centralWidget().tools.header.setEnabled(True)
            self.parent.centralWidget().tools.listwidget.setEnabled(True)
            self.parent.centralWidget().tools.listwidget.addItem(name)

    @QtCore.pyqtSlot()
    def onPredefinedSTL(self):
        self.parent.postview.readStl('data/SATORI.stl')

    @QtCore.pyqtSlot()
    def fitAirfoilInView(self, id):
        # FIXME
        # FIXME move item back to its origin
        # FIXME it could have been moved
        # FIXME because ItemIsMovable in PGraphicsItem does not
        # FIXME get the events or so
        # FIXME
        self.parent.airfoils[id].contour_item.setX(0.0)
        self.parent.airfoils[id].contour_item.setY(0.0)

        dx = 0.05 * self.parent.airfoils[id].contour_item.rect.width()
        rect = self.parent.airfoils[id].contour_item.rect. \
            adjusted(-dx, 0, dx, 0)
        # logger.log.info('Rect Fit Airfoil: %s' % (rect))
        # logger.log.info('View rect: %s' % (self.parent.view.rect()))
        self.parent.view.fitInView(rect, mode=QtCore.Qt.KeepAspectRatio)

        # cache view to be able to keep it during resize
        self.parent.view.getSceneFromView()

    @QtCore.pyqtSlot()
    def onViewAll(self):
        # calculates and returns the bounding rect of all items on the scene
        rect = self.parent.scene.itemsBoundingRect()
        # logger.log.info('Rect FitAll: %s' % (rect))
        self.parent.view.fitInView(rect, mode=QtCore.Qt.KeepAspectRatio)

        # cache view to be able to keep it during resize
        self.parent.view.getSceneFromView()

    @QtCore.pyqtSlot()
    def toggleTestObjects(self):
        if self.parent.testitems:
            gt.deleteTestItems(self.parent.scene)
            logger.log.info('Test items for GraphicsView loaded')
        else:
            gt.addTestItems(self.parent.scene)
            logger.log.info('Test items for GraphicsView removed')
        self.parent.testitems = not self.parent.testitems

    @QtCore.pyqtSlot()
    def onSave(self):
        (fname, thefilter) = QtGui.QFileDialog. \
            getSaveFileNameAndFilter(self.parent,
                                     'Save file', '.', filter=DIALOGFILTER)
        if not fname:
            return

        with open(fname, 'w') as f:
            f.write('This test worked for me ...')

    @QtCore.pyqtSlot()
    def onSaveAs(self):
        (fname, thefilter) = QtGui. \
            QFileDialog.getSaveFileNameAndFilter(
            self.parent, 'Save file as ...', '.',
            filter=DIALOGFILTER)
        if not fname:
            return
        with open(fname, 'w') as f:
            f.write('This test worked for me ...')

    @QtCore.pyqtSlot()
    def onPrint(self):
        dialog = QtGui.QPrintDialog()
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.parent.editor.document().print_(dialog.printer())

    @QtCore.pyqtSlot()
    def onPreview(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)

        preview = QtGui.QPrintPreviewDialog(printer, self.parent)
        preview.paintRequested.connect(self.handlePaintRequest)
        preview.exec_()

    # setup printer for print preview
    def handlePaintRequest(self, printer):
        printer.setOrientation(QtGui.QPrinter.Landscape)
        self.parent.view.render(QtGui.QPainter(printer))

    @QtCore.pyqtSlot()
    def toggleLogDock(self):
        """Switch message log window on/off"""

        sender = self.parent.sender().metaObject().className()

        visible = self.parent.messagedock.isVisible()
        self.parent.messagedock.setVisible(not visible)

        # update the checkbox if toggling is done via keyboard
        if sender == 'QShortcut':
            checkbox = self.parent.centralWidget().tools.cb1
            checkbox.setChecked(not checkbox.isChecked())

    @QtCore.pyqtSlot()
    def onBlockMesh(self):
        pass

    @QtCore.pyqtSlot()
    def removeAirfoil(self):
        """Remove all selected aiorfoils from the scene"""
        for airfoil in self.parent.airfoils:
            self.parent.scene.removeItem(airfoil.contour_item)
            logger.log.info('Airfoil <b><font color=%s>' % (LOGCOLOR) +
                            airfoil.name + '</b> removed')

    @QtCore.pyqtSlot()
    def onMessage(self, msg):
        # move cursor to the end befor writing new message
        # so in case text inside the log window was selected before
        # the new text is pastes correct
        self.parent.messages.moveCursor(QtGui.QTextCursor.End)
        self.parent.messages.insertHtml(msg)

    @QtCore.pyqtSlot()
    def onExit(self):
        sys.exit(QtGui.qApp.quit())

    @QtCore.pyqtSlot()
    def onCalculator(self):
        pass

    @QtCore.pyqtSlot()
    def onBackground(self):
        if self.parent.bgview == 'gradient':
            self.parent.bgview = 'solid'
        else:
            self.parent.bgview = 'gradient'

        self.parent.view.setBackground(self.parent.bgview)

    @QtCore.pyqtSlot()
    def onUndo(self):
        pass

    @QtCore.pyqtSlot()
    def onLevelChanged(self):
        """Change size of message window when floating """
        if self.parent.messagedock.isFloating():
            self.parent.messagedock.resize(700, 300)

    @QtCore.pyqtSlot()
    def onTextChanged(self):
        """Move the scrollbar in the message log-window to the bottom.
        So latest messages are always in the view.
        """
        vbar = self.parent.messages.verticalScrollBar()
        if vbar:
            vbar.triggerAction(QtGui.QAbstractSlider.SliderToMaximum)

    def onTabChanged(self):
        """Sync tabs and toolboxes """
        tab = self.parent.centralwidget.tabs.currentIndex()
        self.parent.centralwidget.tools.toolBox.setCurrentIndex(tab)

    @QtCore.pyqtSlot()
    def onRedo(self):
        pass

    @QtCore.pyqtSlot()
    def onHelp(self):
        pass

    @QtCore.pyqtSlot()
    def onAbout(self):
        QtGui.QMessageBox. \
            about(self.parent, "About " + PyAero.__appname__,
                  "<b>" + PyAero.__appname__ +
                  "</b> is used for "
                  "2D airfoil contour analysis and CFD mesh generation.\
                  <br><br>"
                  "<b>" + PyAero.__appname__ + "</b> code under " +
                  PyAero.__license__ +
                  " license. (c) " +
                  PyAero.__copyright__ + "<br><br>"
                  "email to: " + PyAero.__email__ + "<br>"
                  "Twitter: <a href='http://twitter.com/chiefenne'>\
                  @chiefenne</a><br><br>"
                  "Embedded <b>Aeropython</b> code under MIT license. <br> \
                  (c) 2014 Lorena A. Barba, Olivier Mesnard<br>"
                  "Link to " +
                  "<a href='http://nbviewer.ipython.org/github/" +
                  "barbagroup/AeroPython/blob/master/lessons/" +
                  "11_Lesson11_vortexSourcePanelMethod.ipynb'> \
                  <b>Aeropython</b></a> (iPython notebook)." + "<br><br>"
                  + "<b>VERSIONS:</b>" + "<br>"
                  + PyAero.__appname__ + ": " + PyAero.__version__ +
                  "<br>"
                  + "Python: %s" % (sys.version.split()[0]) + "<br>"
                  + "PyQt: %s" % (PYQT_VERSION_STR) + "<br>"
                  + "Qt: %s" % (QT_VERSION_STR) + "<br>"
                  + "SIP: %s" % (SIP_VERSION_STR)
                  )
