# move selected node to background

# TODO
# load ast for the feature in which nodes are being merged
# within the AST, change the merged nodes to comments
# regenerate the feature file (maybe this is done on demand in another script)
# separate feature to promote a node to the background

import os
#import pickle
import sys

#set debug mode
#debug = false

def updateLineNumbers(feature, offset, increment):
    for key, value in feature['feature'].items():
        if (key == 'children'):
            for child in value:
                if debug:
                    print "Child:", child
                if child['type'] == 'Scenario':
                    if child['location']['line'] >= offset:
                        child['location']['line'] = child['location']['line'] + increment
                if child['type'] == 'Scenario Outline':
                    if child['location']['line'] >= offset:
                        child['location']['line'] = child['location']['line'] + increment
                if child['type'] != 'Background':  # we don't want to update the Background we just created
                    if ('steps' in child):
                        for step in child['steps']:
                            if step['location']['line'] >= offset:
                                step['location']['line'] = step['location']['line'] + increment
                                if debug:
                                    print "moved ", step['text'], "to ", step['location']['line']
                    if ('tags' in child):
                        for tag in child['tags']:
                            if tag['location']['line'] >= offset:
                                tag['location']['line'] = tag['location']['line'] + increment
                                if debug:
                                    print "moved ", tag['name'], "to ", tag['location']['line']
        elif (key == 'tags'):
            for tag in value:
                if tag['location']['line'] >= offset:
                    tag['location']['line'] = tag['location']['line'] + increment
                    if debug:
                        print "moved ", tag['text'], "to ", tag['location']['line']
    for comment in feature['comments']:
        if comment['location']['line'] >= offset:
            comment['location']['line'] = comment['location']['line'] + increment
            if debug:
                print "moved ", comment['text'], "to ", comment['location']['line']


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

featureFileName = None
feature = None

for ge in document.selection:
    if ge.isEntity:
        if count == 0:
            root_node = ge
            backgroundGroup = document.find("Background", None)
            if backgroundGroup : #check that background group node exists
                    document.modifyAttribute([ge], "parent", backgroundGroup[0])
            else:
                    backgroundGroup = document.newGroup(None)[0]  # no need to clearSelection each iteration
                    backgroundGroup.title = 'Background'
                    featureGroup = (ge.parent).parent
                    document.modifyAttribute([backgroundGroup], "parent", featureGroup)
                    document.modifyUserAttribute([backgroundGroup], "type", 'Background')
                    # make newBackgroundItem node a child of the Background group
                    document.modifyAttribute([ge], "parent", backgroundGroup)
#print feature
document.clearSelection()
