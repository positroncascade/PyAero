from PyQt4 import QtGui, QtCore

import PGraphicsItemsCollection as gc


def addTestItems(scene):

    # add items to the scene
    circle1 = gc.GraphicsCollection()
    circle1.Circle(0, 0, 10)

    circle2 = gc.GraphicsCollection()
    circle2.Circle(-30, -30, 30)
    circle2.pen.setColor(QtGui.QColor(255, 0, 0, 255))
    circle2.pen.setWidth(4)
    circle2.brush.setColor(QtGui.QColor(255, 0, 0, 100))

    circle3 = gc.GraphicsCollection()
    circle3.Circle(50, 50, 20)
    circle3.pen.setColor(QtGui.QColor(0, 255, 0, 255))
    circle3.pen.setWidth(2)

    circle4 = gc.GraphicsCollection()
    circle4.Circle(-10, 40, 20)
    circle4.pen.setColor(QtGui.QColor(0, 0, 255, 255))
    circle4.brush.setColor(QtGui.QColor(255, 0, 255, 60))
    circle4.pen.setWidth(3)

    rectangle1 = gc.GraphicsCollection()
    rectangle1.Rectangle(-20, 10, 70, 35)
    rectangle1.pen.setColor(QtGui.QColor(0, 0, 255, 255))
    rectangle1.brush.setColor(QtGui.QColor(0, 255, 0, 180))
    rectangle1.pen.setWidth(2)

    text1 = gc.GraphicsCollection()
    font = QtGui.QFont('Arial', 20)
    font.setBold(True)
    text1.Text(0, 90, 'This is a text', font)
    text1.pen.setColor(QtGui.QColor(50, 30, 200, 255))

    point1 = gc.GraphicsCollection()
    point1.Point(0, 0)
    point1.pen.setColor(QtGui.QColor(0, 0, 0, 255))

    polygon1 = gc.GraphicsCollection()
    polygon = QtGui.QPolygonF()
    polygon.append(QtCore.QPointF(20, 10))
    polygon.append(QtCore.QPointF(45, 10))
    polygon.append(QtCore.QPointF(45, -40))
    polygon.append(QtCore.QPointF(15, -40))
    polygon1.pen.setColor(QtGui.QColor(0, 0, 0, 255))
    polygon1.pen.setWidth(1)
    polygon1.brush.setColor(QtGui.QColor(0, 0, 255, 200))
    polygon1.Polygon(polygon)

    scene.itemc1 = scene.addGraphicsItem(circle1)
    scene.itemc2 = scene.addGraphicsItem(circle2)
    scene.itemc3 = scene.addGraphicsItem(circle3)
    scene.itemc4 = scene.addGraphicsItem(circle4)
    scene.itemr1 = scene.addGraphicsItem(rectangle1)
    # scene.itemt1 = scene.addGraphicsItem(text1)
    scene.itemp1 = scene.addGraphicsItem(point1)
    scene.itempo1 = scene.addGraphicsItem(polygon1)


def deleteTestItems(scene):

    scene.removeItem(scene.itemc1)
    scene.removeItem(scene.itemc2)
    scene.removeItem(scene.itemc3)
    scene.removeItem(scene.itemc4)
    scene.removeItem(scene.itemr1)
    # scene.removeItem(scene.itemt1)
    scene.removeItem(scene.itemp1)
    scene.removeItem(scene.itempo1)