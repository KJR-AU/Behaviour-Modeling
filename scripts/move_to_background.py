# move selected node to background

# TODO
# load ast for the feature in which nodes are being merged
# within the AST, change the merged nodes to comments
# regenerate the feature file (maybe this is done on demand in another script)
# separate feature to promote a node to the background

import os
import pickle
import sys


def updateLineNumbers(feature, offset, increment):
    for key, value in feature['feature'].items():
        if (key == 'children'):
            for child in value:
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
                                print "moved ", step['text'], "to ", step['location']['line']
                    if ('tags' in child):
                        for tag in child['tags']:
                            if tag['location']['line'] >= offset:
                                tag['location']['line'] = tag['location']['line'] + increment
                                print "moved ", tag['name'], "to ", tag['location']['line']
        elif (key == 'tags'):
            for tag in value:
                if tag['location']['line'] >= offset:
                    tag['location']['line'] = tag['location']['line'] + increment
                    print "moved ", tag['text'], "to ", tag['location']['line']
    for comment in feature['comments']:
        if comment['location']['line'] >= offset:
            comment['location']['line'] = comment['location']['line'] + increment
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
            # get the filename of the feature for this node
            featureFileName = ge.user['filename']
            baseName = os.path.basename(featureFileName)
            dirName = os.path.dirname(featureFileName)
            pickleBaseName = os.path.splitext(baseName)[0] + '.pickle'
            pickleFilePath = os.path.join(dirName, pickleBaseName)
            # load the pickled AST for this feature
            feature = pickle.load(open(pickleFilePath, "rb"))
            # print feature
        # find the matching AST node in the feature
        # where the AST node matches on the location line
        # print feature['feature']['children'], '\n\n'
        backgroundExists = False
        for key, value in feature['feature'].items():
            if (key == 'children'):
                current_child = 0
                for child in value:
                    # print current_child
                    if child['type'] == 'Background':
                        backgroundExists = True
                        backgroundIndex = current_child
                        print child, feature['feature']['children'][backgroundIndex]
                        # find last line of background scenario
                        # find the Background group in the graph
                    for step in child['steps']:
                        # print step
                        if step['location']['line'] == ge.user['line']:
                            # print "AST node:", step['text']
                            # print "Graph Element:", ge.title
                            # copy it to a new comment item
                            newBackgroundItem = step
                            # remove the original item from the feature section of the AST
                            # child['steps'].remove(step)
                # insert the step into the background
                if backgroundExists:
                    # update the line location of the new background clause and then append to background AST entry
                    child['steps'].remove(newBackgroundItem)
                    print "removed step:", newBackgroundItem
                    print "Length of background: ", len(feature['feature']['children'][backgroundIndex]['steps'])
                    newBackgroundItem['location']['line'] = feature['feature']['children'][backgroundIndex]['location']['line'] + len(feature['feature']['children'][backgroundIndex]['steps']) + 1
                    feature['feature']['children'][backgroundIndex]['steps'].append(newBackgroundItem)
                    print "appended background:", feature['feature']['children'][backgroundIndex]
                    # make newBackgroundItem node a child of the Background group
                    backgroundGroup = document.find("Background", None)[0]
                    document.modifyAttribute([ge], "parent", backgroundGroup)
                    print "Offset: ", newBackgroundItem['location']['line']
                    updateLineNumbers(feature, newBackgroundItem['location']['line'] + 1, 1)
                    # update all locations
                    # iterate through AST, incrementing all location lines after the insert point by 1
                else:
                    print "Creating Background"
                    # find location of end of Feature description
                    # create new Background AST entry
                    # need to fix the offset to be the end of the description, not just the second line of the file
                    newBackground = {'steps': [], 'keyword': u'Background', 'type': 'Background', 'location': {'column': 1, 'line': 2}, 'name': u''}
                    backgroundIndex = 0
                    # update the line location of the new background clause and then append to background AST entry
                    # newBackgroundItem['location']['line'] = feature['feature']['children'][backgroundIndex]['location']['line'] + len(feature['feature']['children'][backgroundIndex]['steps']) + 1
                    # insert Background after the Feature heading
                    # feature['feature']['children'].insert(backgroundIndex,newBackgroundItem)
                    feature['feature']['children'].insert(backgroundIndex, newBackground)

                    # remove original step from scenario
                    child['steps'].remove(newBackgroundItem)
                    print "removed step:", newBackgroundItem
                    # adjust step location and add steps to new Background
                    print "Length of background: ", len(feature['feature']['children'][backgroundIndex]['steps'])
                    newBackgroundItem['location']['line'] = feature['feature']['children'][backgroundIndex]['location']['line'] + len(feature['feature']['children'][backgroundIndex]['steps']) + 1
                    newBackgroundItem['location']['line'] = feature['feature']['children'][backgroundIndex]['location']['line'] + 1
                    feature['feature']['children'][backgroundIndex]['steps'].append(newBackgroundItem)
                    print "appended background:", feature['feature']['children'][backgroundIndex]
                    # create Background group in the graph
                    backgroundGroup = document.newGroup(None)[0]  # no need to clearSelection each iteration
                    backgroundGroup.title = 'Background'
                    # find feature group and make backgroundGroup a child
                    featureGroup = (ge.parent).parent
                    document.modifyAttribute([backgroundGroup], "parent", featureGroup)
                    # make newBackgroundItem node a child of the Background group
                    document.modifyAttribute([ge], "parent", backgroundGroup)
                    # update all locations
                    # iterate through AST, incrementing all location lines after the insert point by 2
                    # need to fix the offset to be the end of the description, not just the second line of the file
                    # print "Offset: ", feature['feature']['children'][backgroundIndex]['location']['line']+len(feature['feature']['children'][backgroundIndex]['steps'])
                    # updateLineNumbers(feature,feature['feature']['children'][backgroundIndex]['location']['line']+len(feature['feature']['children'][backgroundIndex]['steps'])+1,2)
                    updateLineNumbers(feature, 2, 2)
                current_child = current_child + 1

        # update pickled AST
        # print 'After', feature
        # enable one level of undo for merge
        # if pickleFilPath exists, rename pickleFilePath to os.path.splitext(baseName)[0] + '.1'
        with open(pickleFilePath, 'w') as pickleHandle:
            pickle.dump(feature, pickleHandle)

            # update the graph
            # make the selected nodes children of the Background group
            # reconnect any other incoming our outgoing edges? probably not - we want to show the connection from (last node) of background
            # merged.append(ge)
            # if ge.hasOutEdges:
            #    for e in ge.outEdges:
            #	     document.reconnect(e, Application.EDGE_TAIL, root_node)
            # if ge.hasInEdges:
            #    for e in ge.inEdges:
            #          document.reconnect(e, Application.EDGE_HEAD, root_node)
        count = count + 1
print feature
document.clearSelection()
# document.selection = merged
# print document.selection
# document.deleteSelection(False)
# document.clearSelection()
# print "Done"
# for each item in the selected list after the first item (the root node)
# find the successor of that item
# link the root node to the successor
# delete the current node being merged
