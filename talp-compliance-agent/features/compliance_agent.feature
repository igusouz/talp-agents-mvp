Feature: Compliance Analysis
  As a user
  I want to analyze compliance of investments
  So that I can ensure regulatory conformance

  Scenario: Check health of compliance agent
    Given the compliance agent is running
    When I check the health endpoint
    Then the agent should respond with status healthy
