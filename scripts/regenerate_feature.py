# regenerate feature files from AST

# TODO
# load ast for the feature being regenerated

import os
import pickle
import sys

sys.path.append("/Library/Python/2.7/site-packages")

# from ASTutils import updateLineNumbers

# get selected nodes
count = 0
merged = []
# iterate through the selection - keep first node and remove all others, transferring edges to the first node
# print 'selected:', len(document.selection)
if len(document.selection) != 1:
    Application.alert('You must select one node within the feature you wish to update.')

featureFileName = None
feature = None

ge = document.selection[0]
# get the filename of the feature for this node
featureFileName = ge.user['filename']
with open(featureFileName) as myfile:
    count = sum(1 for line in myfile)
baseName = os.path.basename(featureFileName)
dirName = os.path.dirname(featureFileName)
pickleBaseName = os.path.splitext(baseName)[0] + '.pickle'
pickleFilePath = os.path.join(dirName, pickleBaseName)
# load the pickled AST for this feature
feature = pickle.load(open(pickleFilePath, "rb"))
# print feature
# print "initialising output"
output = ['\n'] * (count + 10)  # empty array of strings the same size as the input, plus a margin
# iterate through the AST, building up the output text in order of line number
for key, value in feature.items():
    if (key == 'comments'):
        for comment in value:
            # print comment['text'], comment['location']['line']
            output[comment['location']['line']] = comment['text']
    elif (key == 'tag'):
        for tag in value:
            # print tag['name']
            output[tag['location']['line']] = tag['name']
    elif (key == 'feature'):
        # print value['location']['line'], 'Feature: ', value['name']
        output[value['location']['line']] = 'Feature: ' + value['name']
        for featurekey, featurevalue in value.items():
            # if (featurekey == 'name'):
            #   print 'Feature', featurevalue
            #   #output[featurevalue['location']['line']] = 'Feature: ' + featurevalue['text'],
            # elif (featurekey == 'children'):
            if (featurekey == 'children'):
                for child in featurevalue:
                    if ('tags' in child):
                        for tag in child['tags']:
                            # print tag['location']['line'], tag['name']
                            output[tag['location']['line']] = tag['name']
                    if child['type'] == 'Background':
                        # print 'Background'
                        output[child['location']['line']] = 'Background: '
                    if child['type'] == 'Scenario':
                        # print 'Scenario', child['name']
                        output[child['location']['line']] = 'Scenario: ' + child['name']
                    if child['type'] == 'ScenarioOutline':
                        # print 'Scenario Outline', child['name']
                        output[child['location']['line']] = 'Scenario Outline: ' + child['name']
                    for step in child['steps']:
                        # print step['location']['line'], step['keyword'], step['text'], '\n'
                        step_text = "%s%s" % (step['keyword'], step['text'])
                        output[step['location']['line']] = step_text

# with open(featureFileName, 'w') as pickleHandle:
#      pickle.dump(feature, pickleHandle)

# update feature file
myfile = open(featureFileName, 'w')
line = 0
for line in range(count + 10):
    # print line, output[line]
    if output[line] != '\n':
        myfile.write(output[line] + '\n')
    else:
        myfile.write(output[line])
myfile.close()

document.clearSelection()
# print "Done"
Application.alert("Feature file updated")
