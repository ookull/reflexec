# Reflexec features

Feature: Multiple config files can be used

  By default Reflexec reads config files from the following paths:

  - /etc/reflexec.ini
  - ~/.config/reflexec.ini (directory is usually specified using
    XDG_CONFIG_HOME environment variable)
  - ./reflexec.ini

  Scenario: Use config from multiple config files

    Multiple config files are read by specified order and values from every
    file overrides previous values. Values from command line args overrides
    values from config files.

    Given Reflexec config file is:
    """
    [reflexec]
    # this value is used
    command = true
    # value is overrided by next config file
    max_execs = 2
    # value is overrided by next config file
    name = Name1

    [output-plain]
    finish_exec = This message will be replaced
    """
    And Reflexec config file reflexec-second.ini is:
    """
    [reflexec]
    # this value is used
    max_execs = 1
    # value is overrided by CLI arg
    name = Name2

    [output-plain]
    finish_exec = Finish message from config
    """
    # use environment variable to override default config files
    And Environment variable REFLEXEC_CONFIG is set to reflexec.ini:reflexec-second.ini:file-not-exist

    When Reflexec is executed with options: --name=MultiConf --output=plain
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    Starting reflexec instance: MultiConf
    Executing command (round #1): true
    Reached maximum execution count (1), exiting
    Finish message from config
    """
