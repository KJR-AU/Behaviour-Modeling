import sys
from behave import *

_DEBUG = False
sys.path.append("scripts")
# noinspection PyPep8
import utils
# noinspection PyPep8
from FlyingLogicStub import *

use_step_matcher("parse")


fl_document = None
fl_app = None


def find_by(candidates, attrib):
    """
    Helper function to search a list of objects
    to find a match
    :param candidates:   list of object
    :param attrib: pairs of {attribute_name: expected_value}
    :return: first object matching criteria
             or None if no element is found
    """
    utils.debug("find_by called searching list", pprint=list)
    utils.debug("for first record with all attrib", pprint=attrib)

    for g in candidates:
        matched = True
        for a in attrib.keys():
            g_attrib = g.__getattr__(a)
            a_attrib = attrib[a]
            utils.debug("checking %s of %s (%r == %r) %s" % (a, g, g_attrib, a_attrib, g_attrib == a_attrib))
            matched &= g_attrib == a_attrib
        if matched:
            return g
    return None


@given("I am running FlyingLogic with a new document")
def new_document(context):
    global fl_document
    global fl_app
    fl_app = FLStub()
    fl_document = Document()


@given("I am running FlyingLogic with a document based on '{source_file}'")
def step_impl(context, source_file):
    global fl_document
    global fl_app
    new_document(context)
    select_file(context, source_file)
    run_script(context, "import_feature_file")


@given("I have a sample file '{filename}'")
def select_file(context, filename):
    global fl_document
    global fl_app
    fl_app.stub_askForFile_response = "Samples/" + filename


@when("I run the script '{scriptname}' outputting to a temporary file")
def run_script_export(context, scriptname):
    global fl_document
    global fl_app
    select_file(context, "temp.feature")
    run_script(context, scriptname)


@when("I run the script '{scriptname}'")
def run_script(context, scriptname):
    global fl_document
    global fl_app
    global _DEBUG
    scriptname = "scripts/" + scriptname + ".py"

    exec (compile(open(scriptname, "rb").read(), scriptname, 'exec'), {
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
    for g in fl_document.stub_groups:
        lookup[g.title] = g

    # verify they exist
    for row in context.table:
        assert row['title'] in lookup, "Expected Group with title: %r" % row['title']


@then("the '{group}' group contains:")
@then("the '{group}' group contains")
def group_contains_nodes(context, group):
    global fl_document
    global fl_app

    selected = find_by(fl_document.stub_groups, {"title": group})
    for row in context.table:
        if row['node'] == 'group':
            c = find_by(selected.children, {
                "title": row['title']
            })
        else:
            c = find_by(selected.children, {
                "type": row['node'],
                "title": row['title']
            })
        assert c is not None, "Expected %r child %r not found" % (row['node'], row['title'])


@then("these nodes are connected in order:")
@then("these nodes are connected in order")
def nodes_are_connected(context):
    """
     | group title | node | title |
    """
    global fl_document
    global fl_app

    top = None
    for row in context.table:
        g = find_by(fl_document.stub_groups, {"title": row['group title']})
        assert g is not None, "Cannot find Group %s" % row['group title']
        if top is None:
            top = find_by(g.children, {
                "type": row['node'],
                "title": row['title']
            })
            assert top is not None, "Cannot find node"
        else:
            next_node = find_by(g.children, {
                "type": row['node'],
                "title": row['title']
            })
            assert next_node is not None, "Cannot find node %s %s" % (row['node'], row['title'])
            assert next_node in map((lambda x: x.target), top.links), "Node (%s) is not linked by: %s" % (next_node, top.links)
            top = next_node


@then("A message is shown with '{expected_alert_message}'")
def step_impl(context, expected_alert_message):
    global fl_app

    found = False
    alert_messages = []
    for x in fl_app.stub_methods_called:
        if x["name"] == 'alert':
            alert_messages.append(x["args"][0])
            if x["args"][0] == expected_alert_message:
                found = True

    assert found, (("Expected Alert message '%s' was not found.\nActual messages were:\t" % expected_alert_message) + '%r' % alert_messages)


@then("the new file is the same as the original")
def step_impl(context):
    import difflib
    original = open("Samples/simple-background.feature", "rb").read().splitlines(True)
    new_file = open("Samples/temp.feature", "rb").read().splitlines(True)
    delta = difflib.ndiff(original, new_file, linejunk=difflib.IS_LINE_JUNK)

    out = ''.join(delta)
    # if all lines should start with space (+/- indicates a change)
    for x in delta:
        assert x.startswith(" "), out

    print("Files are the same")
