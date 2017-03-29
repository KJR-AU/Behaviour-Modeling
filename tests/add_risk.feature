@requires-jython
Feature: Add Risks as a comment to Features and Scenarios


  Scenario: Attaching a risk without a section fails with a message
    Given I am running FlyingLogic with a document based on 'simple-risk-before.feature'
    When I deselect all nodes
    And I run the script 'add_risk'
    Then A message is shown with 'Please select an Feature or Scenario to add a risk.'

  Scenario: Attaching a risk to a Step fails with a message
    Given I am running FlyingLogic with a document based on 'simple-risk-before.feature'
    When I select the node:
      | feature                 | group title                       | node | title                          |
      | Simple example of risks | Access Statement History is paged | When | I access the statement history |
    And I run the script 'add_risk'
    Then A message is shown with 'You must select a Feature or Scenario to add a risk.'

  Scenario: Attaching a risk to a Feature
    Given I am running FlyingLogic with a document based on 'simple-risk-before.feature'
    And I want to add a New Risk:
      | Field       | Value                                            |
      | Risk Type:  | Security                                         |
      | Risk:       | Statements may be accessed by unauthorised users |
      | Likelihood: | Low                                              |
      | Severity:   | High                                             |
    When I select the node:
      | feature                 |
      | Simple example of risks |
    And I run the script 'add_risk'
    Then will check these nodes:
      | feature                 |
      | Simple example of risks |
    And expect to see the 'WRITING_BALLOON_SHOUT' symbol:
    And expect to see have an annotation:
    """
    Risk: [Statements may be accessed by unauthorised users | Type: Security | Likelihood: Low | Severity: High]
    """

  Scenario: Attaching a risk to a Scenario
    Given I am running FlyingLogic with a document based on 'simple-risk-before.feature'
    And I want to add a New Risk:
      | Field       | Value                                               |
      | Risk Type:  | Performance                                         |
      | Risk:       | Too many statements on screen will slow system down |
      | Likelihood: | Low                                                 |
      | Severity:   | Low                                                 |
    When I select the node:
      | feature                 | group title                       |
      | Simple example of risks | Access Statement History is paged |
    And I run the script 'add_risk'
    Then will check these nodes:
      | feature                 | group title                       |
      | Simple example of risks | Access Statement History is paged |
    And expect to see the 'WRITING_BALLOON_SHOUT' symbol:
    And expect to see have an annotation:
    """
    Risk: [Too many statements on screen will slow system down | Type: Performance | Likelihood: Low | Severity: Low]
    """

