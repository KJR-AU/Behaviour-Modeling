# coding=utf-8
from __future__ import print_function
import sys
import os
from pprint import pformat
import re

__all__ = ['nodes_by_path', '_DEBUG', 'reverse_paths', 'write_gherkin_to_file', 'debug']

# When executed as part of test suite debugging may be turned on.
_DEBUG = True


def debug(*args, **kwargs):
    """
    Logs messages with stack trace style like comments to assist debugging.

    :param args: simple list of arguments to print
    :keyword pprint: this argument will be formatted using pprint.pformat
    """
    if _DEBUG:
        # noinspection PyProtectedMember
        caller = sys._getframe().f_back
        filename = os.path.relpath(caller.f_code.co_filename)
        loc = '  File "%s", line %i: ' % (filename, caller.f_lineno)
        if "pprint" in kwargs:
            print(loc, args)
            print("\t\t" + "\n\t\t".join(pformat(kwargs["pprint"], width=300).split("\n")))
        else:
            print(loc, args)


def write_gherkin_to_file(feature_file_name, feature_doc, indent_with="  "):
    """
    Walks the feature document AST printing the elements into a formatted document.

    While the AST contains Line and Column elements these are not honoured, instead
    the document is reformatted cleanly.

    :param feature_file_name:   Feature
    :param feature_doc:         AST containing gherkin file
    :param indent_with:         Defaults to two spaces.
    """

    # Gherkin specification only allow a single feature per files
    # if a list is provided all elements will be printed (but the resulting file would not be valid)
    if isinstance(feature_doc["feature"], list):
        print("WARNING: Multiple Features in file")
        feature_list = feature_doc["feature"]
    else:
        feature_list = [feature_doc["feature"]]

    # For Reference the gherkin.parser.Parser is built using:
    #       <https://github.com/cucumber/cucumber/blob/master/gherkin/gherkin.berp>
    #       <https://github.com/cucumber/gherkin-python/blob/master/gherkin-python.razor>

    with open(feature_file_name, 'w') as file_handle:
        first = True
        for selected_feature in feature_list:
            if not first:
                file_handle.write("\n\n")
            first = False
            indent = indent_with * 0

            # Comments above Tags
            if len(feature_doc["comments"]) > 0:
                file_handle.write(indent + ("\n" + indent).join(feature_doc["comments"]))

            # Tags above "Feature:"
            if "tags" in selected_feature:
                for t in selected_feature["tags"]:
                    file_handle.write(indent + t["name"] + "\n")
            file_handle.write(indent + selected_feature["keyword"] + ": " + selected_feature["name"] + "\n")

            # Description inside Feature
            indent = indent_with * 1
            if len(selected_feature["description"]) > 0:
                file_handle.write(selected_feature["description"] + "\n")

            # Background is always the first child
            for sect in selected_feature["children"]:
                indent = indent_with * 1

                file_handle.write("\n")
                if sect["type"] == "Background":
                    file_handle.write(indent + sect["keyword"] + ":\n")
                else:
                    if "tags" in sect:
                        for t in sect["tags"]:
                            file_handle.write(indent + t["name"] + "\n")
                    file_handle.write(indent + sect["keyword"] + ": " + sect["name"] + "\n")

                # Description inside Scenario
                indent = indent_with * 2
                if len(sect["description"]) > 0:
                    file_handle.write(sect["description"] + "\n")

                for step in sect["steps"]:
                    file_handle.write(indent + step["keyword"] + step["text"] + "\n")


