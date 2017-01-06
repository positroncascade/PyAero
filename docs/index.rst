.. |br| raw:: html

   <br />

.. important::
   VERSION 1.0 is released.
   Meshes in AVL-FIRE, SU2, and GMESH formats can be generated now.

.. important::
   At the moment 4 mesh blocks and associated files are generated.
   These need to be connected first, to be able to get the full mesh.
   Meshes are not yet visualized in PyAero.
   Coming soon.

********************
PyAero documentation
********************

PyAero is an airfoil contour analysis and CFD meshing tool written in Python. |br| 
PyAero is open-source and distributed under the MIT license, see `LICENSE <license.html>`_. |br|

.. figure::  images/gui_airfoil.png
   :align:   center
   :target:  _images/gui_airfoil.png
   :name: GUI

   PyAero user interface at a glance

.. figure::  images/RG15_mesh_part.png
   :align:   center
   :target:  _images/RG15_mesh_part.png
   :name: GUI

   Example mesh around RG15 airfoil (3rd mesh dimension 1 layer)

Features
========

 - Load and display airfoil contour files
 - Airfoil splining and refining
 
   - Prepare contour for meshing
   - Splining is done to get a smooth contour and sufficient contour points
   - Refining allows to improve leading and trailing edge resolution
 
 - Airfoil contour analysis
 
   - Analyze gradient, curvature, and curvature circle at the leading edge
 
 - Trailing edge generation
 
   - Specification of the trailing edge thickness
   - Smart blending functions (arbitrary polynomial)
   - Independent blending for upper and lower contour (e.g. for strong cambered airfoils)
 
 - Automatic generation of block-strcuctured meshes for airfoils
 
   - Currently only single element C-type meshes are supported
 
 - Mesh control
 
   - Boundary layer region
   - Wake region
   - Windtunnel
 
 - Mesh export
 
   - `AVL FIRE <http://www.avl.com/fire-m>`_ (*.flma)
   - `SU2 <http://su2.stanford.edu/>`_ (*.su2)
   - `GMESH <http://gmsh.info>`_ (*.msh)
 
 - Simple aerodynamic analysis, i.e. panel methods
 
   - `AeroPython <http://nbviewer.ipython.org/github/barbagroup/AeroPython/blob/master/lessons/11_Lesson11_vortexSourcePanelMethod.ipynb>`_


Quickstart (for the impatient)
==============================
Goto chapter :ref:`quickstart`.

Code repository
===============

The code ist hosted on GitHub: `PyAero source code <https://github.com/chiefenne/PyAero>`_

.. toctree::
   :hidden:

   Home <self>

.. toctree::
   :caption: Table of Contents
   :numbered:
   :maxdepth: 3
   :hidden:

   introduction
   ui_GUI
   tutorial
   dependencies
   license
