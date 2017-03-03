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
# TODO: Add Tests for FLStub Class

if not dir().__contains__("_DEBUG"):
    _DEBUG = False


class FLStub(object):
    '''
    Generic Stub BaseClass

    1. Assignment to variables will saved to a dictonary for future reads
        Names starting with an _ have special meaning.
    2. Reads of previously assigned variables will return the known result
    3. Reads of unknown variables will return a Method
    4. Calls to that method will be logged
       and if a previous _<MethodName>Response that will be returned
       otherwise nothing will be returned.

    '''

    # instance variables
    _STUB_DICT = None
    _METHODS_CALLED = None
    _METHOD_RESPONSES = None

    def __init__(self):
        self._STUB_DICT = {}
        self._METHODS_CALLED = []
        self._METHOD_RESPONSES = {}

    def __setattr__(self, key, value):
        # bail when accessing instance varables
        if dir(self).__contains__(key):
            return super.__setattr__(self, key, value)
        if key.startswith("_"):
            if key.endswith("Response"):
                if _DEBUG:
                    print "%r : Storing Response for future call to %r, value %r \n" % (self, key, value)
                if not self._METHOD_RESPONSES.has_key(key):
                    self._METHOD_RESPONSES[key] = []
                self._METHOD_RESPONSES[key].append(value)
            else:
                return super.__setattr__(self, key, value)
        else:
            if _DEBUG:
                print "%r : Storing %r, value %r \n" % (self, key, value)
        self._STUB_DICT[key] = value

    def __getattr__(self, name):
        if (self._STUB_DICT.has_key(name)):
            return self._STUB_DICT[name]

        def _missingFunction(*args, **kwargs):
            if self._METHOD_RESPONSES.has_key("_" + name + "Response") and \
                            len(self._METHOD_RESPONSES["_" + name + "Response"]) > 0:
                ret = self._METHOD_RESPONSES["_" + name + "Response"].pop(0)
                if _DEBUG:
                    print "%r : Stub method %r was called returning %r" % (self, name, ret)
                return ret
            else:
                self._METHODS_CALLED.append({'name': name, 'args': args, 'kwargs': kwargs})
                if _DEBUG:
                    print "%r : Warning return value for %r has not been set prior to application under test calling it" % (self, name)
                return None

        self._STUB_DICT[name] = _missingFunction
        return _missingFunction


class Color(FLStub):
    GREEN = 'green'


class GraphElem(FLStub):
    UserAttributes = None
    Attributes = None
    _LINKS = None

    def __init__(self):
        super(GraphElem, self).__init__()
        self.UserAttributes = {}
        self.Attributes = {}
        self._LINKS = []


class Group(GraphElem):
    _CHILDREN = None

    def __init__(self):
        super(Group, self).__init__()
        self._CHILDREN = []


class Document(FLStub):
    _GROUPS = None
    _ENTITIES = None

    def __init__(self):
        super(Document, self).__init__()
        self._GROUPS = []
        self._ENTITIES = {}

    def newGroup(self, children):
        '''
        creates a new group containing all elements in children, which
        must be a list, and returns a list of new elements, Group instance
        first
        '''
        g = Group()
        if children != None:
            g._CHILDREN.extend(children)
        self._GROUPS.append(g)
        return [g]

    def getEntityClassByName(self, name_or_tuple):
        '''
        return the EntityClass instance based on one of two matching
        criteria: if name_or_tuple is a string, then the parameter is the
        name of an entity class to find (preference is given to a custom
        entity class if the are duplicate names); otherwise, if name_
        or_tuple is a tuple, then the parameter must be the tuple (domain_name,
        entity_class_name) identifying an entity class (see
        also the Domain class method getEntityClassByName)

        Examples:
            entityclass = document.getEntityClassByName(‘Goal’)
            entityclass = document.getEntityClassByName( (‘Prerequisite Tree, ‘Milestone’ ) )
        '''
        if not self._ENTITIES.has_key(name_or_tuple):
            self._ENTITIES[name_or_tuple] = []
        e = GraphElem()
        e.type = name_or_tuple
        self._ENTITIES[name_or_tuple].append(e)
        return e

    def addEntityToTarget(self, entityclass, vertexElem):
        '''
        adds a new entity to the graph with class entityclass. The newly
        created entity is connected to the given vertexElem per the setting
        of addEntityAsSuccessor. If vertexElem is None, does not
        connect the new entity to any element. Returns a list of new
        elements, Entity instance first
        '''
        if vertexElem is not None:
            self.connect(vertexElem, entityclass)
        return [entityclass]

    def modifyUserAttribute(self, list, name, value):
        '''
        modify a particular user defined attribute name to value for every
        instance of GraphElem in list
        '''
        if _DEBUG:
            print "modifyUserAttribute name= %r, value= %r \n" % (name, value)

        for e in list:
            e.UserAttributes[name] = value

    def modifyAttribute(self, listOfGraphElem, name, value):
        '''
        modify a particular built-in attribute name (a string) to value
        for every instance of GraphElem in list
        '''
        if _DEBUG:
            print "modifyAttribute name= %r, value= %r \n" % (name, value)

        for e in listOfGraphElem:
            e.Attributes[name] = value
            if (name == 'parent'):
                assert isinstance(value, Group)
                value._CHILDREN.append(e)
                if _DEBUG: print "added %r as child in %r \r" % (e, value._CHILDREN)

    def connect(self, fromElem, toElem):
        '''
        connects an edge from the fromElem to the toElem, where the
        elements must be an entity, junctor or edge. Returns a list of
        new elements
        :type fromElem: GraphElem
        :type toElem: GraphElem
        '''
        assert isinstance(fromElem, GraphElem)
        assert isinstance(toElem, GraphElem)
        fromElem._LINKS.append(toElem)
        pass
