# merge selected nodes

# TODO
# load ast for the feature in which nodes are being merged
# within the AST, change the merged nodes to comments
# regenerate the feature file (maybe this is done on demand in another script)
# separate feature to promote a node to the background

import os
#import pickle
import sys

sys.path.append("/Library/Python/2.7/site-packages")

document.orientation = Application.ORIENTATION_TOP_TO_BOTTOM
document.bias = Application.BIAS_START
document.addEntityAsSuccessor = True

# get selected nodes
count = 0
linked = []
# iterate through the selection - keep first node and remove all others, transferring edges to the first node
# print 'selected:', len(document.selection)
if len(document.selection) <> 2:
    Application.alert('You must select two nodes to link.')

featureFileName = None
feature = None

for ge in document.selection:
    if ge.isEntity:
        linked.append(ge)
        if count == 0:
            root_node = ge
            # get the filename of the feature for this node
            featureFileName = ((ge.parent).parent).user['filename']
            baseName = os.path.basename(featureFileName)
            #dirName = os.path.dirname(featureFileName)
            #pickleBaseName = os.path.splitext(baseName)[0] + '.pickle'
            #pickleFilePath = os.path.join(dirName, pickleBaseName)
            # load the pickled AST for this feature
            #feature = pickle.load(open(pickleFilePath, "rb"))
            from_feature = baseName
            # print 'Before', feature, '\n\n'
            # print 'Comments', feature['comments']
            # print 'Feature', feature['feature']['children']
        if count > 0:  # i.e. we're past the first element
            print("0", linked[0].title, linked[0].entityClass)
            print(linked[1].title)
            if linked[0].entityClass == "Given":
                from_node = linked[1]
                to_node = linked[0]
                to_feature = from_feature
                from_feature = os.path.basename(((ge.parent).parent).user['filename'])# update the baseName
                document.modifyUserAttribute([to_node],"links_to",from_feature)
                document.modifyUserAttribute([from_node],"links_to",to_feature)
                document.connect(from_node, to_node)
            else:
                from_node = linked[0]
                to_node = linked[1]
                to_feature = os.path.basename(((ge.parent).parent).user['filename'])
                document.modifyUserAttribute([to_node],"links_to",from_feature)
                document.modifyUserAttribute([from_node],"links_to",to_feature)
                document.connect(from_node, to_node)
            # find the matching AST node in the feature
            # where the AST node matches on the location line
            # print feature['feature']['children'], '\n\n'

        # link the two nodes in the graph
        count = count + 1
# print linked
# document.clearSelection()
# document.selection = linked
# print document.selection

# document.deleteSelection(False)
document.clearSelection()
# print "Done"
# for each item in the selected list after the first item (the root node)
# find the successor of that item
# link the root node to the successor
# delete the current node being merged
