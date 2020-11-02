# Reflexec features

Feature: Watcher can be interrupted using signals

  The following signals can be used:
  * SIGINT = Ctrl-\
  * SIGQUIT = Ctrl-C

  Scenario: Stop watching changes on QUIT signal

    Given Reflexec config file is:
    """
    [reflexec]
    start = exec
    max_execs = 2
    watch = some-random-pattern

    command = touch stamp
    """
    And File "stamp" does not exist

    When Reflexec is executed in background
    Then File "stamp" is created within 3 seconds

    When File "stamp" is removed
    And QUIT signal is sent to Reflexec
    # QUIT signal must stop Reflexec to watch files and execute command again
    Then File "stamp" is created within 3 seconds

    # Reflexec will stop after 2 rounds
    And Command finishes with return code 0
    And Command output contains the following strings:
    """
    Executing command (round #1): touch stamp
    Starting watcher for filesystem patterns
    Got QUIT signal
    Executing command (round #2): touch stamp
    Reached maximum execution count (2), exiting
    """


  Scenario: Stop program on keyboard interrupt while watching files

    Given Reflexec config file is:
    """
    [reflexec]
    start = exec
    max_execs = 2
    watch = some-random-pattern

    command = touch stamp
    """
    And File "stamp" does not exist

    When Reflexec is executed in background
    Then File "stamp" is created within 3 seconds

    When File "stamp" is removed
    And Wait for 0.2 seconds
    And INT signal is sent to Reflexec
    Then Command finishes with return code 130
    And Command output contains the following strings:
    """
    Keyboard interrupt
    """


  @skip
  # No idea how to emulate Ctrl-C. Sending SIGINT does not kill "sleep" command
  Scenario: Keyboard interrupt controls currently executed command

    Given Reflexec config file is:
    """
    [reflexec]
    log_level = DEBUG
    start = exec
    max_execs = 1
    command = sh -c 'touch stamp && sleep 10'
    """

    When Reflexec is executed in background
    Then File "stamp" is created within 3 seconds

    When Keyboard interrupt is generated
    Then Command finishes with return code 1
    And Command output contains the following strings:
    """
    Keyboard interrupt
    """
