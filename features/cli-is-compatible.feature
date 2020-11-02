# Reflexec features

Feature: CLI interface is POSIX compatible

  POSIX.1-2017
  12. Utility Conventions
  12.2 Utility Syntax Guidelines

  @autodoc
  Scenario: Use -- to signify the end of the CLI options
    # Guideline 10:
    # The first -- argument that is not an option-argument should be
    # accepted as a delimiter indicating the end of options. Any
    # following arguments should be treated as operands, even if they
    # begin with the '-' character.
    When Reflexec is executed with options: --max-execs=1 --delay=0 -- uname -o --kernel-name
    Then Command finishes with return code 0
