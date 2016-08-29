#requirement_text = askForString()
#requirement_ID = askForInteger()
from javax.swing import Box, BoxLayout, JLabel, JCheckBox, JComboBox, JTextField


masterBox = Box(BoxLayout.Y_AXIS)
    
# type
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Risk Type: "))
riskTypeComboBox = JComboBox(['Functional', 'Performance', 'Security', 'Usability', 'Compatability', 'Portability', 'Maintainability'])
controlBox.add(riskTypeComboBox)
masterBox.add(controlBox)

# risk name
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Risk: "))
riskNameField = JTextField(20)
controlBox.add(riskNameField)
masterBox.add(controlBox)

# description text
#controlBox = Box(BoxLayout.X_AXIS)
#controlBox.add(JLabel("Description: "))
#descriptionTextField = JTextField(100)
#controlBox.add(descriptionTextField)
#masterBox.add(controlBox)

# likelihood
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Likelihood: "))
riskLikelihood = JComboBox(['Low', 'Medium', 'High', 'Very High'])
controlBox.add(riskLikelihood)
masterBox.add(controlBox)

# requirement URL
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Severity: "))
riskSeverity = JComboBox(['Low', 'Medium', 'High', 'Very High'])
controlBox.add(riskSeverity)
masterBox.add(controlBox)


# display dialog and collect options
if document.hasSelection == True:
    if 1 == Application.request("New Risk", masterBox, ("Cancel", "OK")):
        #create the new risk node
        document.addEntityAsSuccessor = True
        #eCls = document.getEntityClassByName('Risk')
        #newRisk = document.addEntity(eCls)[0] # attach to currently selected node
        #newRisk.title = riskNameField.text
        selectedEntity = document.selection[0]
        editor = selectedEntity.annotationEditor
        editor.insert("Risk: [", { })
        editor.insert(riskNameField.text, { })
        editor.insert(" | Type: ", { })
        editor.insert(riskTypeComboBox.getSelectedItem(), { })
        editor.insert(" | Likelihood: ", { })
        editor.insert(riskLikelihood.getSelectedItem(), { })
        editor.insert(" | Severity: ", { })
        editor.insert(riskSeverity.getSelectedItem(), { })
        editor.insert("]\n", { })
        editor.flush()
        #if selectedEntity.user['HasRisks'] > 0:
            #selectedEntity.user['HasRisks'] = selectedEntity.user['HasRisks'] + 1
        #else:
        #    selectedEntity.user['HasRisks'] = 1
        #document.modifyAttribute([selectedEntity],"symbol",document.getSymbolByName("WRITING_BALLOON_SHOUT"))
        selectedEntity.symbol = document.getSymbolByName(Application.WRITING_BALLOON_SHOUT)
#else:
#    Application.alert("Please select an item").


