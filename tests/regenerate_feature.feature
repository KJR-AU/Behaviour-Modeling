Feature: Take a single flying logic group and produce a feature file

  Scenario: Round Trip a simple Feature File with Background
    Given I am running FlyingLogic with a document based on 'simple-background.feature'
    When I run the script 'regenerate_feature' outputting to a temporary file
    Then A message is shown with 'Feature file updated'
    And the new file is the same as the original
