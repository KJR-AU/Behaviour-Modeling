
Feature: C-Feature
  -- InterFeatureLink from(feature="C-Feature", scenario="C-S1", keyword="Then ", text="C-T1"), to(feature="M-Feature", scenario="M-S1", keyword="Given ", text="M-G1") --
  -- InterFeatureLink from(feature="C-Feature", scenario="C-S2", keyword="Then ", text="C-T2"), to(feature="M-Feature", scenario="M-S2", keyword="Given ", text="M-G2") --
  @Test1
  Scenario: C-S2
    Given C-G2
    When C-W2
    Then C-T2

  @Test2
  Scenario: C-S1
    Given C-G1
    When C-W1
    Then C-T1
