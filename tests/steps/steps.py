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


def find_nodes(feature, group, node, title):
    """
    Used by tests that have a table of elements:
     | feature | group title | node | title |

    Returns the first element that matches all the critera
    e.g. To select a feature only provide feature name
         To select a scenarios provide group, optionally narrow with feature
         To select node provide node and title, optionally narrow with feature and/or group

    Note:
        if feature is not provided, all features in the document will be considered
        if group is not provided, all scenarios will be considered

    :return: GraphElem from fl_document
    """
    global fl_document

    top = None
    search = fl_document.stub_groups
    if not (feature is None or feature == ""):
        top = find_by(search, {"title": feature})
        assert top is not None, "Cannot find Feature %r" % feature
        search = top.children

    if not (group is None or group == ""):
        top = find_by(search, {"title": group})
        assert top is not None, "Cannot find Group %r" % group
        search = top.children

    criteria = {}
    if not (node is None or node == ""):
        criteria["type"] = node
    if not (title is None or title == ""):
        criteria["title"] = title
    if not criteria == {}:
        top = find_by(search, criteria)
        assert top is not None, "Cannot find %r node %r" % (node, title)

    return top

@given("I am running FlyingLogic with a new document")
def new_document(context):
    global fl_document
    global fl_app
    fl_app = Application()
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


@when("I run the script '{scriptname}' outputting to a temporary file '{tempfilename}'")
def run_script_export(context, scriptname, tempfilename):
    global fl_document
    global fl_app
    select_file(context, tempfilename)
    run_script(context, scriptname)


@when("I run the script '{scriptname}'")
def run_script(context, scriptname):
    global fl_document
    global fl_app
    global _DEBUG
    scriptname = "scripts/" + scriptname + ".py"

    exec (compile(open(scriptname, "rb").read(), scriptname, 'exec'), {
        'scriptParentDirectory': "scripts",
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
            assert top is not None, "Cannot find %s node %s" % (row['node'], row['title'])
        else:
            next_node = find_by(g.children, {
                "type": row['node'],
                "title": row['title']
            })
            assert next_node is not None, "Cannot find %s node %s" % (row['node'], row['title'])
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


@then("the files are the same '{expected}' and '{actual}'")
def step_impl(context, expected, actual):
    import difflib
    original = open("Samples/" + expected, "rb").read().splitlines(True)
    new_file = open("Samples/" + actual, "rb").read().splitlines(True)
    delta = list(difflib.ndiff(original, new_file, linejunk=difflib.IS_LINE_JUNK))

    out = ("Files are different ('-' is missing from %s, '+' is extra) :\n" % actual) + ''.join(delta)
    # if all lines should start with space (+/- indicates a change)
    for x in delta:
        assert x.startswith(" "), out


@when("I deselect all nodes")
def clear_selection(context):
    global fl_document
    fl_document.clearSelction()


@when("I select the node")
@when("I select the node:")
@when("I select the nodes")
@when("I select the nodes:")
def select_nodes(context):
    global fl_document

    for row in context.table:
        fl_document.selection.append(find_nodes(row.get('feature'), row.get('group title'), row.get('node'), row.get('title')))


@given("I want to add a {dialog}")
@given("I want to add a {dialog}:")
def populate_dialog(context, dialog):
    """
      | Field       | Value |
      | Risk Type:  |       |
      | Risk:       |       |
      | Likelihood: |       |
      | Severity:   |       |
    """
    global fl_document
    global fl_app

    kvp = {'Option': "OK"}
    for row in context.table:
        kvp[row['Field']] = row['Value']

    fl_app.stub_request_response = {dialog: kvp}
    pass


list_of_nodes_to_check = []


@then("will check these nodes")
@then("will check these nodes:")
def step_impl(context):
    global list_of_nodes_to_check
    list_of_nodes_to_check = []

    for row in context.table:
        list_of_nodes_to_check.append(find_nodes(row.get('feature'), row.get('group title'), row.get('node'), row.get('title')))


@step("expect to see the '{symbol_name}' symbol:")
def step_impl(context, symbol_name):
    global list_of_nodes_to_check

    for n in list_of_nodes_to_check:
        assert n.symbol == symbol_name, "symbol is '%s', expected '%s'" % (n.symbol, symbol_name)


@step("expect to see have an annotation")
@step("expect to see have an annotation:")
def step_impl(context):
    import difflib

    global list_of_nodes_to_check
    expected = context.text.strip()

    for n in list_of_nodes_to_check:
        actual = n.annotationEditor.plainText.strip()

        delta = list(difflib.ndiff([expected], [actual]))
        out = ("Strings are not the same for %r:\n" % n.title) + ''.join(delta)
        # if all lines should start with space (+/- indicates a change)
        for x in delta:
            assert x.startswith(" "), out
