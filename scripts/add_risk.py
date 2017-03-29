import sys

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

# likelihood
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Likelihood: "))
riskLikelihood = JComboBox(['Low', 'Medium', 'High', 'Very High'])
controlBox.add(riskLikelihood)
masterBox.add(controlBox)

# severity
controlBox = Box(BoxLayout.X_AXIS)
controlBox.add(JLabel("Severity: "))
riskSeverity = JComboBox(['Low', 'Medium', 'High', 'Very High'])
controlBox.add(riskSeverity)
masterBox.add(controlBox)

# display dialog and collect options
if document.hasSelection == True:
    if not document.selection[0].isGroup:
        Application.alert("You must select a Feature or Scenario to add a risk.")

    if 1 == Application.request("New Risk", masterBox, ("Cancel", "OK")):
        document.addEntityAsSuccessor = True
        selectedEntity = document.selection[0]
        editor = selectedEntity.annotationEditor
        editor.insert(utils.encode_risk({"Risk": riskNameField.text,
                                         "Type": riskTypeComboBox.getSelectedItem(),
                                         "Likelihood": riskLikelihood.getSelectedItem(),
                                         "Severity": riskSeverity.getSelectedItem()}), {})
        editor.flush()
        selectedEntity.symbol = document.getSymbolByName(Application.WRITING_BALLOON_SHOUT)
else:
    Application.alert("Please select an Feature or Scenario to add a risk.")
