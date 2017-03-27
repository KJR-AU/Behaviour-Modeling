# move selected node to background
#
from __future__ import print_function
import sys

# START COMMON BLOCK
#   Flying Logic sys.path is preserved between script runs do not need to keep adding it every time.
#   although it is possible that the utils script has been changed so may require a reload
reload_needed = False
if 'scriptParentDirectory' in globals():
    if scriptParentDirectory not in sys.path:
        sys.path.append("/Library/Python/2.7/site-packages")
        sys.path.append(scriptParentDirectory)
    else:
        # TODO: better detection, reload only necessary when actively editing the utils.py
        reload_needed = True

# noinspection PyPep8
import utils

if reload_needed:
    reload(utils)
# END COMMON BLOCK




sys.path.append("/Library/Python/2.7/site-packages")
# from javax.swing import Box, BoxLayout, JLabel, JCheckBox, JComboBox, JTextField
# from ASTutils import updateLineNumbers

document.orientation = Application.ORIENTATION_TOP_TO_BOTTOM
document.bias = Application.BIAS_START
document.addEntityAsSuccessor = True

# get selected nodes
count = 0
merged = []

# iterate through the selection - keep first node and remove all others, transferring edges to the first node
# print 'selected:', len(document.selection)
if len(document.selection) < 1:
    Application.alert('You must select at least one node to move into the background.')

# TODO: sort document.selection based order
#       so multiple nodes can be moved from the same scenario
for ge in document.selection:
    # TODO: Fix assumption that element selected is a node (given/when/then) inside a scenario
    #       and work up the parents to find the scenario and then the feature

    scenarioGroup = ge.parent
    if (scenarioGroup is None or scenarioGroup.user["type"] != 'Scenario'):
        # Application.alert('Ignoring Invalid Selection.')
        continue

    featureGroup = scenarioGroup.parent
    if (featureGroup is None or featureGroup.user["type"] != 'Feature'):
        # Application.alert('Ignoring Invalid Selection.')
        continue

    if ge.isEntity:
        valid = True
        # confirm it is the first child of the parent group
        # ie no edges from within the same group
        for elem in document.all:
            if elem.isEdge:
                src = elem.source
                tgt = elem.target
                if src.isEntity and tgt.isEntity:
                    if tgt == ge and src.parent == scenarioGroup:
                        valid = False
                        break

        if valid:
            backgroundGroup = None
            backgroundGroups = document.find("Background", None)
            if backgroundGroups:  # check that background group node exists
                for candidate in backgroundGroups:
                    if featureGroup == candidate.parent:
                        backgroundGroup = candidate
                        break
            else:
                backgroundGroup = document.newGroup(None)[0]
                backgroundGroup.title = 'Background'
                document.modifyAttribute([backgroundGroup], "parent", featureGroup)
                document.modifyUserAttribute([backgroundGroup], "type", 'Background')

            document.modifyAttribute([ge], "parent", backgroundGroup)
        else:
            Application.alert('You must select node(s) at the top of the scenario.')
            break

document.clearSelection()
