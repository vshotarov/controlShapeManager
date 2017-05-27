'''Contains the core low level functionality of the control shape manager. The functions here work directly
with the data in the nurbs curves.'''
import os
import re

from maya import cmds as mc

# Local import
import utils
reload(utils)

SHAPE_LIBRARY_PATH = "C:/PATH_TO_LIBRARY"


def getShape(crv=None):
    '''Returns a dictionary containing all the necessery information for rebuilding the passed in crv.'''
    crvShapes = validateCurve(crv)

    crvShapeList = []

    for crvShape in crvShapes:
        crvShapeDict = {
            "points": [],
            "knots": [],
            "form": mc.getAttr(crvShape + ".form"),
            "degree": mc.getAttr(crvShape + ".degree"),
            "colour": mc.getAttr(crvShape + ".overrideColor")
        }
        points = []

        for i in range(mc.getAttr(crvShape + ".controlPoints", s=1)):
        	points.append(mc.getAttr(crvShape + ".controlPoints[%i]" % i)[0])

        crvShapeDict["points"] = points
        crvShapeDict["knots"] = utils.getKnots(crvShape)

        crvShapeList.append(crvShapeDict)

    return crvShapeList


def setShape(crv, crvShapeList):
    '''Creates a new shape on the crv transform, using the properties in the crvShapeDict.'''
    crvShapes = validateCurve(crv)

    oldColour = mc.getAttr(crvShapes[0] + ".overrideColor")
    mc.delete(crvShapes)

    for i, crvShapeDict in enumerate(crvShapeList):
        tmpCrv = mc.curve(p=crvShapeDict["points"], k=crvShapeDict["knots"], d=crvShapeDict["degree"], per=bool(crvShapeDict["form"]))
        newShape = mc.listRelatives(tmpCrv, s=1)[0]
        mc.parent(newShape, crv, r=1, s=1)

        mc.delete(tmpCrv)
        newShape = mc.rename(newShape, crv + "Shape" + str(i + 1).zfill(2))

        mc.setAttr(newShape + ".overrideEnabled", 1)

        if "colour" in crvShapeDict.keys():
            setColour(newShape, crvShapeDict["colour"])
        else:
            setColour(newShape, oldColour)


def validateCurve(crv=None):
    '''Checks whether the transform we are working with is actually a curve and returns it's shapes'''
    if mc.nodeType(crv) == "transform" and mc.nodeType(mc.listRelatives(crv, c=1, s=1)[0]) == "nurbsCurve":
        crvShapes = mc.listRelatives(crv, c=1, s=1)
    elif mc.nodeType(crv) == "nurbsCurve":
        crvShapes = mc.listRelatives(mc.listRelatives(crv, p=1)[0], c=1, s=1)
    else:
        mc.error("The object " + crv + " passed to validateCurve() is not a curve")
    return crvShapes


def loadFromLib(shape=None):
    '''Loads the shape data from the shape file in the SHAPE_LIBRARY_PATH directory'''
    path = os.path.join(SHAPE_LIBRARY_PATH, shape + ".json")
    data = utils.loadData(path)
    return data


def saveToLib(crv=None,
              shapeName=None):
    '''Saves the shape data to a shape file in the SHAPE_LIBRARY_PATH directory'''
    crvShape = getShape(crv=crv)
    path = os.path.join(SHAPE_LIBRARY_PATH, re.sub("\s", "", shapeName) + ".json")
    for shapeDict in crvShape:
        shapeDict.pop("colour", None)
    utils.saveData(path, crvShape)


def setColour(crv, colour):
    '''Sets the overrideColor of a curve'''
    if mc.nodeType(crv) == "transform":
        crvShapes = mc.listRelatives(crv)
    else:
        crvShapes = [crv]
    for crv in crvShapes:
        mc.setAttr(crv + ".overrideColor", colour)


def getColour(crv):
    '''Returns the overrideColor of a curve'''
    if mc.nodeType(crv) == "transform":
        crv = mc.listRelatives(crv)[0]
    return mc.getAttr(crv + ".overrideColor")
