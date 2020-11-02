# Reflexec features

Feature: Command execution is flexible

  Scenario: Execute command without watching files
    When Reflexec is executed with options: --max-execs=1 uname
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    Linux
    """

  @autodoc
  Scenario: Execute command with post-execution delay
    When Reflexec is executed with options: --max-execs=1 --delay=0.1 uname
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    Pause 0.1 seconds
    """
