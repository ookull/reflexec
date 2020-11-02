# Reflexec features

Feature: Command execution is informative

  @autodoc
  Scenario: Measure command execution duration
    When Reflexec is executed with options: --max-execs=1 sleep 1
    Then Command finishes with return code 0
    And Output matches with the following patterns:
    """
    Duration of round #1: 1\.[0-9]{2} sec
    """


  Scenario: Display error if command does not exist
    Given File "command-does-not-exist" does not exist
    When Reflexec is executed with options: --max-execs=1 -- ./command-does-not-exist
    Then Command finishes with return code 1
    And Command output contains the following strings:
    """
    Command not found
    """


  Scenario: Display error if there is no permission to execute command
    Given File "permission-denied" exist with permissions 440
    When Reflexec is executed with options: --max-execs=1 -- ./permission-denied arg1
    Then Command finishes with return code 1
    And Command output contains the following strings:
    """
    Permission denied
    """
