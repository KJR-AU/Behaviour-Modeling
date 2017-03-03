#
# TODO: make any background Givens the parent of any other givens within the same file
#       store the filename / URL for each file in the attributes of each node
#
# TODO: tag support - parse existing tags into the info for that node
#
# TODO: component tree link - as a user, I want to link behaviour nodes to component nodes so that I can
#       - see all the scenarios that are impacted when a component changes
#       - understand the emergent structure of the system

import os
import pickle
import sys

# When executed as part of test suite debugging may be turned on.
# default to off
if not dir().__contains__("_DEBUG"):
    _DEBUG = False


def debug(*args):
    '''
    Logs messages with stack trace style like content to assist debugging
    '''
    if _DEBUG:
        caller = sys._getframe().f_back
        print('  File "%s", line %i: ' % (caller.f_code.co_filename, caller.f_lineno), args)



sys.path.append("/Library/Python/2.7/site-packages")

from gherkin.token_scanner import TokenScanner
from gherkin.parser import Parser

document.orientation = Application.ORIENTATION_TOP_TO_BOTTOM
document.bias = Application.BIAS_START
document.addEntityAsSuccessor = True

# ask for FeatureFile
featureFileName = Application.askForFile(Application.lastAskDirectory, False)
file = open(featureFileName, 'r')
contents = file.read()
parser = Parser()
feature = parser.parse(TokenScanner(contents))

# setup pickle file for storing AST
baseName = os.path.basename(featureFileName)
debug(baseName)
dirName = os.path.dirname(featureFileName)
pickleBaseName = os.path.splitext(baseName)[0] + '.pickle'
pickleFilePath = os.path.join(dirName, pickleBaseName)
debug(pickleFilePath)
# NOTE: import will overwrite any existing pickle for this feature
with open(pickleFilePath, 'w') as pickleHandle:
    pickle.dump(feature, pickleHandle)


def set_user_attributes(node):
    """
    Adds meta data from Feature file to the selected entity
    :rtype: None
    :param node: Flying Logic Entity
    """
    document.modifyUserAttribute([node], "filename", featureFileName)
    document.modifyUserAttribute([node], "line", child['location']['line'])
    document.modifyUserAttribute([node], "column", child['location']['column'])

# render AST
newFeature = document.newGroup(None)[0]  # no need to clearSelection each iteration
document.modifyUserAttribute([newFeature], "filename", featureFileName)
newFeature.color = Color.GREEN
debug(feature)
for key, value in feature['feature'].items():
    currentScenario = None
    currentNode = None
    currentBackground = None

    # maintain these to allow correct connection Background to all Scenarios
    in_background = False
    first_in_scenario = False
    last_background_node = None

    debug(key, value, '\n')
    if key == 'name':
        newFeature.title = value
    if key == 'children':
        debug(value)
        for child in value:
            if child['type'] == 'Background':
                debug('Starting', child['type'])
                in_background = True
                eCls = document.getEntityClassByName('Given')
                newBackground = document.newGroup(None)[0]
                newBackground.title = 'Background'
                document.modifyAttribute([newBackground], "parent", newFeature)
                set_user_attributes(newBackground)
                currentBackground = newBackground
            elif child['type'] == 'Scenario' or child['type'] == 'ScenarioOutline':
                debug('Starting', child['type'], child['name'])
                in_background = False
                first_in_scenario = True
                eCls = document.getEntityClassByName('Given')
                newScenario = document.newGroup(None)[0]
                newScenario.title = child['name']
                currentScenario = newScenario
                currentNode = None
                document.modifyAttribute([newScenario], "parent", newFeature)
                set_user_attributes(newScenario)
            for step in child['steps']:
                debug(step['keyword'])
                if step['keyword'] == u'Given ':
                    eCls = document.getEntityClassByName('Given')
                    newGiven = document.addEntityToTarget(eCls, None)[0]
                    newGiven.title = step['text']
                    currentNode = newGiven
                    if currentScenario is None:
                        document.modifyAttribute([newGiven], "parent", currentBackground)
                    else:
                        document.modifyAttribute([newGiven], "parent", currentScenario)
                    set_user_attributes(currentNode)
                elif step['keyword'] == u'When ':
                    eCls = document.getEntityClassByName('When')
                    newWhen = document.addEntityToTarget(eCls, currentNode)[0]
                    newWhen.title = step['text']
                    currentNode = newWhen
                    document.modifyAttribute([newWhen], "parent", newScenario)
                    set_user_attributes(currentNode)
                elif step['keyword'] == u'Then ':
                    eCls = document.getEntityClassByName('Then')
                    newThen = document.addEntityToTarget(eCls, currentNode)[0]
                    newThen.title = step['text']
                    currentNode = newThen
                    document.modifyAttribute([newThen], "parent", newScenario)
                    set_user_attributes(currentNode)
                elif step['keyword'] == u'And ':
                    # TODO: Gherkin 'And' is really a repeat of the previous Keyword
                    #       could preserve that intent when building the Flying Logic representation
                    #       with 'AND GIVEN' 'AND WHEN' and 'AND THEN' nodes?
                    eCls = document.getEntityClassByName('And')
                    newAnd = document.addEntityToTarget(eCls, currentNode)[0]
                    newAnd.title = step['text']
                    currentNode = newAnd
                    set_user_attributes(currentNode)
                else:
                    assert false, "Unknown keyword %r in Feature File Steps" % step['keyword']

                # while processing the background
                # associate the current element (first in a scenario)
                # with the last background node
                debug("in_background = ", in_background)
                if in_background:
                    last_background_node = currentNode
                elif first_in_scenario:
                    if last_background_node is not None:
                        document.connect(last_background_node, currentNode)
                    first_in_scenario = False
