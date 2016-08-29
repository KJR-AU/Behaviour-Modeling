#regenerate feature files
#is there a way to pickle the original AST and just make changes to the AST when we make other changes 
#e.g. turn merged steps into comments, update tags, etc etc - that way when we need to regenerate, we just read the relevant
#pickled AST and serialise 


import sys
sys.path.append("/Library/Python/2.7/site-packages")
from javax.swing import Box, BoxLayout, JLabel, JCheckBox, JComboBox, JTextField

document.orientation = Application.ORIENTATION_TOP_TO_BOTTOM
document.bias = Application.BIAS_START 
document.addEntityAsSuccessor = True

#for each top level group (which should be a feature file)
#create the matching feature file
  #for each child group (which should be either a Background or a Scenario or a Scenario Outline
      #if Background
         #output Background keyword, description and steps
      #if Scenario
         #output tags, Scenario keyword, description, steps and tables
      #if Scenario Outline
         #output tags, Scenario Outline keyword, description, steps and examples
 
