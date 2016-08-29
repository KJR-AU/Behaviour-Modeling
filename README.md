# Behaviour-Modeling

A set of script to support the generation of behaviour graphs from Gherkin feature files, along with a limited set of model maintenance operations (merge, promote to background, etc).

Works with Flying Logic - use the Edit menu to run one of the scripts below:

Currently working scripts:

import_feature_file.py:  ingests a Gherkin feature file and generates a graphical display of each clause, as well as saving the Abstract Syntax Tree as a pickled python object.

merge_nodes.py: merges selected nodes in the graph and update the AST as a pickled python object. Merged nodes are changed to comments.

move_to_background.py: moves the selected node from within a Scenario into the Background 

regenerate_feature.py: outputs an updated feature file (i.e. overwrites the original!), reflecting the status of the current Abstract Syntax Tree. 

TODO:

See Trello board for details, but in general:

- move_to_background.py needs to be made more robust
- support needs to be added for And clauses
- Example tables and Scenario Outlines need to be supported, especially in the regenerate script
- As a pretty printer, regenerate could be much better - there are probably examples elsewhere we could re-use / reference.

May support other visualisation libraries in future (e.g. open source DOT graph format, YED) so that it's not dependent on the closed source Flying Logic tool, and could be integrated into Visual Studio and Eclipse, and perhaps Confluence or some other web-based approach.
