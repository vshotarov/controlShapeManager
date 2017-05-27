'''Creates a very simple UI, which is just a button on a specified shelf containing a popup with all the needed
control shape functions.'''
import maya.cmds as mc


# Local import
import functions
reload(functions)

SHELF_NAME = "Custom"
ICON_PATH = "C:/PATH_TO_ICONS"

if SHELF_NAME and mc.shelfLayout(SHELF_NAME, ex=1):
    children = mc.shelfLayout(SHELF_NAME, q=1, ca=1) or []
    for each in children:
        try:
            label = mc.shelfButton(each, q=1, l=1)
        except:
            continue
        if label == "ctlShapeManager":
            mc.deleteUI(each)

    mc.setParent(SHELF_NAME)
    mc.shelfButton(l="ctlShapeManager", i="commandButton.png", width=37, height=37, iol="CTL")
    popup = mc.popupMenu(b=1)
    mc.menuItem(p=popup, l="Save to library", c=functions.saveCtlShapeToLib)

    sub = mc.menuItem(p=popup, l="Assign from library", subMenu=1)

    for each in functions.getAvailableControlShapes():
        mc.menuItem(p=sub, l=each[0], c=each[1])

    mc.menuItem(p=popup, l="Copy", c=functions.copyCtlShape)
    mc.menuItem(p=popup, l="Paste", c=functions.pasteCtlShape)

    sub = mc.menuItem(p=popup, l="Set colour", subMenu=1)

    for each in functions.getAvailableColours():
        mc.menuItem(p=sub, l=each[0], c=each[1], i=ICON_PATH + each[2])

    mc.menuItem(p=popup, l="Flip", c=functions.flipCtlShape)
    mc.menuItem(p=popup, l="Mirror", c=functions.mirrorCtlShapes)
