```diff
+ RELEASE 1.0 IS READY.
+ MESHES CAN BE GENERATED
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

* 1.0
    * Meshes can be generated now.
    * Export available in AVL-FIRE format and SU2 format

* 0.9
    * GUI is almost ready, at least ready to be able to do meaningful work
    * All preparations for mehing are done
    * Airfoil contours can be loaded, splined and refined
    * A trailing edge thickness can be added

* 0.8
    * Raw functionality of GUI available
    * Zooming and moving works
    * Airfoils can be loaded (also multiple airfoils is possible)


Andreas Ennemoser – [@chiefenne](https://twitter.com/chiefenne) – andreas.ennemoser@aon.at
 
Distributed under the MIT license. See LICENSE for more information.
