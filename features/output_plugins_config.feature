# Reflexec features

Feature: Output plugins can be configured using config file

  Scenario: Configure plain output plugin
    Given Reflexec config file is:
    """
    [reflexec]
    command = true
    max_execs = 1
    delay = .1
    output = plain

    [output-plain]
    start_reflexec = [start_reflexec] Starting reflexec instance: {cmd_name}
    start_exec = [start_exec] Executing command (round #{exec_count}): {command}
    finish_exec = [finish_exec] Duration of round #{exec_count}: {duration_str}
    # use invalid value in "start_delay" to test error resistance
    start_delay = [start_delay] Pause {UNKNOWN_VALUE} seconds
    """

    When Reflexec is executed with options: reflexec.ini
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    [start_reflexec] Starting reflexec instance: true
    [start_exec] Executing command (round #1): true
    Command finished successfully
    [finish_exec] Duration of round #1:
    ERROR: Invalid key 'UNKNOWN_VALUE' while formatting 'start_delay' message for output plugin 'plain'
    """


  Scenario: Configure logger output plugin
    Given Reflexec config file is:
    """
    [reflexec]
    command = true
    max_execs = 1
    delay = .1
    output = log

    [output-log]
    start_reflexec = [start_reflexec] Starting reflexec instance: {cmd_name}
    # use invalid value in "start_exec" to test error resistance
    start_exec = [start_exec] Executing command {UNKNOWN_VALUE}
    finish_exec = [finish_exec] Duration of round #{exec_count}: {duration_str}
    start_delay = [start_delay] Pause {delay} seconds
    """

    When Reflexec is executed with options: reflexec.ini
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    INFO: [start_reflexec] Starting reflexec instance: true
    ERROR: Invalid key 'UNKNOWN_VALUE' while formatting 'start_exec' message for output plugin 'log'
    INFO: Command finished successfully
    INFO: [finish_exec] Duration of round #1:
    INFO: [start_delay] Pause 0.1 seconds
    """


  Scenario: Configure color terminal output plugin
    Given Reflexec config file is:
    """
    [reflexec]
    command = true
    max_execs = 1
    delay = .1
    output = colorterm

    [output-colorterm]
    start_exec = {bg.black}START{bg.reset}
    # use invalid value in "finish_exec_success" to test error resistance
    finish_exec_success = {fg.UNKNOWN}
    start_delay = {cr}DELAY {delay} SECONDS
      {clear_eol}
    """

    When Reflexec is executed with options: reflexec.ini
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    <CSI>40mSTART<CSI>49m
    ERROR: Error while formatting 'finish_exec_success' message for output plugin 'colorterm': 'AnsiFore' object has no attribute 'UNKNOWN'
    DELAY 0.1 SECONDS<CSI>0K
    """


  Scenario: Configure terminal title bar output plugin
    Given Reflexec config file is:
    """
    [reflexec]
    command = true
    max_execs = 1
    delay = .1
    output = titlebar

    [output-titlebar]
    exit_str_success = SUCCESS
    start_exec = [ EXEC #{exec_count} {cmd_name} ]
    finish_exec = [ FINISH {exit_status} #{exec_count} {cmd_name} ]
    start_delay = [ PAUSE {exit_status} #{exec_count} {cmd_name} ]
    """

    When Reflexec is executed with options: reflexec.ini
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    <OSC>2;[ EXEC #1 true ]<BEL>
    <OSC>2;[ FINISH SUCCESS #1 true ]<BEL>
    <OSC>2;[ PAUSE SUCCESS #1 true ]<BEL>
    """


  Scenario: Configure fancy terminal title bar output plugin
    Given Reflexec config file is:
    """
    [reflexec]
    command = true
    max_execs = 1
    delay = .1
    output = fancytitlebar

    [output-fancytitlebar]
    exit_str_success = SUCCESS

    # U+23F5 BLACK MEDIUM RIGHT-POINTING TRIANGLE
    start_exec = [ \xE2\x8f\xB5 #{exec_count} {cmd_name} ]
    # U+1F3C1 CHEQUERED FLAG
    finish_exec = [ \xF0\x9F\x8F\x81 {exit_str_success} #{exec_count} {cmd_name} ]
    # U+23F8 DOUBLE VERTICAL BAR
    start_delay = [ \xE2\x8F\xB8 {exit_status} #{exec_count} {cmd_name} ]
    """

    When Reflexec is executed with options: reflexec.ini
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    <OSC>2;[ ⏵ #1 true ]<BEL>
    <OSC>2;[ 🏁 SUCCESS #1 true ]<BEL>
    <OSC>2;[ ⏸ SUCCESS #1 true ]<BEL>
    """


  Scenario: Use command output plugin
    Given Reflexec config file is:
    """
    [reflexec]
    command = true
    max_execs = 1
    output = command

    [output-command]
    finish_exec_success = sh -c 'echo EXIT CODE $?'
    """

    When Reflexec is executed with options: reflexec.ini
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    EXIT CODE 0
    """

    Given Reflexec config file is:
    """
    [reflexec]
    command = true
    max_execs = 1
    output = command

    [output-command]
    finish_exec_success = {UNKNOWN_VALUE}
    """

    When Reflexec is executed with options: reflexec.ini
    Then Command finishes with return code 0
    And Command output contains the following strings:
    """
    ERROR: Invalid key 'UNKNOWN_VALUE' while formatting 'finish_exec' message for output plugin 'command'
    """
