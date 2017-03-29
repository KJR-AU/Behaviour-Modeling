# coding=utf-8
#
# This file exists to supply stubs to fake FlyingLogicClasses when testing
# these are usually provided from within Flying Logic when executed as a script.
#
# Interface Specification is based on <http://flyinglogic.com/docs/Flying%20Logic%20Scripting%20Guide.pdf>
#
# Note: Do the bare minimum to get the tests to pass,
#       This is not a complete reimplementation of FlyingLogic Classes
#       only implement methods required to for tests with minimal dummy placeholders
#       will be used where no functionality is needed.
#

# TODO: Add Tests for FLStub Class, not verifying a passing test by running against real Flying Logic should ensure stub is accurate

import utils
import random

__all__ = ["FLStub", "Document", "Color", "Application"]


class FLStub(object):
    """
    Generic Stub BaseClass

    1. Assignment to variables will saved to a dictionary for future reads
        Names starting with an stub_ have special meaning.
    2. Reads of previously assigned variables will return the known result
    3. Reads of unknown variables will return a Method
    4. Calls to that method will be logged
       and if a previous stub_<MethodName>_response that will be returned
       otherwise nothing will be returned.

    """

    # instance variables
    stub_properties = None
    stub_methods_called = None
    stub_method_responses = None

    def __init__(self):
        self.stub_properties = {}
        self.stub_methods_called = []
        self.stub_method_responses = {}

    def __setattr__(self, key, value):
        # bail when accessing instance variables
        if dir(self).__contains__(key):
            return super(FLStub, self).__setattr__(key, value)
        if key.startswith("stub_"):
            if key.endswith("_response"):
                utils.debug("%r : Storing Response for future call to %r, value %r \n" % (self, key, value))
                if key not in self.stub_method_responses:
                    self.stub_method_responses[key] = []
                self.stub_method_responses[key].append(value)
            else:
                return super(FLStub, self).__setattr__(key, value)
        else:
            pass
            # utils.debug("%r : Storing %r, value %r \n" % (self, key, value))
        self.stub_properties[key] = value

    def __getattr__(self, name):

        # jython implementation of dir() uses these
        if name in ("__methods__", "__members__"):
            raise AttributeError()

        if name in self.stub_properties:
            return self.stub_properties[name]

        def _missing_function(*args, **kwargs):
            if "stub_" + name + "_response" in self.stub_method_responses and \
                            len(self.stub_method_responses["stub_" + name + "_response"]) > 0:
                ret = self.stub_method_responses["stub_" + name + "_response"].pop(0)
                utils.debug("%r : Stub method %r was called returning %r" % (self, name, ret))
                return ret
            else:
                self.stub_methods_called.append({'name': name, 'args': args, 'kwargs': kwargs})
                utils.debug("%r : Warning return value for %r has not been set prior to application under test calling it" % (self, name))
                return None

        self.stub_properties[name] = _missing_function
        return _missing_function


class TextEditor(FLStub):
    _text = None

    def __init__(self):
        super(TextEditor, self).__init__()
        self._text = ""

    @property
    def text(self):
        return "<html>" + self._text + "</html>"

    @property
    def plainText(self):
        return self._text

    def insert(self, text, attributes):
        self._text += text

    def flush(self):
        pass


class Application(FLStub):
    WRITING_BALLOON_SHOUT = "WRITING_BALLOON_SHOUT"

    def request(self, title_or_message, message_or_labels, labels_or_none=None):
        '''
        request( message, labels )
        request( title = "Request", message, labels )
            displays a request dialog with title (default "Request"( to the user to answer a question
            by making a selection among a set of buttons with labels (a tuple).

            Returns an integer matching the index of the label in the tuple.

            Note: the message can be a string or a Java Component object,
            allowing for the creation of a more complicated dialog
        '''

        if labels_or_none is None:
            # only passed message and labels
            title = "Request"
            message = title_or_message
            labels = message_or_labels
        else:
            # passed all three
            title = title_or_message
            message = message_or_labels
            labels = labels_or_none

        # if no response is defined, try "Cancel" button
        if not ("stub_request_response" in self.stub_method_responses and self.stub_request_response.has_key(title)):
            try:
                return labels.index("Cancel")
            except ValueError:
                # FIXME: don't know what FL does when user closes without selecting an button
                return -1

        if isinstance(message, str):
            # simple string message with custom buttons,
            # response based on button
            return self.stub_request_response[title]

        try:
            from javax.swing import Box, BoxLayout, JLabel, JCheckBox, JComboBox, JTextField
        except ImportError as e:
            assert False, "WARNING: Jython not present."

        # TODO: This assumes a simple grid lay out of 'rows' each containing:
        #  |  Label:  | Control |
        dialog_responses = self.stub_request_response[title]
        assert (isinstance(message, Box))
        for row in message.getComponents():
            assert (isinstance(row, Box))
            fields = row.getComponents()

            assert (2 == len(fields))
            assert (isinstance(fields[0], JLabel))
            label = fields[0].getText().strip()
            value = dialog_responses[label]

            if (isinstance(fields[1], JTextField)):
                fields[1].setText(value)
            elif (isinstance(fields[1], JComboBox)):
                fields[1].setSelectedItem(value)
            else:
                raise NotImplementedError("Unknown type" + fields[1].__class__)

        try:
            # return the desired response (default OK)
            return labels.index(dialog_responses['Option'])
        except ValueError:
            return -1


class Color(FLStub):
    GREEN = 'green'


