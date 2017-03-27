# Exports all the document's nodes into files
# * Top Level Groups => Features
# * Nested Groups => Background or Scenarios


from __future__ import print_function
import sys
import shutil
import os

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


document.clearSelection()


def extract_tags(group_element):
    #utils.debug("Extracting Tags from ", pprint=group_element.user)
    try:
        tags = []
        if group_element.user["tags"] is not None:
            for t in group_element.user["tags"].split(","):
                tags.append({'location': {'column': 0, 'line': 0},
                             'name': t,
                             'type': 'Tag'})
        return tags
    except KeyError:
        return []


features = []
elements = {}
sections = {}
edges = {}

# Iterate though all the elements, extracting details that were set by
# 'Import Feature File' to build a new in-memory representation
# which can then be written out.
#
# NOTE: document.all does walk the trees so the information of relationships and order has to be re-established.
#
for elem in document.all:
    if elem.isGroup:
        if elem.color == Color.GREEN:
            # TOP LEVEL FEATURE
            x = {'type': 'Feature',
                 'language': 'en',
                 'keyword': u'Feature',
                 'tags': extract_tags(elem),
                 'location': {'column': 0, 'line': 0},
                 'name': elem.title,
                 'children': [],
                 'filename': elem.user['filename']}
            for c in elem.children:
                x['children'].append(c.eid)
            features.append(x)
        else:
            # Background, Scenario or Scenario Outline.
            x = {'type': elem.user["type"],
                 'location': {'column': 0, 'line': 0},
                 'steps': [],
                 'keyword': elem.user["type"],
                 'name': ''
                 }
            if elem.user["type"] != "Background":
                x['name'] = elem.title
                x['tags'] = extract_tags(elem)

            for c in elem.children:
                x['steps'].append(c.eid)
            sections[elem.eid] = x
    elif elem.isEdge:
        src = elem.source
        tgt = elem.target
        if src.isEntity and tgt.isEntity:
            #utils.debug("src " + str(src.eid) + " tgt " + str(tgt.eid))
            if src.eid not in edges:
                edges[src.eid] = [tgt.eid]
            else:
                edges[src.eid].append(tgt.eid)
        else:
            utils.debug("Unknown Edge")
    elif elem.isEntity:
        #utils.debug(elem, elem.eid, elem.title, elem.isEdge, elem.user)
        x = {'type': 'Step',
             'location': {'column': 0, 'line': 0},
             'keyword': elem.user["keyword"],
             'text': elem.title}
        elements[elem.eid] = x
        #utils.debug(str(elem.eid) + " " + elem.title)
    else:
        utils.debug("unknown element", elem)

for feature in features:
    for childId in feature['children']:
        for stepId in sections[childId]['steps']:
            if stepId in elements:
                elements[stepId]['feature'] = feature['name']
                elements[stepId]['scenario'] = sections[childId]['name']

# if len(features) > 1:
#     # TODO: Handle Multiple Features in a single document
#     #       eg. Implement choice which feature to export?
#     #       or export all to different files in the same folder
#     raise NotImplementedError("too many Features in document")

for selectedFeature in features:

    featureFileName = selectedFeature['filename']
    #Application.alert("doing " + featureFileName)
    featureDoc = {'type': 'GherkinDocument', 'comments': [], 'feature': selectedFeature}
    
    # noinspection PyRedeclaration
    seen_background_node = False
    sections_in_order = []
    for eid in selectedFeature["children"]:
        s = sections[eid]
        if s["keyword"] == "Background":
            if seen_background_node:
                raise NotImplementedError("Too many 'Background' nodes in Feature")
            seen_background_node = True
            sections_in_order.insert(0, s)
        elif s["keyword"] == "Scenario":
            sections_in_order.append(s)
        else:
            raise NotImplementedError("Regenerating section of type %r not implemented" % (s["keyword"]))

    selectedFeature["children"] = sections_in_order

    #utils.debug("elements", pprint=elements)
    #utils.debug("edges", pprint=edges)
    
    edgesInFeature = {};
    for srcId in edges:
        for tgtId in edges[srcId]:
            if elements[tgtId]['feature'] == selectedFeature['name'] and elements[srcId]['feature'] == selectedFeature['name']:
                if srcId not in edgesInFeature:
                    edgesInFeature[srcId] = [tgtId]
                else:
                    edgesInFeature[srcId].append(tgtId)
            elif ((elements[tgtId]['feature'] == selectedFeature['name'] and elements[srcId]['feature'] != selectedFeature['name']) or
                (elements[srcId]['feature'] == selectedFeature['name'] and elements[tgtId]['feature'] != selectedFeature['name'])):
                # inter-feature link - encode and save as a comment
                comment = utils.encode_inter_feature_link(
                    elements[srcId]['feature'],
                    elements[srcId]['scenario'],
                    elements[srcId]['keyword'], 
                    elements[srcId]['text'],
                    elements[tgtId]['feature'],
                    elements[tgtId]['scenario'],
                    elements[tgtId]['keyword'], 
                    elements[tgtId]['text']
                )
                
                featureDoc['comments'].append(comment)

    # Now for each section take their nodes and sort them.
    sorted_nodes = utils.nodes_by_path(edgesInFeature)
    
    for c in selectedFeature["children"]:
        ret = []
        found = False
        for s in sorted_nodes:
            if s in c["steps"]:
                found = True
                ret.append(elements[s])
        c["steps"] = ret
        if not found:
            raise NotImplementedError("""
                Unable to place all items in the section
                Ensure that there are no loops, and background is connected to at least one scenario
            """)
    
    try:
        # TODO: Element may not exist (FL API missing a good way to check)
        if document.user["comments"] is not None:
            featureDoc['comments'].append(document.user["comments"])
    except KeyError:
        pass
    
    #utils.debug(pprint=featureDoc)
    
    shutil.copyfile(featureFileName, featureFileName + ".old")
    utils.write_gherkin_to_file(featureFileName, featureDoc)
