from PyQt4 import QtGui, QtCore


class HtmlView(QtGui.QWebView):
    """docstring for PHtmLvIEW"""
    def __init__(self, parent):
        super(HtmlView, self).__init__(parent)
        self.parent = parent

    webview = QtGui.QWebView()
    localfile = '.'
    webview.fromLocalFile(localfile)