# noinspection PyPep8Naming
class GraphElem(FLStub):
    # static
    _EIDCounter = 0
    _annotationEditor = None

    def __init__(self):
        super(GraphElem, self).__init__()
        GraphElem._EIDCounter += 1
        utils.debug("Creating element ", self, GraphElem._EIDCounter)
        self.eid = GraphElem._EIDCounter
        self.user = {}
        self.Attributes = {}
        self.links = []
        self.title = ""
        self.type = None
        self._annotationEditor = TextEditor()

    @property
    def parent(self): return self.Attributes['parent']

    @property
    def isEdge(self): return isinstance(self, VertexElem)

    @property
    def isGroup(self): return isinstance(self, Group)

    @property
    def isEntity(self): return True

    @property
    def annotationEditor(self): return self._annotationEditor

    def __str__(self):
        return "GraphElem(%i): %r" % (self.eid, self.title)


class Group(GraphElem):
    children = None

    def __init__(self):
        super(Group, self).__init__()
        self.type = "Group"
        self.children = []

    def __str__(self):
        return "Group(%i): %r" % (self.eid, self.title)


class VertexElem(GraphElem):
    source = None
    target = None

    def __init__(self, from_elem, to_elem):
        super(VertexElem, self).__init__()
        self.source = from_elem
        self.target = to_elem

    def __str__(self):
        return "VertexElem: %s => %s" % (self.source.eid, self.target.eid)


# noinspection PyPep8Naming
class Document(GraphElem):
    stub_groups = None
    stub_entities = None
    stub_entity_classes = {}
    selection = None

    def __init__(self):
        super(Document, self).__init__()
        self.stub_groups = []
        self.stub_entities = []
        self.stub_entity_classes = {}
        self.selection = []

    @property
    def all(self):
        """ the entire graph as a list of GraphElement instances """
        results = []
        results.extend(self.stub_groups)
        results.extend(self.stub_entities)
        for k in self.stub_entities:
            if len(k.links) > 0:
                results.extend(k.links)

        # Flying Logic does not guarantee the order of elements
        # so the stub can't either
        random.shuffle(results)
        return results

    def newGroup(self, children):
        """
        creates a new group containing all currently selected elements
        and returns a list of new elements, Group instance first
        """
        g = Group()
        if children is not None:
            g.children.extend(children)
        self.stub_groups.append(g)
        return [g]

    def getEntityClassByName(self, name_or_tuple):
        """
        return the EntityClass instance based on one of two matching
        criteria: if name_or_tuple is a string, then the parameter is the
        name of an entity class to find (preference is given to a custom
        entity class if the are duplicate names); otherwise, if name_
        or_tuple is a tuple, then the parameter must be the tuple (domain_name,
        entity_class_name) identifying an entity class (see
        also the Domain class method getEntityClassByName)

        Examples:
            entity_class = document.getEntityClassByName(‘Goal’)
            entity_class = document.getEntityClassByName( (‘Prerequisite Tree, ‘Milestone’ ) )
        """
        if name_or_tuple not in self.stub_entity_classes:
            entity_class = {'type': name_or_tuple}
            self.stub_entity_classes[name_or_tuple] = entity_class
        else:
            entity_class = self.stub_entity_classes[name_or_tuple]
        return entity_class

    def addEntityToTarget(self, entity_class, vertexElem):
        """
        adds a new entity to the graph with class entity_class. The newly
        created entity is connected to the given vertexElem per the setting
        of addEntityAsSuccessor. If vertexElem is None, does not
        connect the new entity to any element. Returns a list of new
        elements, Entity instance first
        """
        utils.debug("addEntityToTarget ", entity_class, vertexElem)
        e = GraphElem()

        e.type = entity_class["type"]
        self.stub_entities.append(e)
        if vertexElem is not None:
            self.connect(vertexElem, e)
        return [e]

    @staticmethod
    def modifyUserAttribute(nodes, name, value):
        """
        modify a particular user defined attribute name to value for every
        instance of GraphElem in list
        """

        for e in nodes:
            utils.debug("modifyUserAttribute name=%r, value=%r \n" % (name, value), pprint=e)
            e.user[name] = value

    @staticmethod
    def modifyAttribute(listOfGraphElem, name, value):
        """
        modify a particular built-in attribute name (a string) to value
        for every instance of GraphElem in list
        """
        utils.debug("modifyAttribute name= %r, value= %r" % (name, value))

        for e in listOfGraphElem:
            if name == 'parent':
                # special handling for parent attribute
                # to ensure element is always in parent.children
                if e.Attributes.has_key(name):
                    old_parent = e.Attributes[name]
                    assert isinstance(old_parent, Group)
                    old_parent.children.remove(e)
                assert isinstance(value, Group)
                utils.debug("added %r as child in %r" % (e, value.children))
                value.children.append(e)
            e.Attributes[name] = value

    @staticmethod
    def connect(fromElem, toElem):
        """
        connects an edge from the fromElem to the toElem, where the
        elements must be an entity, junctor or edge. Returns a list of
        new elements
        :type fromElem: GraphElem
        :type toElem: GraphElem
        """
        assert isinstance(fromElem, GraphElem)
        assert isinstance(toElem, GraphElem)
        x = VertexElem(fromElem, toElem)
        fromElem.links.append(x)

    def clearSelection(self):
        """
        deselects every element in the graph
        :return:
        """
        self.selection = []

    @property
    def hasSelection(self):
        """True if any elements in the graph are selected, otherwise False (read only)"""
        return len(self.selection) > 0

    def getSymbolByName(self, name):
        return name
