```diff
- Heavy coding ongoing. The meshing kernel is ready but not yet implemented in the GUI.
+ The user interface is ready. Usability is satisfactory for me.
```

# PyAero
> PyAero is an open-source airfoil contour analysis and CFD meshing tool written in Python.

![](docs/images/gui_airfoil.png)
<p align="center">PyAero GUI at a glance</p>

![](docs/images/RG15_mesh_part.png)
<p align="center">Example mesh as used in the AVL-FIRE CFD code. Third mesh dimension in 2D is 1 cell layer.</p>

## Features

 - Airfoil contour analysis, refining and splining
 - Trailing edge generation
 - Automatic generation of block-strcuctured meshes for airfoils
 - Mesh control and smoothing
 - Automatic definition of boundary faces
 - Mesh export (AVL FIRE .flm, SU2 .su2)
 - Simple aerodynamic analysis, i.e. panel methods
 - Advanced aerodynamic analysis, i.e. linking to open source CFD software

## Dependencies

 - PyQt4
 - PyVTK
 - numpy, scipy, matplotlib
 - lxml (will be removed)

## Documentation

The [PyAero documentation](http://pyaero.readthedocs.io/en/latest) is hosted at [Read the Docs](https://readthedocs.org/).

It is automatically generated using the files in the [docs](https://github.com/chiefenne/PyAero/tree/master/docs) folder via [Sphinx](http://www.sphinx-doc.org/en/stable/index.html).

## Release History

* 0.6
    * Work in progress


Andreas Ennemoser – [@chiefenne](https://twitter.com/chiefenne) – andreas.ennemoser@aon.at
 
Distributed under the MIT license. See LICENSE for more information.
