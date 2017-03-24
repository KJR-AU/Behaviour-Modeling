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

#set debug mode
#debug = false
# get selected nodes
count = 0
merged = []
# iterate through the selection - keep first node and remove all others, transferring edges to the first node
# print 'selected:', len(document.selection)
if len(document.selection) < 2:
    Application.alert('You must select at least two nodes to merge.')

featureFileName = None
feature = None

for ge in document.selection:
    if ge.isEntity:
        if count == 0:
            root_node = ge
            #if ! ge.isEntity:
            #    Application.alert('Only entity nodes can be merged.')
            # get the filename of the feature for this node
            featureFileName = ((ge.parent).parent).user['filename']
        if count > 0:  # i.e. we're past the first element
            # check that we're only merging nodes in the same feature
            if ((ge.parent).parent).user['filename'] != featureFileName:
                Application.alert('You can only merge nodes from the same feature.')
            else:
                # update the graph
                merged.append(ge)
                if ge.hasOutEdges:
                    for e in ge.outEdges:
                        document.reconnect(e, Application.EDGE_TAIL, root_node)
                if ge.hasInEdges:
                    for e in ge.inEdges:
                        document.reconnect(e, Application.EDGE_HEAD, root_node)
        count = count + 1
# print merged
document.clearSelection()
document.selection = merged
# print document.selection
document.deleteSelection(False)
document.clearSelection()
# print "Done"
# for each item in the selected list after the first item (the root node)
# find the successor of that item
# link the root node to the successor
# delete the current node being merged
