.. |br| raw:: html

   <br />

.. important::
   VERSION 1.0 is released.
   Meshes in AVL-FIRE and SU2 format can be generated now.
   The documentation needs to be updated.

.. important::
   At the moment 4 mesh blocks and associated files are generated.
   These need to be connected first, to be able to get the full mesh.
   An update shall come soon.

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

 - Load and display airfoil contour files (different formats are recognized)
 - Airfoil contour analysis, refining and splining
 - Trailing edge generation including smart blending functions
 - Automatic generation of block-strcuctured meshes for airfoils (C-type)
 - Mesh control (specifically in the boundary layer region) and smoothing
 - Automatic definition of boundary faces
 - Mesh export (AVL FIRE .flma, SU2 .su2)
 - Simple aerodynamic analysis, i.e. panel methods
 - Advanced aerodynamic analysis, i.e. linking to open source CFD software
 - More to come :)

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