def nodes_by_path(forward_edges):
    """
    Sorts a subset of the nodes by their depth

    Based on https://en.wikipedia.org/wiki/Topological_sorting#Kahn.27s_algorithm

            1 ─> 2 ─┬─> 3 ─> 7
                    └─> 4 ─> 5 ─> 6

    Order of branches depends on order of elements in forward_edges
    e.g. if edges contains {2: [3,4]}
         return with have 3 branch first [1, 2, 3, 7, 4, 5, 6]
    whereas {2: [4,3]}
         return with have 4 branch first [1, 2, 4, 5, 6, 3, 7]

    Any nodes attached as part of a loop or branching away from a loop will not appear in the output
    e.g. This will only return [1]
              1 ─┬─> 2 ──┬─> 3
                 └── 4 <─┘

    Any unattached paths will all be returned; although order is not guaranteed.
    eg. The two paths [1,2,3] and [4,5,6] will be returned one after the other.
              1 ─> 2 ─> 3
              4 ─> 5 ─> 6

    :param forward_edges:
    :return: sorted list of unique nodes
    """
    # O(Edges) pass of edges to extract all nodes
    #           and determine reversed version
    all_nodes = set()
    backward_edges = reverse_paths(forward_edges, all_nodes)

    # O(Nodes) find list of nodes with no inbound edges
    origins = []
    for e in all_nodes:
        if e not in backward_edges.keys():
            origins.append(e)

    # debug(" origins", pprint=origins)
    # debug(" all_nodes", pprint=all_nodes)

    # L ← Empty list that will contain the sorted elements
    sorted_list = []

    # S ← Set of all nodes with no incoming edges
    # while S is non-empty do
    while len(origins) > 0:
        # remove a node n from S
        n = origins.pop(-1)
        # add n to tail of L
        sorted_list.append(n)
        # for each node m
        #       with an edge e from n to m do
        while n in forward_edges and len(forward_edges[n]) > 0:
            # Remove edge e (from n to m) from the graph

            # first the forward edge
            m = forward_edges[n].pop(-1)

            # backward edge
            if m in backward_edges:
                inbound_edges = backward_edges[m]
                index = inbound_edges.index(n)
                del inbound_edges[index]
                if len(inbound_edges) == 0:
                    del backward_edges[m]
                    origins.append(m)
            else:
                origins.append(m)
    return sorted_list


def reverse_paths(edges, all_nodes=set()):
    """
    Reverse all the paths in a directed graph

    e.g.      {A: [B, D], B: [C]}       # A ─┬─> B ──> C
                                        #    └─> D
    becomes   {C: [B], B: [A], D: [A]}  # A <─┬─ B <── C
                                        #     └─ D

    :param all_nodes:
    :param edges:
    :return:
    """
    rev = {}
    for k in edges.keys():
        all_nodes.add(k)
        for v in edges[k]:
            all_nodes.add(v)
            if v in rev:
                rev[v].append(k)
            else:
                rev[v] = [k]
    # print(pformat(edges),"=>",pformat(rev))
    return rev


def decode_risks(inputText):
    decodedRisks = []
    matchObjects = re.finditer(r'Risk: \[(.*?) | Type: (.*?) | Likelihood: (.*?) | Severity: (.*?)\]', inputText)
    for matchObj in matchObjects:
        decodedRisks.append({
            'Risk': matchObj.group(1),
            'Type': matchObj.group(2),
            'Likelihood': matchObj.group(3),
            'Severity': matchObj.group(4)
        })
    return decodedRisks


def encode_risk(risk):
    return u'Risk: [%s | Type: %s | Likelihood: %s | Severity: %s]' % (
        risk['Risk'],
        risk['Type'],
        risk['Likelihood'],
        risk['Severity']
    )


def decode_inter_feature_link(linkString):
    decodedLinks = []
    matchObjects = re.finditer( r'-- InterFeatureLink from\(feature=\"(.*?)\", scenario=\"(.*?)\", keyword=\"(.*?)\", text=\"(.*?)\"\), to\(feature=\"(.*?)\", scenario=\"(.*?)\", keyword=\"(.*?)\", text=\"(.*?)\"', linkString)

    for matchObj in matchObjects:
        decodedLink = {
            'from_feature': matchObj.group(1),
            'from_scenario': matchObj.group(2),
            'from_keyword': matchObj.group(3),
            'from_text': matchObj.group(4),
            'to_feature': matchObj.group(5),
            'to_scenario': matchObj.group(6),
            'to_keyword': matchObj.group(7),
            'to_text': matchObj.group(8)
        }
        decodedLinks.append(decodedLink)
    return decodedLinks

def encode_inter_feature_link(from_feature, from_scenario, from_keyword, from_text, to_feature, to_scenario, to_keyword, to_text):
    encodedLinkString = "-- InterFeatureLink "
    encodedLinkString += "from("
    encodedLinkString += "feature=\"" + from_feature + "\", "
    encodedLinkString += "scenario=\"" + from_scenario + "\", "
    encodedLinkString += "keyword=\"" + from_keyword + "\", "
    encodedLinkString += "text=\"" + from_text +"\""
    encodedLinkString += "), to("
    encodedLinkString += "feature=\"" + to_feature + "\", "
    encodedLinkString += "scenario=\"" + to_scenario + "\", "
    encodedLinkString += "keyword=\"" + to_keyword + "\", "
    encodedLinkString += "text=\"" + to_text + "\""
    encodedLinkString += ") --"
    
    return encodedLinkString
