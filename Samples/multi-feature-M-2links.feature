
Feature: M-Feature
  -- InterFeatureLink from(feature="C-Feature", scenario="C-S1", keyword="Then ", text="C-T2"), to(feature="M-Feature", scenario="M-S2", keyword="Given ", text="M-G2") --
  -- InterFeatureLink from(feature="C-Feature", scenario="C-S2", keyword="Then ", text="C-T1"), to(feature="M-Feature", scenario="M-S1", keyword="Given ", text="M-G1") --
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
