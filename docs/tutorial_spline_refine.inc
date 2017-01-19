Splining and Refining Airfoil Contours
--------------------------------------

The meshing process in `PyAero <index.html>`_ relies on the point distribution on the airfoil contour. During meshing, there is a mesh constructed around the airfoil, which consists of mesh lines perpendicular to the airfoil contour. These lines are starting at the individual airfoil contour points. So in order to be able to generate a proper mesh, the contour point distribution has to be adapted first. This is important, because in particular old wing sections are specified via a quite coarse resolution. In the figure below, there is an animation of:

- the original airfoil contour
- the splined airfoil contour
- and the mesh lines parting from the splined contour

.. _figure_splining_animated_new:
.. figure::  images/splining_animated_new.gif
   :align:   center
   :target:  _images/splining_animated_new.gif
   :name: splining_animated_new
