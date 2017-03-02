# find and merge nodes matching input text
# investigate if this script could just select the matching nodes and then call the merge script

import sys

sys.path.append("/Library/Python/2.7/site-packages")

document.orientation = Application.ORIENTATION_TOP_TO_BOTTOM
document.bias = Application.BIAS_START
document.addEntityAsSuccessor = True

search_string = Application.askForString("Item Text:", None)
matching = document.find(search_string, None)
# get selected nodes
count = 0
merged = []
for ge in matching:
    if ge.isEntity:
        if count == 0:
            root_node = ge
        print count, ge.title
        if count > 0:  # i.e. we're past the first element
            merged.append(ge)
            if ge.hasOutEdges:
                for e in ge.outEdges:
                    document.reconnect(e, Application.EDGE_TAIL, root_node)
            if ge.hasInEdges:
                for e in ge.inEdges:
                    document.reconnect(e, Application.EDGE_HEAD, root_node)
        count = count + 1
print merged
document.clearSelection()
document.selection = merged
print document.selection
document.deleteSelection(False)
print "Done"
# for each item in the selected list after the first item (the root node)
# find the successor of that item
# link the root node to the successor
# delete the current node being merged
