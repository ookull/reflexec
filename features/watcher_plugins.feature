# Reflexec features

Feature: Expected changes are registered by watcher plugins

  Scenario Outline: Register file change using specified plugin
    Given Reflexec config file is:
    """
    [reflexec]
    start = exec
    watch = stamp
    max_execs = 2
    watcher = <watcher-plugin>

    # create file "stamp" to notify test
    command = sh -c "touch stamp ; echo 'CHANGED FILE: {changed_file}'"
    """
    And File "stamp" does not exist

    When Reflexec is executed in background
    Then File "stamp" is created within 3 seconds

    When File "stamp" is removed
    # Reflexec must detect file change and create file again
    Then File "stamp" is created within 3 seconds

    # Reflexec will stop after 2 rounds
    And Command finishes with return code 0
    And Command output contains the following strings:
    """
    Executing command (round #1): sh -c touch stamp ; echo 'CHANGED FILE: '
    Starting watcher for filesystem patterns
    Changed file: ./stamp
    Executing command (round #2): sh -c touch stamp ; echo 'CHANGED FILE: ./stamp'
    Reached maximum execution count (2), exiting
    """

    Examples: Plugins
      | watcher-plugin                                      |
      | autodetect                                          |
      | scan                                                |
      | reflexec.watcher.plugin:ScanFileSystemWatcherPlugin |


  Scenario: Display error message on invalid watcher plugin
    When Reflexec is executed with options: --max-execs=1 --watcher=INVALID -- true
    Then Command finishes with return code 1
    And Command output contains the following strings:
    """
    Specified built-in watcher plugin 'INVALID' does not exist
    """
