User Interface
==============

`PyAero <index.html>`_ comes with a graphical user interface (GUI) written in PYTHON and `PyQt4 <http://www.riverbankcomputing.com/software/pyqt/intro>`_. The reason for using PyQt4 is that it works with Python 2.7.x., whereas PyQt5 needs Python 3.x. May be at a later point in time a migration to the more modern packages will be undertaken.

Main Screen
-----------

.. _figure_main_screen:
.. figure::  images/main_screen.png
   :align:   center
   :target:  _images/main_screen.png
   :name: mainscreen

   Graphical user interface of PyAero

Menus
------

Menus in `PyAero <index.html>`_ try to behave much the same as in typical desktop software. For standard menus as :menuselection:`File` or :menuselection:`Print` the documentation will be kept short. See `GUI screenshot <mainscreen_>`_ for the location of the menubar in the GUI and `menu structure <menu_structure_>`_ for an overview of the menu structure.

The menus in the menubar and the tools in the toolbar (see Toolbar) are coded in a dynamic way. That is, all menus and toolbar items (and their respective handlers/callbacks) are read from XML files (PMenu.xml, PToolbar.xml).The graphical user interface is automatically populated using the entries of those files. With this structure in place, menus and toolbar items can easily be extended and customized. When adding new menus and thus functionality, it is required to provide respective handlers (referring to PyQt nomenclature so-called “slots”) to take care of the newly introduced functionality.

.. figure::  images/menu_structure.png
   :align:   center
   :target:  _images/menu_structure.png
   :name: menu_structure

   PyAero menu structure

.. include:: ui_menu_file.inc
.. include:: ui_menu_edit.inc
.. include:: ui_menu_view.inc
.. include:: ui_menu_tools.inc
.. include:: ui_menu_help.inc

Toolbar
-------

The toolbar in `PyAero <index.html>`_ (see also:ref:`figure_main_screen`) allows fast access to actions which are otherwise triggered by menus. Each of the toolbar buttons launch a specific action. The toolbar can be customized by editing the file :file:`$PYAEROPATH/data/PToolBar.xml`.

.. figure::  images/toolbar_animated.gif
   :align:   center
   :target:  _images/toolbar_animated.gif
   :name: menu_structure

   Overview on toolbar options
