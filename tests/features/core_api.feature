Feature: Core API Interface Contracts

  The core API should provide simple, reliable interfaces for loading conversations.

  Scenario: Load conversation from file
    Given a JSONL file with valid messages
    When I call load() with the file path
    Then I should get a Conversation object
    And the conversation should contain all messages from the file

  Scenario: Load returns empty conversation for empty file
    Given an empty JSONL file
    When I call load() with the file path
    Then I should get a Conversation object
    And the conversation should have zero messages

  Scenario: Load handles missing file gracefully
    Given a non-existent file path
    When I call load() with the file path
    Then it should raise an appropriate exception
    And the exception message should be user-friendly
