# Reflexec features

Feature: Command line interface is informative

  @autodoc
  Scenario: Output help message on request
    When Reflexec is executed with options: --help
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    usage:
    positional arguments:
    optional arguments:
    """


  Scenario: Output program version on request
    When Reflexec is executed with options: --version
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    reflexec
    """


  Scenario: Output usage information on unknown option
    When Reflexec is executed with options: --unknown-option
    Then Command finishes with return code 2
    And Command output contains the following strings:
    """
    usage: reflexec
    error: unrecognized arguments: --unknown-option
    """


  @autodoc
  Scenario: Output plugins list on request
    When Reflexec is executed with options: --list-plugins
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    Output plugins:

    colorterm
    command
    default
    fancytitlebar
    json
    log
    null
    titlebar

    Watcher plugins:

    inotify
    """


  Scenario Outline: Display error on invalid CLI options
    When Reflexec is executed with options: <arg>
    Then Command finishes with return code 2
    And Command output contains the following strings:
    """
    <error_msg>
    """

    Examples: <arg>
      | arg                 | error_msg                                               |
      | --max-execs=INVALID | invalid int value: 'INVALID'                            |
      | --max-execs=-1      | Negative value is not allowed for --max-execs           |
      | --delay=INVALID     | invalid float value: 'INVALID'                          |
      | --start=INVALID     | invalid choice: 'INVALID' (choose from 'exec', 'watch') |

