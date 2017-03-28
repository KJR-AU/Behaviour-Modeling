
Feature: M-Feature
  <<InterFeatureLink FROM FEATURE<C-Feature> SCENARIO<C-S1> KEYWORD<Then > TEXT<C-T2> TO FEATURE<M-Feature> SCENARIO<M-S2> KEYWORD<Given > TEXT<M-G2> >>
  <<InterFeatureLink FROM FEATURE<C-Feature> SCENARIO<C-S2> KEYWORD<Then > TEXT<C-T1> TO FEATURE<M-Feature> SCENARIO<M-S1> KEYWORD<Given > TEXT<M-G1> >>
  @Test
  Scenario: M-S1
    Given M-G1
    When M-W1
    Then M-T1

  @Test
  Scenario: M-S2
    Given M-G2
    When M-W2
    Then M-T2
