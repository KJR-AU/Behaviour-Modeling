#requirement_text = askForString()
#requirement_ID = askForInteger()
from javax.swing import Box, BoxLayout, JLabel, JCheckBox, JComboBox, JTextField


masterBox = Box(BoxLayout.Y_AXIS)

# type
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Node Type: "))
nodeTypeComboBox = JComboBox(['Given', 'When', 'Then', 'And',])
controlBox.add(nodeTypeComboBox)
masterBox.add(controlBox)

# component name
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Text: "))
componentNameField = JTextField(20)
controlBox.add(componentNameField)
masterBox.add(controlBox)

# notes
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Notes: "))
requirementTextField = JTextField(100)
controlBox.add(requirementTextField)
masterBox.add(controlBox)

# requirement trace
#controlBox = Box(BoxLayout.X_AXIS)
#controlBox.add(JLabel("Requirement ID: "))
#requirementIDField = JTextField(5)
#controlBox.add(requirementIDField)
#masterBox.add(controlBox)

# requirement URL
#controlBox = Box(BoxLayout.X_AXIS)
#controlBox.add(JLabel("Requirement URL: "))
#requirementURLField = JTextField(20)
#controlBox.add(requirementURLField)
#masterBox.add(controlBox)

#requirement_text = Application.askForString("Requirement text:","As a user I...")

# display dialog and collect options
if 1 == Application.request("New Requirement", masterBox, ("Cancel", "OK")):
    #create the new requirement node
    nodeType = nodeTypeComboBox.getSelectedItem()
    eCls = document.getEntityClassByName(nodeType)
    if len(document.selection) > 0:
        selectedNode = document.selection[0]
        newRequirement = document.addEntityToTarget(eCls, selectedNode)[0] # no need to clearSelection each iteration
    else:
        newRequirement = document.addEntityToTarget(eCls, None)[0] # no need to clearSelection each iteration
    componentName = componentNameField.text
    newRequirement.title = componentName
    #newRequirement.annotation = requirementTextField.text
    editor = newRequirement.annotationEditor
    #if requirementURLField.text != '':
    #    editor.insert(requirementTextField.text, { Application.LINK: requirementURLField.text  } )
    #else:
    #    editor.insert(requirementTextField.text, { })
    editor.flush()
    newRequirement.user['keyword'] = nodeType
    newRequirement.user['type'] = 'Scenario' #default to scenario for now
    #newRequirement.user['ReqID'] = requirementIDField.text


