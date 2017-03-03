from behave import *

use_step_matcher("parse")

_DEBUG = False

from FlyingLogicStub import FLStub, Document, Color

fl_document = None
fl_app = None


def findBy(list, attrib):
    '''
    Helper function to search a list of objects
    to find a match
    :param list:   list of object
    :param attrib: pairs of {attribute_name: expected_value}
    :return: first object matching critera
             or None if no element is found
    '''
    for g in list:
        all = True
        for a in attrib.keys():
            if _DEBUG: print("checking %r.%r (%r) == %r" % (g, a, g.__getattr__(a), attrib[a]))
            all &= g.__getattr__(a) == attrib[a]
        if all:
            return g
    return None


@given("I am running FlyingLogic with a new document")
def new_document(context):
    global fl_document
    global fl_app
    fl_app = FLStub()
    fl_document = Document()


@given("I have a sample file '{filename}'")
def select_file(context, filename):
    global fl_document
    global fl_app
    fl_app._askForFileResponse = "Samples/" + filename


@when("I run the script '{scriptname}'")
def run_script(context, scriptname):
    global fl_document
    global fl_app
    scriptname = "scripts/" + scriptname + ".py"
    execfile(scriptname, {
        'document': fl_document,
        'Application': fl_app,
        'Color': Color(),
        '_DEBUG': _DEBUG
    })


@then("the document contains groups:")
@then("the document contains groups")
def document_groups_exists(context):
    global fl_document
    global fl_app

    # index the items
    lookup = {}
    for g in fl_document._GROUPS:
        lookup[g.title] = g

    # verify they exist
    for row in context.table:
        assert lookup.has_key(row['title']), "Expected Group with title: %r" % row['title']


@then("the '{group}' group contains:")
@then("the '{group}' group contains")
def group_contains_nodes(context, group):
    global fl_document
    global fl_app

    selected = findBy(fl_document._GROUPS, {"title": group})
    for row in context.table:
        if row['node'] == 'group':
            c = findBy(selected._CHILDREN, {
                "title": row['title']
            })
        else:
            c = findBy(selected._CHILDREN, {
                "type": row['node'],
                "title": row['title']
            })
        assert c != None, "Expected %r child %r not found" % (row['node'], row['title'])


@then("these nodes are connected in order:")
@then("these nodes are connected in order")
def nodes_are_connected(context):
    '''
     | group title | node | title |
    '''
    global fl_document
    global fl_app

    top = None
    for row in context.table:
        g = findBy(fl_document._GROUPS, {"title": row['group title']})
        if top is None:
            top = findBy(g._CHILDREN, {
                "type": row['node'],
                "title": row['title']
            })
            assert top is not None, "Cannot find node"
        else:
            next_node = findBy(g._CHILDREN, {
                "type": row['node'],
                "title": row['title']
            })
            assert next_node is not None, "Cannot find node"
            assert top._LINKS.__contains__(next_node), "Nodes are not linked"
