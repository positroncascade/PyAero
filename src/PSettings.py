# ****************
# PyAero settings
# ****************

# scale factor for airfoil (standardized is size 0-1)
# during saving the chord size specified for the airfoil will be used to get
# the coordinate range in the specs set by the user
AIRFOILSIZE = 100

# path to icons
ICONS = '../icons/'
ICONS_S = 'ICONS/16x16/'
ICONS_L = 'ICONS/24x24/'

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
