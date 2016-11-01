# -*- coding: utf-8 -*-

from PyQt4 import QtGui, QtCore
import PFileSystem
import PSvpMethod


class Toolbox(object):
    # call constructor of toolbox

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

        # ******************************************
        # toolbox item1 --> treeview in PFileSystem
        # ******************************************
        item1 = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        item1.setLayout(layout)

        # instance of QFileSystemModel (needs to have a proper parent)
        self.filesystem = PFileSystem.FileSystem(self.parent)

        # handler
        self.filesystem.tree.clicked.connect(self.filesystem.onFileSelected)
        self.filesystem.tree.doubleClicked.connect(self.filesystem.onFileLoad)

        layout.addWidget(self.filesystem.tree)
        layout.setAlignment(QtCore.Qt.AlignTop)

        # ******************************************
        # toolbox item2
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
        # toolbox item3
        # ******************************************
        form3 = QtGui.QFormLayout()

        label4 = QtGui.QLabel(u'Refinement tolerance (°)')
        self.tolerance = QtGui.QDoubleSpinBox()
        self.tolerance.setSingleStep(0.1)
        self.tolerance.setDecimals(1)
        self.tolerance.setRange(160.0, 175.0)
        self.tolerance.setValue(169.0)
        form3.addRow(label4, self.tolerance)

        label5 = QtGui.QLabel('Number points on spline (-)')
        self.spline_points = QtGui.QSpinBox()
        self.spline_points.setRange(30, 1000)
        self.spline_points.setValue(300)
        form3.addRow(label5, self.spline_points)

        button1 = QtGui.QPushButton('Contour analysis')
        button1.setGeometry(10, 10, 200, 50)
        form3.addRow(button1)

        item3 = QtGui.QGroupBox('Airfoil contour options')
        item3.setLayout(form3)

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
        self.cb2.setChecked(False)
        self.cb3 = QtGui.QCheckBox('Airfoil spline')
        self.cb3.setChecked(False)
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
        self.cb4.clicked.connect(self.toggleChord)

        # populate toolbox
        self.tab1 = self.toolBox.addItem(item1, 'Airfoil Database')
        self.tab2 = self.toolBox.addItem(item2, 'Aerodynamics')
        self.tab3 = self.toolBox.addItem(item3, 'Contour Analysis')
        self.tab4 = self.toolBox.addItem(item4, 'Meshing')
        self.tab5 = self.toolBox.addItem(item5, 'Viewing options')

        self.toolBox.setItemToolTip(0, 'Create a report summarizing \
                                        available information')

        icon = QtGui.QIcon('icons/16x16/Items.png')
        self.toolBox.setItemIcon(0, icon)

        icon = QtGui.QIcon('icons/24x24/Fast delivery.png')
        self.toolBox.setItemIcon(1, icon)

        icon = QtGui.QIcon('icons/24x24/Book.png')
        self.toolBox.setItemIcon(2, icon)

        icon = QtGui.QIcon('icons/24x24/Mesh.png')
        self.toolBox.setItemIcon(4, icon)

        icon = QtGui.QIcon('icons/24x24/Search.png')
        self.toolBox.setItemIcon(4, icon)

        self.toolBox.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def toggleRawPoints(self):
        """Toggle points from raw airfoil contour (on/off)"""
        pass

    @QtCore.pyqtSlot()
    def toggleChord(self):
        """Toggle visibility of the airfoil chord"""
        if self.parent.airfoil.chord:
            visible = self.parent.airfoil.chord.isVisible()
            self.parent.airfoil.chord.setVisible(not visible)

    @QtCore.pyqtSlot()
    def runPanelMethod(self):
        """Gui callback to run AeroPython panel method in module PSvpMethod"""
        if not self.parent.airfoil:
            self.noairfoilWarning('Can\'t run AeroPython')
            return

        x = list()
        y = list()
        for point in self.parent.airfoil.raw_coordinates:
            x.append(QtCore.QPointF(point).x())
            y.append(QtCore.QPointF(point).y())

        u_inf = self.freestream.value()
        alpha = self.spin.value()
        npanel = self.panels.value()

        PSvpMethod.runSVP(x, y, u_inf, alpha, npanel)

    @QtCore.pyqtSlot()
    def analyzeAirfoil(self):
        """Do airfoil contour analysis with respect to geometric features"""
        if not self.parent.airfoil:
            self.noairfoilWarning('Can\'t do contour analysis')
            return

        # switch tab to contour analysis
        self.parent.centralwidget.tabs.setCurrentIndex(1)

        tolerance = self.tolerance.value()
        points = self.spline_points.value()
        self.parent.contourview.analyze(tolerance, points)

    def noairfoilWarning(self, action):
        QtGui.QMessageBox. \
            information(self.parent, 'Information',
                        'No airfoil loaded. Can\'t do %s.' % (action),
                        QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton,
                        QtGui.QMessageBox.NoButton)
        return
