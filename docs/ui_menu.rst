Menus
------

Menus in `PyAero <index.html>`_ try to behave much the same as in typical desktop software. For standard menus as *File* or *Print* the documentation will be kept short. See `GUI screenshot <mainscreen_>`_ for the location of the menubar in the GUI and `menu structure <menu_structure_>`_ for an overview of the menu structure.

The menus in the menubar and the tools in the toolbar (see Toolbar) are coded in a dynamic way. That is, all menus and toolbar items (and their respective handlers/callbacks) are read from XML files (PMenu.xml, PToolbar.xml).The graphical user interface is automatically populated using the entries of those files. With this structure in place, menus and toolbar items can easily be extended and customized. When adding new menus and thus functionality, it is required to provide respective handlers (referring to PyQt nomenclature so-called “slots”) to take care of the newly introduced functionality.

.. figure::  images/menu_structure.png
   :align:   center
   :target:  _images/menu_structure.png
   :name: menu_structure

   PyAero menu structure
