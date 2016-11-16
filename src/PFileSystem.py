from PyQt4 import QtGui, QtCore

from PSettings import AIRFOILDATA, FILEFILTER, ICONS_L
import PLogger as logger


class FileSystem(QtGui.QFileSystemModel):

    def __init__(self,  parent=None):
        super(FileSystem, self).__init__(parent)

        self.parent = parent

        self.setFilter(QtCore.QDir.AllDirs |
                       QtCore.QDir.Files |
                       QtCore.QDir.NoDotAndDotDot)
        filefilter = QtCore.QStringList(FILEFILTER)
        self.setNameFilters(filefilter)
        # if true, filtered files are shown, but grey
        # if false they are not shown
        self.setNameFilterDisables(False)

        # this path is watched for changes
        self.setRootPath(AIRFOILDATA)

        self.tree = QtGui.QTreeView()
        self.tree.setModel(self)
        # this function sets actual start dir in treeview
        self.tree.setRootIndex(self.index(AIRFOILDATA))
        self.tree.setAnimated(True)

        self.tree.setColumnHidden(1, True)  # hide size column
        self.tree.setColumnHidden(2, True)  # hide type column
        self.tree.setColumnHidden(3, True)  # hide date modified column

        header = self.tree.header()
        header.setResizeMode(QtGui.QHeaderView.ResizeToContents)

    def data(self, index, role):
        """
        This function partly overrides the standard QFileSystemModel data
        function to return custom file and folder icons
        """
        fileInfo = self.getFileInfo(index)[4]

        if role == QtCore.Qt.DecorationRole:
            if fileInfo.isDir():
                return QtGui.QPixmap(ICONS_L + 'Folder.png')
            elif fileInfo.isFile():
                return QtGui.QPixmap(ICONS_L + 'airfoil.png')

        return super(FileSystem, self).data(index, role)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def onFileSelected(self, index):

        return

        fileInfo = self.getFileInfo(index)[4]
        if fileInfo.isDir():
            return
        name = self.getFileInfo(index)[0]
        logger.log.info('<b><font color="#2784CB">%s</b> selected' % (name))

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def onFileLoad(self, index):
        fullname = self.getFileInfo(index)[2]
        fileInfo = self.getFileInfo(index)[4]
        if fileInfo.isDir():
            return
        self.parent.slots.loadAirfoil(fullname, '#')

    def getFileInfo(self, index):
        indexItem = self.index(index.row(), 0, index.parent())
        fileInfo = self.fileInfo(indexItem)
        path = fileInfo.absolutePath()
        name = fileInfo.fileName()
        ext = fileInfo.suffix()
        fullname = fileInfo.absoluteFilePath()
        return [name, path, fullname, ext, fileInfo]
