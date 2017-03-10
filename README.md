# Behaviour-Modeling

A set of script to support the generation of behaviour graphs from Gherkin feature files, along with a limited set of model maintenance operations (merge, promote to background, etc).

Works with Flying Logic - use the Edit menu to run one of the scripts below:

Currently working on scripts:

* **import_feature_file.py**: 
  Ingests a Gherkin feature file and generates a graphical display of each clause.

* **regenerate_feature.py**: 
  Outputs an updated feature file reflecting the contents of of the Flying Logic document. 

* **merge_nodes.py**: 
  merges selected nodes in the graph and update the AST as a pickled python object. Merged nodes are changed to comments.

* **move_to_background.py**: 
  moves the selected node from within a Scenario into the Background 


## TODO

See Trello board for details, but in general:

- move_to_background.py needs to be made more robust
- support needs to be added for "And" clauses
- Example tables and Scenario Outlines need to be supported, especially in the regenerate script
- As a pretty printer, regenerate could be much better - there are probably examples elsewhere we could re-use / reference.

May support other visualisation libraries in future (e.g. open source DOT graph format, YED) so that it's not dependent on the closed source Flying Logic tool, and could be integrated into Visual Studio and Eclipse, and perhaps Confluence or some other web-based approach.

## Dependencies

Tested with:
- Flying Logic 3.0.6
  * Import this project's "Behaviour-Modeling.xlogic-d" domain.
- Python 2.7.6
  * 'gherkin-official' package 
  
Development also requires:
  * 'behave' package for running tests.
  * 'pprint' package for formatting debug messages.
  
## References

- [Scripting Guide for Flying Logic (PDF)](http://flyinglogic.com/docs/Flying+Logic+Scripting+Guide.pdf)
- [Cucumber Reference Material](https://cucumber.io/docs/reference)
- [Gherkin Reference Material](https://github.com/cucumber/gherkin)
  

