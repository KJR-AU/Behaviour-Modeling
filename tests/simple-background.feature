Feature: login

Background:
Given User is on login page

@Test1
Scenario: Display an error message when login with invalid credentials
#Given User is on login page
When User enters invalid username and password
Then login failure error message is displayed


@Test2
Scenario: User successfully login with valid credentials
#Given User is on login page
When User enters valid username and password
Then User is logged in


















