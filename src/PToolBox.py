# -*- coding: utf-8 -*-

import os

from PyQt4 import QtGui, QtCore
import PFileSystem
import PIconProvider
import PSvpMethod
import PSplineRefine
import PTrailingEdge
import PMeshing
from PSettings import ICONS_L, DIALOGFILTER, OUTPUTDATA
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

        self.listwidget = ListWidget(self.parent)
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
        self.spin.setValue(0.0)
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
        form = QtGui.QFormLayout()

        label = QtGui.QLabel(u'Gridpoints along airfoil')
        points_on_airfoil = 100
        text = QtGui.QLineEdit(str(points_on_airfoil))
        text.setEnabled(False)
        form.addRow(label, text)

        label = QtGui.QLabel(u'Gridpoints normal to airfoil')
        self.points_n = QtGui.QSpinBox()
        self.points_n.setSingleStep(1)
        self.points_n.setRange(1, 200)
        self.points_n.setValue(15)
        form.addRow(label, self.points_n)

        label = QtGui.QLabel('Thickness normal to Airfoil (%)')
        label.setToolTip('The thickness is specified wrt to the unit chord')
        self.normal_thickness = QtGui.QDoubleSpinBox()
        self.normal_thickness.setSingleStep(0.1)
        self.normal_thickness.setRange(1., 10.)
        self.normal_thickness.setValue(4.0)
        self.normal_thickness.setDecimals(1)
        form.addRow(label, self.normal_thickness)

        label = QtGui.QLabel('Cell Thickness ratio (-)')
        label.setToolTip('Thickness of the last cell vs. the first cell in ' +
                         'the airfoil mesh block' +
                         '\nThe first cell is the one attached to the airfoil')
        self.ratio = QtGui.QDoubleSpinBox()
        self.ratio.setSingleStep(0.1)
        self.ratio.setRange(1., 10.)
        self.ratio.setValue(3.0)
        self.ratio.setDecimals(1)
        form.addRow(label, self.ratio)

        label = QtGui.QLabel(u'Gridpoints at trailing edge')
        self.te_div = QtGui.QSpinBox()
        self.te_div.setSingleStep(1)
        self.te_div.setRange(1, 20)
        self.te_div.setValue(3)
        form.addRow(label, self.te_div)

        label = QtGui.QLabel(u'Gridpoints downstream trailing edge')
        self.points_te = QtGui.QSpinBox()
        self.points_te.setSingleStep(1)
        self.points_te.setRange(1, 100)
        self.points_te.setValue(6)
        form.addRow(label, self.points_te)

        label = QtGui.QLabel('Length behing trailing edge (%)')
        label.setToolTip('The length is specified wrt to the unit chord')
        self.length_te = QtGui.QDoubleSpinBox()
        self.length_te.setSingleStep(0.1)
        self.length_te.setRange(0.1, 30.)
        self.length_te.setValue(4.0)
        self.length_te.setDecimals(1)
        form.addRow(label, self.length_te)

        label = QtGui.QLabel('Cell Thickness ratio (-)')
        label.setToolTip('Thickness of the last cell vs. the first cell in ' +
                         'the trailing edge mesh block' + '\n'
                         'The first cell is the one attached to the airfoil ' +
                         'trailing edge')
        self.ratio_te = QtGui.QDoubleSpinBox()
        self.ratio_te.setSingleStep(0.1)
        self.ratio_te.setRange(1., 10.)
        self.ratio_te.setValue(3.0)
        self.ratio_te.setDecimals(1)
        form.addRow(label, self.ratio_te)

        button = QtGui.QPushButton('Create Mesh')
        hbl = QtGui.QHBoxLayout()
        hbl.addStretch(stretch=1)
        hbl.addWidget(button, stretch=4)
        hbl.addStretch(stretch=1)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(form)
        vbox.addLayout(hbl)
        box = QtGui.QGroupBox('Airfoil contour meshing')
        box.setLayout(vbox)

        vbl = QtGui.QVBoxLayout()
        vbl.addStretch(1)
        vbl.addWidget(box)
        vbl.addStretch(15)

        item4 = QtGui.QWidget()
        item4.setLayout(vbl)

        button.clicked.connect(self.makeMesh)

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
        self.cb3.setChecked(True)
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
        self.cb3.clicked.connect(self.toggleSpline)
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
        self.tolerance.setValue(169.0)
        form.addRow(label, self.tolerance)

        label = QtGui.QLabel('Number points on spline (-)')
        self.points = QtGui.QSpinBox()
        self.points.setRange(50, 500)
        self.points.setValue(150)
        form.addRow(label, self.points)

        button = QtGui.QPushButton('Spline and Refine')
        hbl = QtGui.QHBoxLayout()
        hbl.addStretch(stretch=1)
        hbl.addWidget(button, stretch=4)
        hbl.addStretch(stretch=1)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(form)
        vbox.addLayout(hbl)
        box = QtGui.QGroupBox('Airfoil contour refinement')
        box.setLayout(vbox)

        form1 = QtGui.QFormLayout()

        label = QtGui.QLabel(u'Upper side blending length (%)')
        self.blend_u = QtGui.QDoubleSpinBox()
        self.blend_u.setSingleStep(1.0)
        self.blend_u.setDecimals(1)
        self.blend_u.setRange(5.0, 100.0)
        self.blend_u.setValue(30.0)
        form1.addRow(label, self.blend_u)
        label = QtGui.QLabel(u'Lower side blending length (%)')
        self.blend_l = QtGui.QDoubleSpinBox()
        self.blend_l.setSingleStep(1.0)
        self.blend_l.setDecimals(1)
        self.blend_l.setRange(5.0, 100.0)
        self.blend_l.setValue(30.0)
        form1.addRow(label, self.blend_l)

        label = QtGui.QLabel(u'Upper blending polynomial exponent (-)')
        self.exponent_u = QtGui.QDoubleSpinBox()
        self.exponent_u.setSingleStep(0.1)
        self.exponent_u.setDecimals(1)
        self.exponent_u.setRange(1.0, 5.0)
        self.exponent_u.setValue(3.0)
        form1.addRow(label, self.exponent_u)
        label = QtGui.QLabel(u'Lower blending polynomial exponent (-)')
        self.exponent_l = QtGui.QDoubleSpinBox()
        self.exponent_l.setSingleStep(0.1)
        self.exponent_l.setDecimals(1)
        self.exponent_l.setRange(1.0, 5.0)
        self.exponent_l.setValue(3.0)
        form1.addRow(label, self.exponent_l)

        label = QtGui.QLabel(u'Trailing edge thickness relative to chord (%)')
        self.thickness = QtGui.QDoubleSpinBox()
        self.thickness.setSingleStep(0.05)
        self.thickness.setDecimals(2)
        self.thickness.setRange(0.0, 10.0)
        self.thickness.setValue(0.4)
        form1.addRow(label, self.thickness)

        button1 = QtGui.QPushButton('Add Trailing Edge')
        hbl1 = QtGui.QHBoxLayout()
        hbl1.addStretch(stretch=1)
        hbl1.addWidget(button1, stretch=4)
        hbl1.addStretch(stretch=1)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(form1)
        vbox.addLayout(hbl1)
        box1 = QtGui.QGroupBox('Airfoil trailing edge')
        box1.setLayout(vbox)

        # export menu
        name = ''
        hbox = QtGui.QHBoxLayout()
        lbl = QtGui.QLabel('Filename')
        self.lineedit = QtGui.QLineEdit(name)
        btn = QtGui.QPushButton('Browse')
        hbox.addWidget(lbl)
        hbox.addWidget(self.lineedit)
        hbox.addWidget(btn)

        box2 = QtGui.QGroupBox('Export modified contour')
        box2.setLayout(hbox)

        vbl = QtGui.QVBoxLayout()
        vbl.addStretch(1)
        vbl.addWidget(box)
        vbl.addStretch(1)
        vbl.addWidget(box1)
        vbl.addStretch(1)
        vbl.addWidget(box2)
        vbl.addStretch(10)

        item6 = QtGui.QWidget()
        item6.setLayout(vbl)

        button.clicked.connect(self.spline_and_refine)
        button1.clicked.connect(self.makeTrailingEdge)
        button.clicked.connect(self.updatename)
        button1.clicked.connect(self.updatename)
        btn.clicked.connect(self.onBrowse)

        # ******************************************
        # toolbox item7 --> Bokeh test
        # ******************************************
        # layout = QtGui.QBoxLayout()
        # layout.addWidget(webview)
        # item7 = QtGui.QWidget()
        # item7.setLayout(layout)

        # ******************************************
        # End of toolbox items
        # ******************************************

        # populate toolbox
        self.tb1 = self.toolBox.addItem(item1, 'Airfoil Database')
        self.tb2 = self.toolBox.addItem(item6,
                                        'Contour Splining and Refinement')
        self.tb4 = self.toolBox.addItem(item4, 'Meshing')
        self.tb5 = self.toolBox.addItem(item2, 'Aerodynamics')
        self.tb3 = self.toolBox.addItem(item3, 'Contour Analysis')
        self.tb6 = self.toolBox.addItem(item5, 'Viewing options')

        self.toolBox.setItemToolTip(0, 'Airfoil database ' +
                                       '(browse filesystem)')
        self.toolBox.setItemToolTip(1, 'Spline and refine the contour')
        self.toolBox.setItemToolTip(2, 'Generate a 2D mesh around the ' +
                                       'selected airfoil')
        self.toolBox.setItemToolTip(3, 'Compute panel based aerodynamic ' +
                                    'coefficients')
        self.toolBox.setItemToolTip(4, 'Analyze the curvature of the ' +
                                       'selected airfoil')

        self.toolBox.setItemIcon(0, QtGui.QIcon(ICONS_L + 'airfoil.png'))
        self.toolBox.setItemIcon(1, QtGui.QIcon(ICONS_L + 'Pixel editor.png'))
        self.toolBox.setItemIcon(2, QtGui.QIcon(ICONS_L + 'mesh.png'))
        self.toolBox.setItemIcon(3, QtGui.QIcon(ICONS_L + 'Fast delivery.png'))
        self.toolBox.setItemIcon(4, QtGui.QIcon(ICONS_L + 'Pixel editor.png'))
        self.toolBox.setItemIcon(5, QtGui.QIcon(ICONS_L + 'Configuration.png'))

        # preselect airfoil database box
        self.toolBox.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def toggleRawPoints(self):
        """Toggle points of raw airfoil contour (on/off)"""
        for airfoil in self.parent.airfoils:
            if hasattr(airfoil, 'markers') and airfoil.contour_item.isSelected():
                visible = airfoil.markers.isVisible()
                airfoil.markers.setVisible(not visible)

    @QtCore.pyqtSlot()
    def toggleSpline(self):
        for airfoil in self.parent.airfoils:
            if airfoil.contour_item.isSelected():
                visible = airfoil.contourspline_item.isVisible()
                airfoil.contourspline_item.setVisible(not visible)

    @QtCore.pyqtSlot()
    def toggleChord(self):
        """Toggle visibility of the airfoil chord"""
        for airfoil in self.parent.airfoils:
            if hasattr(airfoil, 'chord') and airfoil.contour_item.isSelected():
                visible = airfoil.chord.isVisible()
                airfoil.chord.setVisible(not visible)

    @QtCore.pyqtSlot()
    def runPanelMethod(self):
        """Gui callback to run AeroPython panel method in module PSvpMethod"""
        if not self.parent.airfoils:
            self.noairfoilWarning('Can\'t run AeroPython')
            return

        for airfoil in self.parent.airfoils:
            if airfoil.contour_item.isSelected():

                x, y = airfoil.raw_coordinates
                u_inf = self.freestream.value()
                alpha = self.spin.value()
                panels = self.panels.value()
                PSvpMethod.runSVP(airfoil.name, x, y, u_inf, alpha, panels)

    @QtCore.pyqtSlot()
    def spline_and_refine(self):
        """Spline and refine airfoil"""

        if not self.parent.airfoils:
            self.noairfoilWarning('Can\'t do splining and refining')
            return

        for airfoil in self.parent.airfoils:
            if airfoil.contour_item.isSelected():
                id = self.parent.airfoils.index(airfoil)

                refine = PSplineRefine.SplineRefine(id)
                refine.doSplineRefine(tolerance=self.tolerance.value(),
                                      points=self.points.value())

    @QtCore.pyqtSlot()
    def makeTrailingEdge(self):

        if not self.parent.airfoils:
            self.noairfoilWarning('Can\'t make trailing edge')
            return

        for airfoil in self.parent.airfoils:
            if airfoil.contour_item.isSelected():
                # check if splining already available
                if not hasattr(airfoil, 'spline_data'):
                    QtGui.QMessageBox. \
                        information(self.parent, 'Information',
                                    'Splining needs to be done first. %s.' %
                                    ('Can\'t make trailing edge'),
                                    QtGui.QMessageBox.Ok,
                                    QtGui.QMessageBox.NoButton,
                                    QtGui.QMessageBox.NoButton)
                    return

                id = self.parent.airfoils.index(airfoil)

                trailing = PTrailingEdge.TrailingEdge(id)
                trailing.trailingEdge(blend=self.blend_u.value()/100.0,
                                      ex=self.exponent_u.value(),
                                      thickness=self.thickness.value(),
                                      side='upper')
                trailing.trailingEdge(blend=self.blend_l.value()/100.0,
                                      ex=self.exponent_l.value(),
                                      thickness=self.thickness.value(),
                                      side='lower')

    @QtCore.pyqtSlot()
    def makeMesh(self):

        for airfoil in self.parent.airfoils:
            if airfoil.contour_item.isSelected():
                contour = airfoil.spline_data[0]
                name = airfoil.name
                break

        tunnel = PMeshing.Windtunnel()
        block_airfoil = \
            tunnel.AirfoilMesh(name='block_airfoil',
                               contour=contour,
                               divisions=self.points_n.value(),
                               ratio=self.ratio.value(),
                               thickness=self.normal_thickness.value()/100.0)

        block_te = \
            tunnel.TrailingEdgeMesh(block_airfoil, name='block_TE',
                                    te_divisions=self.te_div.value(),
                                    length=self.length_te.value()/100.0,
                                    divisions=self.points_te.value(),
                                    ratio=self.ratio_te.value())

        block_airfoil.writeFLMA(airfoil=name, depth=0.2)
        block_te.writeFLMA(airfoil=name, depth=0.2)

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
        self.parent.contourview.analyze(plot)

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

    @QtCore.pyqtSlot()
    def updatename(self):
        for airfoil in self.parent.airfoils:
            if airfoil.contour_item.isSelected():
                name = airfoil.name
                break

        sending_button = self.parent.sender()
        nameroot, extension = os.path.splitext(str(name))

        if 'Spline' in sending_button.text():
            nameroot += '_Spline'
            self.lineedit.setText(nameroot + extension)
        if 'Trailing' in sending_button.text():
            nameroot += '_Spline_TE'
            self.lineedit.setText(nameroot + extension)

    def onBrowse(self):

        dialog = QtGui.QFileDialog()

        provider = PIconProvider.IconProvider()
        dialog.setIconProvider(provider)
        dialog.setNameFilter(DIALOGFILTER)
        dialog.setNameFilterDetailsVisible(True)
        dialog.setDirectory(OUTPUTDATA)
        # allow only to select one file
        dialog.setFileMode(QtGui.QFileDialog.AnyFile)
        # display also size and date
        dialog.setViewMode(QtGui.QFileDialog.Detail)
        # make it a save dialog
        dialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
        # put default name in the save dialog
        dialog.selectFile(self.lineedit.text())

        # open custom file dialog using custom icons
        if dialog.exec_():
            names = dialog.selectedFiles()
            # filter = dialog.selectedFilter()

        if not names:
            return

        # names is a list of QStrings
        filename = str(names[0])

        # get coordinates of modified contour
        for airfoil in self.parent.airfoils:
            if airfoil.contour_item.isSelected():
                x, y = airfoil.spline_data[0]

        with open(filename, 'w') as f:
            f.write('#\n')
            f.write('# Derived from:     %s\n' % (str(airfoil.name)))
            f.write('# Number of points: %s\n' % (len(x)))
            f.write('#\n')
            for i, xx in enumerate(x):
                f.write(2*'{:10.6f}'.format(x[i], y[i]) + '\n')


class ListWidget(QtGui.QListWidget):
    """Subclassing QListWidget in order to be able to catch key press
    events
    """
    def __init__(self, parent):
        super(ListWidget, self).__init__()
        self.parent = parent

        self.itemClicked.connect(self.handleActivated)

    def keyPressEvent(self, event):
        key = event.key()

        if key == QtCore.Qt.Key_Delete:
            items = self.selectedItems()
            for item in items:
                row = self.row(item)
                self.takeItem(row)
                delete = False
                for airfoil in self.parent.airfoils:
                    if item.text() == airfoil.name:
                        delete = True
                        break
                if delete:
                    self.parent.slots.removeAirfoil()

        # call original implementation of QListWidget keyPressEvent handler
        super(ListWidget, self).keyPressEvent(event)

    # @QtCore.pyqtSlot() commented here because otherewise
    # "item" is not available
    def handleActivated(self, item):

        for airfoil in self.parent.airfoils:
            airfoil.contour_item.setSelected(False)

        for selecteditem in self.selectedItems():
            for airfoil in self.parent.airfoils:
                if airfoil.name == selecteditem.text():
                    airfoil.contour_item.setSelected(True)
