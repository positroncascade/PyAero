# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import PFileSystem
import PSvpMethod
from PSettings import ICONS_S, ICONS_L
import PLogger as logger


class Toolbox(object):

    def __init__(self, parent):
        """Main menus for PyAero functionality.
        Inserted in left pane of splitter window which in turn is the app's
        CentralWidget.

        Args:
            parent (QWidget): MainWindow from PyAero.py
        """
        self.parent = parent

        # create toolbox widget for left side of splitter
        self.toolBox = QtGui.QToolBox()

        # set the style
        style = (""" QToolBox::tab:selected {font: bold; } """)
        self.toolBox.setStyleSheet(style)

        # ******************************************
        # toolbox item1 --> treeview in PFileSystem
        # ******************************************
        item1 = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        item1.setLayout(layout)

        # instance of QFileSystemModel (needs to have a proper parent)
        filesystem = PFileSystem.FileSystem(self.parent)

        # handler
        filesystem.tree.clicked.connect(filesystem.onFileSelected)
        filesystem.tree.doubleClicked.connect(filesystem.onFileLoad)

        layout.addWidget(filesystem.tree, stretch=12)
        # layout.setAlignment(QtCore.Qt.AlignTop)

        self.header = QtGui.QLabel('Loaded airfoil(s)')
        self.header.setEnabled(False)
        layout.addStretch(stretch=2)
        layout.addWidget(self.header)

        self.listwidget = MyListWidget(self.parent)
        self.listwidget.setEnabled(False)
        # allow multiple selections
        self.listwidget.setSelectionMode(QtGui.QAbstractItemView.
                                         ExtendedSelection)
        layout.addWidget(self.listwidget, stretch=5)
        layout.addStretch(stretch=1)

        # ******************************************
        # toolbox item2 --> Aeropython settings
        # ******************************************
        form = QtGui.QFormLayout()

        label1 = QtGui.QLabel(u'Angle of attack (°)')
        self.spin = QtGui.QDoubleSpinBox()
        self.spin.setSingleStep(0.1)
        self.spin.setDecimals(1)
        self.spin.setRange(-10.0, 10.0)
        self.spin.setValue(2.0)
        form.addRow(label1, self.spin)

        label2 = QtGui.QLabel('Freestream velocity (m/s)')
        self.freestream = QtGui.QDoubleSpinBox()
        self.freestream.setSingleStep(0.1)
        self.freestream.setDecimals(2)
        self.freestream.setRange(0.0, 100.0)
        self.freestream.setValue(10.0)
        form.addRow(label2, self.freestream)

        label3 = QtGui.QLabel('Number of panels (-)')
        self.panels = QtGui.QSpinBox()
        self.panels.setRange(10, 500)
        self.panels.setValue(40)
        form.addRow(label3, self.panels)

        runbtn = QtGui.QPushButton('Calculate lift coefficient')
        form.addRow(runbtn)

        item2 = QtGui.QGroupBox('AeroPython Panel Method')
        item2.setLayout(form)

        runbtn.clicked.connect(self.runPanelMethod)

        # ******************************************
        # toolbox item3 --> contour analysis
        # ******************************************
        box = QtGui.QVBoxLayout()

        hlayout = QtGui.QHBoxLayout()
        gb = QtGui.QGroupBox('Select contour to analyse')
        self.b1 = QtGui.QRadioButton('Original')
        self.b2 = QtGui.QRadioButton('Refined')
        self.b1.setChecked(True)
        hlayout.addWidget(self.b1)
        hlayout.addWidget(self.b2)
        gb.setLayout(hlayout)
        box.addWidget(gb)

        hlayout = QtGui.QHBoxLayout()
        self.cgb = QtGui.QGroupBox('Select plot quantity')
        self.cpb1 = QtGui.QRadioButton('Gradient')
        self.cpb2 = QtGui.QRadioButton('Curvature')
        self.cpb3 = QtGui.QRadioButton('Radius of Curvature')
        self.cpb1.setChecked(True)
        hlayout.addWidget(self.cpb1)
        hlayout.addWidget(self.cpb2)
        hlayout.addWidget(self.cpb3)
        self.cgb.setLayout(hlayout)
        self.cgb.setEnabled(False)
        box.addWidget(self.cgb)

        button1 = QtGui.QPushButton('Analyze')
        button1.setGeometry(10, 10, 200, 50)
        box.addWidget(button1)

        box.addStretch(1)

        item3 = QtGui.QWidget()
        item3.setLayout(box)

        button1.clicked.connect(self.analyzeAirfoil)

        # ******************************************
        # toolbox item4 --> Meshing
        # ******************************************

        item4 = QtGui.QWidget()

        # ******************************************
        # toolbox item5 --> viewing options (checkboxes)
        # ******************************************
        item5 = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        item5.setLayout(layout)
        self.cb1 = QtGui.QCheckBox('Message window')
        self.cb1.setChecked(True)
        self.cb2 = QtGui.QCheckBox('Airfoil points')
        self.cb2.setChecked(True)
        self.cb3 = QtGui.QCheckBox('Airfoil spline')
        self.cb3.setChecked(False)
        self.cb3.setDisabled(True)
        self.cb4 = QtGui.QCheckBox('Chord')
        self.cb4.setChecked(True)
        layout.addWidget(self.cb1)
        layout.addWidget(self.cb2)
        layout.addWidget(self.cb3)
        layout.addWidget(self.cb4)
        layout.setAlignment(QtCore.Qt.AlignTop)

        # connect signals to slots
        self.cb1.clicked.connect(self.parent.slots.toggleLogDock)
        self.cb2.clicked.connect(self.toggleRawPoints)
        # self.cb3.clicked.connect()
        self.cb4.clicked.connect(self.toggleChord)

        # ******************************************
        # toolbox item6 --> contour modification
        # ******************************************
        form = QtGui.QFormLayout()

        label = QtGui.QLabel(u'Refinement tolerance (°)')
        self.tolerance = QtGui.QDoubleSpinBox()
        self.tolerance.setSingleStep(0.1)
        self.tolerance.setDecimals(1)
        self.tolerance.setRange(140.0, 175.0)
        self.tolerance.setValue(172.0)
        form.addRow(label, self.tolerance)

        label = QtGui.QLabel('Number points on spline (-)')
        self.spline_points = QtGui.QSpinBox()
        self.spline_points.setRange(50, 500)
        self.spline_points.setValue(150)
        form.addRow(label, self.spline_points)

        button = QtGui.QPushButton('Spline and Refine')
        hbl = QtGui.QHBoxLayout()
        hbl.addStretch(stretch=1)
        hbl.addWidget(button, stretch=4)
        hbl.addStretch(stretch=1)

        box = QtGui.QGroupBox('Airfoil contour refinement settings')
        box.setLayout(form)

        form1 = QtGui.QFormLayout()

        label = QtGui.QLabel(u'Blending length relative to chord (%)')
        self.blending = QtGui.QDoubleSpinBox()
        self.blending.setSingleStep(0.01)
        self.blending.setDecimals(2)
        self.blending.setRange(0.0, 1.0)
        self.blending.setValue(0.3)
        form1.addRow(label, self.blending)

        label = QtGui.QLabel(u'Blending polynomial exponent (-)')
        self.exponent = QtGui.QDoubleSpinBox()
        self.exponent.setSingleStep(0.1)
        self.exponent.setDecimals(1)
        self.exponent.setRange(1.0, 5.0)
        self.exponent.setValue(3.0)
        form1.addRow(label, self.exponent)

        label = QtGui.QLabel(u'Trailing edge thickness relative to chord (%)')
        self.thickness = QtGui.QDoubleSpinBox()
        self.thickness.setSingleStep(0.05)
        self.thickness.setDecimals(2)
        self.thickness.setRange(0.0, 5.0)
        self.thickness.setValue(0.6)
        form1.addRow(label, self.thickness)

        box1 = QtGui.QGroupBox('Airfoil trailing edge settings')
        box1.setLayout(form1)

        button1 = QtGui.QPushButton('Add Trailing Edge')
        hbl1 = QtGui.QHBoxLayout()
        hbl1.addStretch(stretch=1)
        hbl1.addWidget(button1, stretch=4)
        hbl1.addStretch(stretch=1)

        vbl = QtGui.QVBoxLayout()
        vbl.addStretch(1)
        vbl.addWidget(box)
        vbl.addLayout(hbl)
        vbl.addStretch(1)
        vbl.addWidget(box1)
        vbl.addLayout(hbl1)
        vbl.addStretch(10)

        item6 = QtGui.QWidget()
        item6.setLayout(vbl)

        button.clicked.connect(self.modifyAirfoil)

        # ******************************************
        # End of toolbox items
        # ******************************************

        # populate toolbox
        self.tb1 = self.toolBox.addItem(item1, 'Airfoil Database')
        self.tb2 = self.toolBox.addItem(item6, 'Contour Modification')
        self.tb3 = self.toolBox.addItem(item3, 'Contour Analysis')
        self.tb4 = self.toolBox.addItem(item4, 'Meshing')
        self.tb5 = self.toolBox.addItem(item2, 'Aerodynamics')
        self.tb6 = self.toolBox.addItem(item5, 'Viewing options')

        self.toolBox.setItemToolTip(0, 'Airfoil database ' +
                                       '(browse filesystem)')
        self.toolBox.setItemToolTip(1, 'Spline and refine the contour')
        self.toolBox.setItemToolTip(2, 'Analyze the curvature of the ' +
                                       'selected airfoil')
        self.toolBox.setItemToolTip(3, 'Generate a 2D mesh around the ' +
                                       'selected airfoil')
        self.toolBox.setItemToolTip(4, 'Compute panel based aerodynamic ' +
                                    'coefficients')

        self.toolBox.setItemIcon(0, QtGui.QIcon(ICONS_L + 'airfoil.png'))
        self.toolBox.setItemIcon(1, QtGui.QIcon(ICONS_L + 'Pixel editor.png'))
        self.toolBox.setItemIcon(2, QtGui.QIcon(ICONS_L + 'Pixel editor.png'))
        self.toolBox.setItemIcon(3, QtGui.QIcon(ICONS_L + 'mesh.png'))
        self.toolBox.setItemIcon(4, QtGui.QIcon(ICONS_L + 'Fast delivery.png'))
        self.toolBox.setItemIcon(5, QtGui.QIcon(ICONS_L + 'Configuration.png'))

        # preselect airfoil database box
        self.toolBox.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def toggleRawPoints(self):
        """Toggle points of raw airfoil contour (on/off)"""
        for airfoil in self.parent.airfoils:
            if airfoil.markers and airfoil.contour_item.isSelected():
                visible = airfoil.markers.isVisible()
                airfoil.markers.setVisible(not visible)

    @QtCore.pyqtSlot()
    def toggleChord(self):
        """Toggle visibility of the airfoil chord"""
        for airfoil in self.parent.airfoils:
            if airfoil.chord and airfoil.contour_item.isSelected():
                visible = airfoil.chord.isVisible()
                airfoil.chord.setVisible(not visible)

    @QtCore.pyqtSlot()
    def runPanelMethod(self):
        """Gui callback to run AeroPython panel method in module PSvpMethod"""
        if not self.parent.airfoils:
            self.noairfoilWarning('Can\'t run AeroPython')
            return

        x, y = self.parent.airfoil.raw_coordinates

        u_inf = self.freestream.value()
        alpha = self.spin.value()
        npanel = self.panels.value()

        PSvpMethod.runSVP(x, y, u_inf, alpha, npanel)

    @QtCore.pyqtSlot()
    def modifyAirfoil(self):
        pass

    @QtCore.pyqtSlot()
    def analyzeAirfoil(self):
        """Airfoil contour analysis with respect to geometric features"""

        if not self.parent.airfoils:
            self.noairfoilWarning('Can\'t do contour analysis')
            return

        # switch tab and toolbox to contour analysis
        self.parent.centralwidget.tabs.setCurrentIndex(1)
        self.toolBox.setCurrentIndex(1)

        # enable radio buttons for plotting when analysis starts
        self.cgb.setEnabled(True)

        # select plot variable based on radio button state
        plot = 1*self.cpb1.isChecked() + 2*self.cpb2.isChecked() + \
            3*self.cpb3.isChecked()
        # analyse contour
        self.parent.contourview.analyze(self.tolerance.value(),
                                        self.spline_points.value(),
                                        plot)

        # connect signals to slots
        self.cpb1.clicked.connect(lambda:
                                  self.parent.contourview.drawContour(1))
        self.cpb2.clicked.connect(lambda:
                                  self.parent.contourview.drawContour(2))
        self.cpb3.clicked.connect(lambda:
                                  self.parent.contourview.drawContour(3))

    def noairfoilWarning(self, action):
        QtGui.QMessageBox. \
            information(self.parent, 'Information',
                        'No airfoil loaded. %s.' % (action),
                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton,
                        QtGui.QMessageBox.NoButton)
        return


class MyListWidget(QtGui.QListWidget):
    """Subclassing QListWidget in order to be able to catch key press
    events
    """
    def __init__(self, parent):
        super(MyListWidget, self).__init__()
        self.parent = parent

        self.itemClicked.connect(self.handleActivated)

    def keyPressEvent(self, event):

        if event.type() == QtCore.QEvent.KeyPress and \
                           event.matches(QtGui.QKeySequence.Delete):

            items = self.selectedItems()
            for item in items:
                row = self.row(item)
                self.takeItem(row)
                logger.log.info('Deleted: %s' % (item.text()))

        # continue handling key press events which are not
        # catched here, but should be catched elsewhere
        super(MyListWidget, self).keyPressEvent(event)

    # @QtCore.pyqtSlot() commented here because otherewise
    # item is not available
    def handleActivated(self, item):
        name = item.text()
        logger.log.info('Was clicked: %s' % (name))

        for airfoil in self.parent.airfoils:
            airfoil.contour_item.setSelected(False)

        for selecteditem in self.selectedItems():
            for airfoil in self.parent.airfoils:
                if airfoil.name == selecteditem.text():
                    airfoil.contour_item.setSelected(True)
