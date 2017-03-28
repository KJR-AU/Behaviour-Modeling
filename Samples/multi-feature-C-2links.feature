
Feature: C-Feature
  <<InterFeatureLink FROM FEATURE<C-Feature> SCENARIO<C-S1> KEYWORD<Then > TEXT<C-T2> TO FEATURE<M-Feature> SCENARIO<M-S2> KEYWORD<Given > TEXT<M-G2> >>
  <<InterFeatureLink FROM FEATURE<C-Feature> SCENARIO<C-S2> KEYWORD<Then > TEXT<C-T1> TO FEATURE<M-Feature> SCENARIO<M-S1> KEYWORD<Given > TEXT<M-G1> >>
  @Test2
  Scenario: C-S1
    Given C-G2
    When C-W2
    Then C-T2

  @Test1
  Scenario: C-S2
    Given C-G1
    When C-W1
    Then C-T1
