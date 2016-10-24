# ****************
# PyAero settings
# ****************

# scale factor for airfoil (standardized is size 0-1)
# during saving the chord size specified for the airfoil will be used to get
# the coordinate range in the specs set by the user
AIRFOILSIZE = 100

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

# base64 encoded string representation of gzipped airfoil coordinate file
# MH32 is an airfoil for rc-gliders by Martin Hepperle
MH32_COMPRESSED = '''
H4sICIlqr1IC/21oMzJfY29udG91ci50eHQAZVM7jlRBDIx3TjHSiJCV/5+cgIRTIALE/XNc7p4E
Npmteu2yXbZfj9fzx3eVZ30mP788v/3++efX4/XgT8LfB53fB312R8rB6sCVFIvZ93uy+WINBfZ5
tzgygMVEgZnKBldr8GJPvC+vLmBhWSxUqy8jPDizc+NVuYE1yBY3I380cQKbRQKb+NZrncDe6vve
TQXYNA8uRby1nv6Cg4HNaOsLI+RTNLTYA/2rpa4/EQJ9JZY63wv9yrRlJ14RLzwNHv1Gfs48/ngZ
+mOTo+/aBczE+95q6yEYslgM+cmzt171gB5p1sZLCfKNj30wrR/ju6yfrAR9moerT96r98+88Z0/
vuIfOwmY8xJVS8hYtwRLboj5SCwxswExQ4lD1A6ZOm+IUG7XyveFTJ0goiwvkehbqKPfhK2xM8BL
7KaM81WHYIGGOpedtN0729nJdx0CDfO4WTgUhPP4fAhb++aBXEIYosHpt7lZcRDRfuqgWU1sJPfb
oCBYmpEW10LdnR6tIzrmxi69ymluCum9CpJj0LgsezZy007M3pF12J2TnruTc2dT6b1Lvpjv3b7n
6v/d9V9zm9bCAAQAAA=='''
