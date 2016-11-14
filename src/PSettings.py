# ****************
# PyAero settings
# ****************

# path to PyAero installation
PYAEROPATH = '.'

# set locale
# can be either 'C' or ''
# if string is empty than system default locale is used
# in case of 'C' decimal separator is a dot in spin boxes, etc.
LOCALE = 'C'

# Window style. Possible options are the the results of:
# QtGui.QStyleFactory.keys()
# 'Windows', 'WindowsXP', 'WindowsVista', 'Motif'
# 'CDE', 'Plastique', 'Cleanlooks'
STYLE = 'Windows'

# airfoil chord length
CHORDLENGTH = 1.

# path to icons
ICONS = '../icons/'
ICONS_S = ICONS + '16x16/'
ICONS_L = ICONS + '24x24/'

# path to data (e.g. airfoil coordinate files)
# path can be absolute or relative (to position where starting PyAero)
AIRFOILDATA = '../data'

# default airfoil for fast loading
DEFAULT_CONTOUR = AIRFOILDATA + '/RC_Glider/mh32.dat'

# set the filter for files to be shown in dialogs
DIALOGFILTER = 'Airfoil contour files (*.dat *.txt);;STL files (*.stl)'

# set the filter for files to be shown in the airfoil browser
FILEFILTER = ['*.dat', '*.txt', '*.msh']

# set anchor for zooming
# 'mouse' means zooming wrt to mouse pointer location
# 'center' means zooming wrt to the view center
ZOOMANCHOR = 'mouse'

# visibility of scroolbars in graphicsview (True, False)
SCROLLBARS = False

# background of graphicsview ('solid', 'gradient')
VIEWSTYLE = 'gradient'

# set zoom limits so that scene is always in meaningful size
MINZOOM = 100.0
MAXZOOM = 10000.

# scale increment
SCALEINC = 1.1

# Color for emphasized log messages
LOGCOLOR = '#1763E7'
