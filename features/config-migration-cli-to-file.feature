# Reflexec features

Feature: CLI options can be converted to config file

  Scenario: Create config file with default values
    Given File "reflexec.ini" does not exist
    When User creates an empty config file using CLI
    """
    reflexec --write-config
    """
    Then Config file reflexec.ini is created
    """
    [reflexec]
    #name =
    #start = exec
    #type = default
    #watch = *
    #watcher = autodetect
    #delay = 0
    #max_execs = 0
    #output = default
    #command =
    """


  Scenario: Create config file with custom values using long CLI options
    Given File "reflexec.ini" does not exist
    When Reflexec is executed with options:
    """
    --name="Custom Name"
    --start=watch
    --watcher=filesystem
    --watch=reflexec.ini
    --watch=some_other_file
    --delay=1.2
    --max-execs=3
    --output=null
    --output=json

    --write-config
    --config-file=reflexec.ini

    true
    """
    Then Command finishes with return code 0
    And Config file reflexec.ini contains the following data:
    """
    [reflexec]
    name = Custom Name
    start = watch
    watcher = filesystem
    watch = reflexec.ini
      some_other_file
    delay = 1.2
    max_execs = 3
    output = null, json
    command = true
    """


  Scenario: Create config file with custom values using short CLI options
    Given File "reflexec.ini" does not exist
    When Reflexec is executed with options:
    """
    -n "Custom Name"
    -s watch
    -W autodetect
    --watch=reflexec.ini
    -w some_other_file
    -d 1.2
    -m 3
    --output=null
    -o json

    --write-config
    -c reflexec.ini

    true
    """
    Then Command finishes with return code 0
    And Config file reflexec.ini contains the following data:
    """
    [reflexec]
    name = Custom Name
    start = watch
    watcher = autodetect
    watch = reflexec.ini
      some_other_file
    delay = 1.2
    max_execs = 3
    output = null, json
    command = true
    """


  Scenario: Display error if config file overwriting fails
    Given Config file exist
    When Reflexec is executed with options: --write-config
    Then Command finishes with return code 3
    And Command output contains the following strings:
    """
    Error while creating config file 'reflexec.ini': file already exists
    """


  Scenario: Raise error message if config file writing fails
    When Reflexec is executed with options: --write-config --config-file=directory-not-exist/reflexec.ini
    Then Command finishes with return code 3
    And Command output contains the following strings:
    """
    Error while writing config file 'directory-not-exist/reflexec.ini': No such file or directory
    """


  Scenario: Raise error message if config file writing fails
    Given Directory "ro-dir" exist with RO permissions
    When Reflexec is executed with options: --write-config --config-file=ro-dir/reflexec.ini
    Then Command finishes with return code 3
    And Command output contains the following strings:
    """
    Error while writing config file 'ro-dir/reflexec.ini': Permission denied
    """
