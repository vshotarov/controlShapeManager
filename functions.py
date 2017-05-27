'''This module contains functions to provide a higher level of interaction with the commands in the manager.py file. 
The commands in this file are meant to be the ones used by the users, so they should be used in the UI.'''
import functools
import os

import maya.cmds as mc

# Local import
import manager
reload(manager)


def getAvailableControlShapes():
    '''Returns a list of the available control shapes in the specified library. Each element
    of the list is a tuple containing the label (name) of the controlShape and a reference
    to the command to assign that shape via functools.partial'''
    lib = manager.SHAPE_LIBRARY_PATH
    return [(x.split(".")[0], functools.partial(assignControlShape, x.split(".")[0])) for x in os.listdir(lib)]


def getAvailableColours():
    '''Returns a list of the available 32 colours for overrideColor in maya. Each element
    of the list is a tuple containig the label, reference to the command which assigns the
    colour and the name of an image to be used as an icon'''
    return [("index" + str(i).zfill(2), functools.partial(assignColour, i), "shapeColour" + str(i).zfill(2) + ".png") for i in range(32)]


def assignColour(*args):
    '''Assigns args[0] as the overrideColor of the selected curves'''
    for each in mc.ls(sl=1, fl=1):
        manager.setColour(each, args[0])


def assignControlShape(*args):
    '''Assigns args[0] as the shape of the selected curves'''
    sel = mc.ls(sl=1, fl=1)
    for each in sel:
        manager.setShape(each, manager.loadFromLib(args[0]))
    mc.select(sel)


def saveCtlShapeToLib(*args):
    '''Saves the selected shape in the defined control shape library'''
    result = mc.promptDialog(title="Save Control Shape to Library",
                             m="Control Shape Name",
                             button=["Save", "Cancel"],
                             cancelButton="Cancel",
                             dismissString="Cancel")
    if result == "Save":
        name = mc.promptDialog(q=1, t=1)
        manager.saveToLib(mc.ls(sl=1, fl=1)[0], name)
    rebuildUI()


def mirrorCtlShapes(*args):
    '''Mirrors the selected control's shape to the other control on the other side'''
    sel = mc.ls(sl=1, fl=1)
    for ctl in sel:
        if ctl[0] not in ["L", "R"]:
            continue
        search = "R_"
        replace = "L_"
        if ctl[0] == "L":
            search = "L_"
            replace = "R_"
        shapes = manager.getShape(ctl)
        for shape in shapes:
            shape.pop("colour")
        manager.setShape(ctl.replace(search, replace), shapes)
        _flipCtlShape(ctl.replace(search, replace))
    mc.select(sel)


def copyCtlShape(*args):
    '''Copies the selected control's shape to a global variable for pasting'''
    global ctlShapeClipboard
    ctlShapeClipboard = manager.getShape(mc.ls(sl=1, fl=1)[0])
    for ctlShape in ctlShapeClipboard:
        ctlShape.pop("colour")


def pasteCtlShape(*args):
    '''Assigns the control's shape from the ctlShapeClipboard global variable 
    to the selected controls'''
    sel = mc.ls(sl=1, fl=1)
    for each in sel:
        manager.setShape(each, ctlShapeClipboard)
    mc.select(sel)


def flipCtlShape(*args):
    '''Flips the selected control shapes to the other side in all axis'''
    sel = mc.ls(sl=1, fl=1)
    for each in sel:
        _flipCtlShape(each)
    mc.select(sel)


def flipCtlShapeX(*args):
    '''Flips the selected control shapes to the other side in X'''
    sel = mc.ls(sl=1, fl=1)
    for each in sel:
        _flipCtlShape(each, [-1, 1, 1])
    mc.select(sel)


def flipCtlShapeY(*args):
    '''Flips the selected control shapes to the other side in Y'''
    sel = mc.ls(sl=1, fl=1)
    for each in sel:
        _flipCtlShape(each, [1, -1, 1])
    mc.select(sel)


def flipCtlShapeZ(*args):
    '''Flips the selected control shapes to the other side in Z'''
    sel = mc.ls(sl=1, fl=1)
    for each in sel:
        _flipCtlShape(each, [1, 1, -1])
    mc.select(sel)


def _flipCtlShape(crv=None, axis=[-1, -1, -1]):
    '''Scales the points of the crv argument by the axis argument. This function is not meant to be
    called directly. Look at the flipCtlShape instead.'''
    shapes = manager.getShape(crv)
    newShapes = []
    for shape in shapes:
        for i, each in enumerate(shape["points"]):
            shape["points"][i] = [each[0] * axis[0], each[1] * axis[1], each[2] * axis[2]]
        newShapes.append(shape)
    manager.setShape(crv, newShapes)
    mc.select(crv)


def rebuildUI(*args):
    '''Rebuilds the UI defined in managerUI.py'''
    mc.evalDeferred("""
import controlShapeManager
reload(controlShapeManager)
""")
