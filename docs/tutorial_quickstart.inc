.. _quickstart:
Quickstart
----------

The easiest way to see whats going on is to follow `this PyAero tutorial on YouTube <https://www.youtube.com/watch?v=RBrBEyHAAss>`_ to get the minimum necessary introduction to `PyAero <index.html>`_.


The general steps for mesh generation in `PyAero <index.html>`_ can be explained as follows:

1. Load an airfoil contour file

   - Loading can be done in several ways (see also :ref:`tutorial_load`).
   - For the quick start, just use the :menuselection:`File --> Open` menu and browse to your airfoil contour and load it

2. Spline and refine the airfoil contour

   - This is an important task, since the mesh around the airfoil is based on the point distribution which is generated right here
   - For first tests you can go with the default settings and just click the *Spline and Refine* Button
   - The contour will first be splined (constant distance between points) with the given number of points.
   - In the same step the contour will be refined mainly around the leading edge. The refinment criterion is a minimum angle between two consecutive line segments made of three adjacent points

3. Make a trailing edge with finite thickness

   - Since in real life the airfoil trailing edge has a finit thickness, this needs to be taken into account before meshing
   - The defaults make a trailing edge with a thickness of 0.4% relative to the unity chord length

3. Mesh the refined airfoil contour

   - Click on *Create Mesh* to create your first mesh

4. Export the mesh in the required format

   - Click on *Export Mesh* to export the mesh in a specific format. Use the appropriate check box(es)

This is it.