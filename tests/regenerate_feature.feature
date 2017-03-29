Feature: Take a single flying logic group and produce a feature file

  Scenario: Round Trip a simple Feature File with Background
    Given I am running FlyingLogic with a document based on 'simple-background.feature'
    When I run the script 'regenerate_feature' outputting to a temporary file 'temp.feature'
    Then A message is shown with 'Feature file updated'
    And the files are the same 'simple-background.feature' and 'temp.feature'

  Scenario: Round Trip a simple Feature File with risks
    Given I am running FlyingLogic with a document based on 'simple-risk-after.feature'
    When I run the script 'regenerate_feature' outputting to a temporary file 'temp.feature'
    Then A message is shown with 'Feature file updated'
    And the files are the same 'simple-risk-after.feature' and 'temp.feature'
