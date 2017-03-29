import sys

#
# TODO: make any background Givens the parent of any other givens within the same file
#       store the filename / URL for each file in the attributes of each node
#
# TODO: component tree link - as a user, I want to link behaviour nodes to component nodes so that I can
#       - see all the scenarios that are impacted when a component changes
#       - understand the emergent structure of the system

importItemLabel = "Import Diagram from Cucumber Feature File"

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

# noinspection PyPep8
from gherkin.token_scanner import TokenScanner
# noinspection PyPep8
from gherkin.parser import Parser

document.orientation = Application.ORIENTATION_TOP_TO_BOTTOM
document.bias = Application.BIAS_START
document.addEntityAsSuccessor = True

# ask for FeatureFile
featureFileName = Application.askForFile(Application.lastAskDirectory, False)
contents = open(featureFileName, 'r').read()
parser = Parser()
feature = parser.parse(TokenScanner(contents))


def set_user_attributes(node, child, step=None):
    """
    Adds meta data from Feature file to the selected entity
    This is used to regenerate the feature file
    :param step:
    :param child:
    :rtype: None
    :param node: Flying Logic Entity
    """
    global document
    # document.modifyUserAttribute([node], "line", child['location']['line'])
    # document.modifyUserAttribute([node], "column", child['location']['column'])
    if step is not None:
        document.modifyUserAttribute([node], "keyword", step['keyword'])
    document.modifyUserAttribute([node], "type", child['type'])


def capture_tags(group, element_with_tags):
    global document
    if "tags" in element_with_tags:
        tags = []
        for t in element_with_tags["tags"]:
            tags.append(t["name"])
        document.modifyUserAttribute([group], "tags", ",".join(tags))


# render AST
newFeature = document.newGroup(None)[0]  # no need to clearSelection each iteration
document.modifyUserAttribute([newFeature], "filename", featureFileName)
document.modifyUserAttribute([newFeature], "type", 'Feature')
newFeature.color = Color.GREEN
capture_tags(newFeature, feature['feature'])

utils._DEBUG = False
utils.debug("Feature File AST as produced by parser", pprint=feature)

interFeatureLinks = []

for key, value in feature['feature'].items():
    currentScenario = None
    currentNode = None
    currentBackground = None

    # maintain these to allow correct connection Background to all Scenarios
    in_background = False
    # noinspection PyRedeclaration
    first_in_scenario = False
    last_background_node = None

    if key == 'name':
        newFeature.title = value
    elif key == 'description':
        # preserve comment
        newFeature.annotationEditor.insert(value, {})

        # if there are risks render the balloon
        if len(utils.decode_risks(value)) > 0:
            newFeature.symbol = document.getSymbolByName(Application.WRITING_BALLOON_SHOUT)

        # if it has inter-feature link, save for later re-creation
        interFeatureLinks = utils.decode_inter_feature_link(value)
    elif key == 'children':
        for child in value:

            utils.debug(key, value, '\n')
            if child['type'] == 'Background':
                #utils.debug('Starting', child['type'])
                in_background = True
                newBackground = document.newGroup(None)[0]
                newBackground.title = 'Background'
                document.modifyAttribute([newBackground], "parent", newFeature)
                set_user_attributes(newBackground, child)
                currentBackground = newBackground
                currentGroup = newBackground
            elif child['type'] == 'Scenario' or child['type'] == 'ScenarioOutline':
                #utils.debug('Starting', child['type'], child['name'])
                in_background = False
                first_in_scenario = True
                newClass = document.getEntityClassByName('Given')
                newScenario = document.newGroup(None)[0]
                newScenario.title = child['name']
                currentScenario = newScenario
                currentGroup = newScenario
                currentNode = None
                document.modifyAttribute([newScenario], "parent", newFeature)
                set_user_attributes(newScenario, child)
                capture_tags(newScenario, child)

            # preserve comment and risk balloon
            if child.has_key('description'):
                currentGroup.annotationEditor.insert(child['description'], {})
                if len(utils.decode_risks(child['description'])) > 0:
                    currentGroup.symbol = document.getSymbolByName(Application.WRITING_BALLOON_SHOUT)



            for step in child['steps']:
                #utils.debug("starting step", step['keyword'])
                if step['keyword'] == u'Given ':
                    newClass = document.getEntityClassByName('Given')
                elif step['keyword'] == u'When ':
                    newClass = document.getEntityClassByName('When')
                elif step['keyword'] == u'Then ':
                    newClass = document.getEntityClassByName('Then')
                elif step['keyword'] == u'And ':
                    newClass = document.getEntityClassByName('And')
                # TODO: Gherkin 'And' is really a repeat of the previous Keyword
                #       could preserve that intent when building the Flying Logic Representation
                #       with 'AND GIVEN' 'AND WHEN' and 'AND THEN' nodes?

                else:
                    assert false, "Unknown keyword %r in Feature File Steps" % step['keyword']

                # Create a new Node and link it to the previous
                currentNode = document.addEntityToTarget(newClass, currentNode)[0]
                currentNode.title = step['text']
                if currentScenario is None:
                    document.modifyAttribute([currentNode], "parent", currentBackground)
                else:
                    document.modifyAttribute([currentNode], "parent", currentScenario)
                set_user_attributes(currentNode, child, step)

                # while processing the background
                # associate the current element (first in a scenario)
                # with the last background node
                #utils.debug("in_background = ", in_background)
                if in_background:
                    last_background_node = currentNode
                elif first_in_scenario:
                    if last_background_node is not None:
                        document.connect(last_background_node, currentNode)
                    first_in_scenario = False

# create a catalogue of all the entities in the document tagged with feature/scenario/keyword/text
catalogue = []
for elem in document.all:
    if elem.isGroup and elem.color == Color.GREEN:
        feature = elem.title
        for child in elem.children:
            if child.isGroup:
                scenario = child.title
                for step in child.children:
                    if step.isEntity:
                        keyword = step.user["keyword"]
                        text = step.title
                        entity = {'entity': step, 'feature': feature, 'scenario': scenario, 'keyword': keyword, 'text': text}
                        catalogue.append(entity)
    
# recreate inter-feature link provided both features exist
for link in interFeatureLinks:
    utils.debug("InterFeatureLink: " + str(link))
    src = {}
    tgt = {}
    for entity in catalogue:
        if (link['from_feature'] == entity['feature'] and link['from_scenario'] == entity['scenario'] and link['from_keyword'] == entity['keyword'] and link['from_text'] == entity['text']):
            src = entity
        elif (link['to_feature'] == entity['feature'] and link['to_scenario'] == entity['scenario'] and link['to_keyword'] == entity['keyword'] and link['to_text'] == entity['text']):
            tgt = entity
    if src and tgt:
        document.connect(src['entity'], tgt['entity'])
    
 
