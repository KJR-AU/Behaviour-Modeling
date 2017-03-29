Feature: build a flying logic group from a specific feature file
  Reads the file and creates Flying Logic Elements
  - Single Group for the File
  - Nested group for the Background and each Scenario
  - Given / When / Then Elements created as nodes and linked as per the file

  Scenario: Simple Feature File with Background
    Given I am running FlyingLogic with a new document
    And I have a sample file 'simple-background.feature'
    When I run the script 'import_feature_file'
    Then the document contains groups:
      | title                                                        |
      | login                                                        |
      | Background                                                   |
      | Display an error message when login with invalid credentials |
      | User successfully login with valid credentials               |
    And the 'login' group contains:
      | node  | title                                                        |
      | group | Background                                                   |
      | group | Display an error message when login with invalid credentials |
      | group | User successfully login with valid credentials               |
    And the 'Background' group contains:
      | node  | title                 |
      | Given | User is on login page |
    And the 'Display an error message when login with invalid credentials' group contains:
      | node | title                                    |
      | When | User enters an invalid username          |
      | When | User enters an invalid password          |
      | Then | login failure error message is displayed |
    And the 'User successfully login with valid credentials' group contains:
      | node | title                      |
      | When | User enters valid username |
      | When | User enters valid password |
      | Then | User is logged in          |
    And these nodes are connected in order:
      | group title                                                  | node  | title                           |
      | Background                                                   | Given | User is on login page           |
      | Display an error message when login with invalid credentials | When  | User enters an invalid username |
      | Display an error message when login with invalid credentials | When  | User enters an invalid password |
    And these nodes are connected in order:
      | group title                                    | node  | title                      |
      | Background                                     | Given | User is on login page      |
      | User successfully login with valid credentials | When  | User enters valid username |
      | User successfully login with valid credentials | When  | User enters valid password |


  Scenario: Links across features
    Given I am running FlyingLogic with a document based on 'multi-feature-C-2links.feature'
    And I have a sample file 'multi-feature-M-2links.feature'
    When I run the script 'import_feature_file'
    Then these nodes are connected in order:
      | group title | node  | title |
      | C-S1        | Then  | C-T1  |
      | M-S1        | Given | M-G1  |
    And these nodes are connected in order:
      | group title | node  | title |
      | C-S2        | Then  | C-T2  |
      | M-S2        | Given | M-G2  |