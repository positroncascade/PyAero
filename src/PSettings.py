# ****************
# PyAero settings
# ****************

# path to PyAero installation
PYAEROPATH = '.'

# airfoil chord length
# FIXME
# FIXME if e.g. not 100 then zoom etc. in graphicsview is wrong
# FIXME
CHORDLENGTH = 100.0

# path to icons
ICONS = '../icons/'
ICONS_S = ICONS + '16x16/'
ICONS_L = ICONS + '24x24/'

# path to data (e.g. airfoil coordinate files)
# path can be absolute or relative (to position where starting PyAero)
AIRFOILDATA = '../data'

# set the filter for files to be shown in dialogs
DIALOGFILTER = 'Airfoil contour files (*.dat *.txt);;STL files (*.stl)'

# set the filter for files to be shown in the airfoil browser
FILEFILTER = ['*.dat', '*.txt', '*.msh']

# set anchor when zooming (mouse pointer 'mouse' or view center 'center')
ZOOMANCHOR = 'mouse'

# visibility of scroolbars in graphicsview (True, False)
SCROLLBARS = False

# background of graphicsview ('solid', 'gradient')
VIEWSTYLE = 'gradient'

# zoom limits
MINZOOM = 0.01
MAXZOOM = 100

# scale increment
SCALEINC = 1.2
