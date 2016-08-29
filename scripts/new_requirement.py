#requirement_text = askForString()
#requirement_ID = askForInteger()
from javax.swing import Box, BoxLayout, JLabel, JCheckBox, JComboBox, JTextField


masterBox = Box(BoxLayout.Y_AXIS)
    
# type
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Node Type: "))
nodeTypeComboBox = JComboBox(['State', 'Event', 'Conditional', 'External Input', 'External Output',])
controlBox.add(nodeTypeComboBox)
masterBox.add(controlBox)

# component name
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Component Name: "))
componentNameField = JTextField(20)
controlBox.add(componentNameField)
masterBox.add(controlBox)

# requirement text
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Requirement Text: "))
requirementTextField = JTextField(100)
controlBox.add(requirementTextField)
masterBox.add(controlBox)

# requirement trace
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Requirement ID: "))
requirementIDField = JTextField(5)
controlBox.add(requirementIDField)
masterBox.add(controlBox)

# requirement URL
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Requirement URL: "))
requirementURLField = JTextField(20)
controlBox.add(requirementURLField)
masterBox.add(controlBox)

#requirement_text = Application.askForString("Requirement text:","As a user I...")

# display dialog and collect options
if 1 == Application.request("New Requirement", masterBox, ("Cancel", "OK")):
    #create the new requirement node
    nodeType = nodeTypeComboBox.getSelectedItem()
    eCls = document.getEntityClassByName(nodeType)
    newRequirement = document.addEntityToTarget(eCls, None)[0] # no need to clearSelection each iteration
    componentName = componentNameField.text
    newRequirement.title = componentName
    #newRequirement.annotation = requirementTextField.text
    editor = newRequirement.annotationEditor
    if requirementURLField.text != '':
        editor.insert(requirementTextField.text, { Application.LINK: requirementURLField.text  } )
    else:
        editor.insert(requirementTextField.text, { })
    editor.flush()
    newRequirement.user['ReqID'] = requirementIDField.text


