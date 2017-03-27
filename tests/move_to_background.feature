Feature: Move selected nodes to the background

  Scenario: No nodes selected is not valid
    Given I am running FlyingLogic with a document based on 'simple-merge.feature'
    When I deselect all nodes
    When I run the script 'move_to_background'
    Then A message is shown with 'You must select at least one node to move into the background.'


  Scenario: Selecting a node lower in the scenario is not valid
    Given I am running FlyingLogic with a document based on 'simple-merge.feature'
    When I select the node
      | group title                                    | node | title             |
      | User successfully login with valid credentials | Then | User is logged in |
    When I run the script 'move_to_background'
    Then A message is shown with 'You must select node(s) at the top of the scenario.'


  #  TODO: Create New linkage to the other scenarios in the same feature
  #  TODO: Remove identical nodes at the top of other scenarios
  Scenario: Selecting the first node within a scenario
    Given I am running FlyingLogic with a document based on 'simple-merge.feature'
    When I select the node
      | group title                                    | node  | title                 |
      | User successfully login with valid credentials | Given | User is on login page |
    When I run the script 'move_to_background'
    Then the 'Background' group contains:
      | node  | title                 |
      | Given | User is on login page |
    And these nodes are connected in order:
      | group title                                    | node  | title                      |
      | Background                                     | Given | User is on login page      |
      | User successfully login with valid credentials | When  | User enters valid username |
    #And these nodes are connected in order:
    #  | group title                                                  | node  | title                 |
    #  | Background                                                   | Given | User is on login page |
    #  | Display an error message when login with invalid credentials | When  | User enters an invalid username|