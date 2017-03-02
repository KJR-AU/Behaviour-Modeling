# merge selected nodes

# TODO
# load ast for the feature in which nodes are being merged 
# within the AST, change the merged nodes to comments
# regenerate the feature file (maybe this is done on demand in another script) 
# separate feature to promote a node to the background

import os
import pickle
import sys

sys.path.append("/Library/Python/2.7/site-packages")

document.orientation = Application.ORIENTATION_TOP_TO_BOTTOM
document.bias = Application.BIAS_START
document.addEntityAsSuccessor = True

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
            # get the filename of the feature for this node
            featureFileName = ge.user['filename']
            baseName = os.path.basename(featureFileName)
            dirName = os.path.dirname(featureFileName)
            pickleBaseName = os.path.splitext(baseName)[0] + '.pickle'
            pickleFilePath = os.path.join(dirName, pickleBaseName)
            # load the pickled AST for this feature
            feature = pickle.load(open(pickleFilePath, "rb"))
            # print 'Before', feature, '\n\n'
            # print 'Comments', feature['comments']
            # print 'Feature', feature['feature']['children']
        if count > 0:  # i.e. we're past the first element
            # check that we're only merging nodes in the same feature
            if ge.user['filename'] != featureFileName:
                Application.alert('You can only merge nodes from the same feature.')
            else:
                # find the matching AST node in the feature
                # where the AST node matches on the location line
                # print feature['feature']['children'], '\n\n'
                for key, value in feature['feature'].items():
                    if (key == 'children'):
                        for child in value:
                            for step in child['steps']:
                                # print step
                                if step['location']['line'] == ge.user['line']:
                                    # print "AST node:", step['text']
                                    # print "Graph Element:", ge.title
                                    # copy it to a new comment item
                                    newComment = step
                                    # print newComment
                                    # change the new item type to Comment
                                    newComment['type'] = 'Comment'
                                    # update the text to include the Keyword
                                    newComment['text'] = '#' + newComment['keyword'] + newComment['text']
                                    # insert the new item in the Comments section of the AST
                                    feature['comments'].append(newComment)
                                    # remove the original item from the feature section of the AST
                                    child['steps'].remove(step)

                # update pickled AST
                # print 'After', feature
                # enable one level of undo for merge
                # if pickleFilPath exists, rename pickleFilePath to os.path.splitext(baseName)[0] + '.1'
                with open(pickleFilePath, 'w') as pickleHandle:
                    pickle.dump(feature, pickleHandle)

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
