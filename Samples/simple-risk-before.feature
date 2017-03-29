Feature: Simple example of risks

  @Test1
  Scenario: Access Statement History is paged
    Given I have authenticated as a valid user
    When I access the statement history
    Then I see a list my of 10 most recent statements
