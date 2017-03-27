Feature: login

  @Test1
  Scenario: Display an error message when login with invalid credentials
    Given User is on login page
    When User enters an invalid username
    When User enters an invalid password
    Then login failure error message is displayed

  @Test2
  Scenario: User successfully login with valid credentials
    Given User is on login page
    When User enters valid username
    When User enters valid password
    Then User is logged in


