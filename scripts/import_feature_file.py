#TODO
#make any background Givens the parent of any other givens within the same file
#store the filename / URL for each file in the attributes of each node
#tag support - parse existing tags into the info for that node
#component tree link - as a user, I want to link behaviour nodes to component nodes so that I can 
# - see all the scenarios that are impacted when a component changes 
# - understand the emergent structure of the system

import os
import pickle 
import sys
sys.path.append("/Library/Python/2.7/site-packages")
#sys.path.append(scriptParentDirectory)
from javax.swing import Box, BoxLayout, JLabel, JCheckBox, JComboBox, JTextField
#from gherkin.parser import Parser
#from gherkin.parser import Lexer 
from gherkin.token_scanner import TokenScanner
from gherkin.token_matcher import TokenMatcher
from gherkin.parser import Parser
from gherkin.errors import ParserError

document.orientation = Application.ORIENTATION_TOP_TO_BOTTOM
document.bias = Application.BIAS_START 
document.addEntityAsSuccessor = True

#ask for FeatureFile
featureFileName = Application.askForFile(Application.lastAskDirectory,False)
file = open(featureFileName, 'r')
contents = file.read()
parser=Parser()
feature=parser.parse(TokenScanner(contents))

#setup pickle file for storing AST
baseName = os.path.basename(featureFileName)
#print baseName
dirName = os.path.dirname(featureFileName)
pickleBaseName = os.path.splitext(baseName)[0] + '.pickle'
pickleFilePath = os.path.join(dirName,pickleBaseName)
#print pickleFilePath
#NOTE: import will overwrite any existing pickle for this feature
with open(pickleFilePath, 'w') as pickleHandle:
    pickle.dump(feature, pickleHandle)

#render AST
newFeature = document.newGroup(None)[0] # no need to clearSelection each iteration
document.modifyUserAttribute([newFeature],"filename",featureFileName)
newFeature.color = Color.GREEN
print feature
for key,value in feature['feature'].items():
    currentScenario = None
    #print key, value, '\n'
    if (key == 'name'):
         newFeature.title = value
    if (key == 'children'):
         #print value
         for child in value:
            if child['type'] == 'Background':
               #print 'Background'
               eCls = document.getEntityClassByName('Given')
               newBackground = document.newGroup(None)[0] # no need to clearSelection each iteration
               newBackground.title = 'Background' 
               document.modifyAttribute([newBackground],"parent",newFeature)
               document.modifyUserAttribute([newBackground],"filename",featureFileName)
               document.modifyUserAttribute([newBackground],"line",child['location']['line'])
               document.modifyUserAttribute([newBackground],"column",child['location']['column'])
               #print "line", child['location']['line']
               #print "col", child['location']['column']
               currentBackground = newBackground
            elif child['type'] == 'Scenario' or child['type'] == 'ScenarioOutline':
               #print 'Scenario', child['name'], '\n'
               eCls = document.getEntityClassByName('Given')
               newScenario = document.newGroup(None)[0] # no need to clearSelection each iteration
               newScenario.title = child['name'] 
               currentScenario = newScenario
               currentNode = None 
               document.modifyAttribute([newScenario],"parent",newFeature)
               document.modifyUserAttribute([newScenario],"filename",featureFileName)
               document.modifyUserAttribute([newScenario],"line",child['location']['line'])
               document.modifyUserAttribute([newScenario],"column",child['location']['column'])
            for step in child['steps']:
                if step['keyword'] == u'Given ':
                    #print step['keyword'], step['text'], '\n'
                    eCls = document.getEntityClassByName('Given')
                    newGiven = document.addEntityToTarget(eCls, None)[0] # no need to clearSelection each iteration
                    newGiven.title = step['text'] 
                    currentNode = newGiven
                    if currentScenario is None:
                       document.modifyAttribute([newGiven],"parent",currentBackground)
                    else:
                       document.modifyAttribute([newGiven],"parent",currentScenario)
                    document.modifyUserAttribute([newGiven],"filename",featureFileName)
                    document.modifyUserAttribute([newGiven],"line",step['location']['line'])
                    document.modifyUserAttribute([newGiven],"column",step['location']['column'])
                if step['keyword'] == u'When ':
                    #print step['keyword'], step['text'], '\n' 
                    eCls = document.getEntityClassByName('When')
                    newWhen = document.addEntityToTarget(eCls, currentNode)[0] # no need to clearSelection each iteration
                    newWhen.title = step['text'] 
                    currentNode = newWhen
                    document.modifyAttribute([newWhen],"parent",newScenario)
                    document.modifyUserAttribute([newWhen],"filename",featureFileName)
                    document.modifyUserAttribute([newWhen],"line",step['location']['line'])
                    document.modifyUserAttribute([newWhen],"column",step['location']['column'])
                if step['keyword'] == u'Then ':
                    #print step['keyword'], step['text'], '\n'
                    eCls = document.getEntityClassByName('Then')
                    newThen = document.addEntityToTarget(eCls, currentNode)[0] # no need to clearSelection each iteration
                    newThen.title = step['text'] 
                    currentNode = newThen
                    document.modifyUserAttribute([newThen],"filename",featureFileName)
                    document.modifyUserAttribute([newThen],"line",step['location']['line'])
                    document.modifyUserAttribute([newThen],"column",step['location']['column'])
                    #print 'Scenario: ', newScenario
                    #print 'Then: ', newThen
                    #document.modifyAttribute([newThen],"parent",newScenario)
                if step['keyword'] == u'And ':
                    #print step['keyword'], step['text'], '\n'
                    eCls = document.getEntityClassByName('And')
                    newAnd = document.addEntityToTarget(eCls, currentNode)[0] # no need to clearSelection each iteration
                    newAnd.title = step['text'] 
                    currentNode = newAnd
                    document.modifyUserAttribute([newAnd],"filename",featureFileName)
                    document.modifyUserAttribute([newAnd],"line",step['location']['line'])
                    document.modifyUserAttribute([newAnd],"column",step['location']['column'])



