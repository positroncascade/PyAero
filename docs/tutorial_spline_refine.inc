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

   Airfoil contour before and after splining

Two functions improve the contour before meshing. After clicking *Spline and Refine* in the respective toolbox function (see :ref:`figure_toolbox_spline_refine_1`), the contour will at first be splined and in a second step refined.

.. _figure_toolbox_spline_refine_1:
.. figure::  images/toolbox_spline_refine_1.png
   :align:   center
   :target:  _images/toolbox_spline_refine_1.png
   :name: toolbox_spline_refine_1

   Toolbox function for specifying spline and refining parameters

The splining is done using B-splines via the Scyipy function :code:`scipy.interpolate.splprep`. This produces a spline representation through the initial (raw) airfoil contour. The number of points on the spline obviously can be set by `Number of points on spline (-)`. Using an equal arc length the respective number of points is distributed homogeneously along the spline. This is the intended behaviour, as it guarantees constant size mesh cells around the airfoil (since the mesh is based on these points). 


.. _figure_splining_raw:
.. figure::  images/splining_raw.png
   :align:   center
   :target:  _images/splining_raw.png
   :name: splining_raw

   Airfoil RG15: Points are as loaded from original file

.. _figure_splining_60pts:
.. figure::  images/splining_60pts.png
   :align:   center
   :target:  _images/splining_60pts.png
   :name: splining_60pts

   Airfoil RG15: Contour after splining with 60 points, no refinements

.. _figure_splining_120pts:
.. figure::  images/splining_120pts.png
   :align:   center
   :target:  _images/splining_120pts.png
   :name: splining_120pts

   Airfoil RG15: Contour after splining with 120 points, no refinements

.. _figure_splining_60pts_ref170:
.. figure::  images/splining_60pts_ref170.png
   :align:   center
   :target:  _images/splining_60pts_ref170.png
   :name: splining_60pts_ref170

   Airfoil RG15: Contour after splining with 60 points, LE refinement 170°

.. _figure_splining_60pts_ref170_TE3:
.. figure::  images/splining_60pts_ref170_TE3.png
   :align:   center
   :target:  _images/splining_60pts_ref170_TE3.png
   :name: splining_60ptsplining_60pts_ref170_TE3s_ref170

   Airfoil RG15: Contour after splining with 60 points, LE and TE refinements

Obviously, at the leading and trailing edges some more care is necessary to produce the required mesh resolution. At the leading edge it is required to resolve the big pressure gradients which are produced by the shape of the airfoil nose.
