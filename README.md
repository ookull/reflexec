# Reflexec

Reflexec is a utility to automate annoying save-and-run routines in terminal
environment. Reflexec watches file system and triggers command execution on
specified file event (e.g. file change).


## Features

* Watch file system events (e.g. file change) using shell patterns.
* Execute command on file system event.
* Display summary of command execution (time spent, exit code).
* Support for different outputs (including standard logging, terminal output,
  terminal titlebar and system notification).
* Quick configuration with command line arguments.
* Advanced configuration using config file.
* Config file generation from command line.


## Activity diagram

  ```
  .------------------------------------------------------------.
  :                                                            :
  :                  O                                         :
  :                  |                                         :
  :          .--------------.                                  :
  :          |Parse CLI args|                                  :
  :          ˋ--------------ˊ                                  :
  :                  |                                         :
  :          .---------------.                                 :
  :          |(Re)load config| <--------------------.          :
  :          ˋ---------------ˊ                      |          :
  :                  |                              |          :
  :          .---------------.                      |          :
  :          |Execute command|                      |          :
  :          ˋ---------------ˊ                      |          :
  :                  |                              |          :
  :          .--------------.                       |          :
  :          |Report results|                       |          :
  :          ˋ--------------ˊ                       |          :
  :                  |                              |          :
  :           .-------------.                       |          :
  :           |Reload config|                       |          :
  :           ˋ-------------ˊ                       |          :
  :                  |                              |          :
  :          .----------------.                     |          :
  :          |Watch filesystem|                     |          :
  :          ˋ----------------ˊ                     |          :
  :                  |         Filesystem event /   |          :
  :          .--------------.  SIGQUIT              |          :
  :          |Register event| >---------------------ˊ          :
  :          ˋ--------------ˊ                                  :
  :                  |                                         :
  :                  | Keyboard interrupt ^C                   :
  :                  |                                         :
  :                  V                                         :
  :                  O                                         :
  :                                                            :
  `------------------------------------------------------------'
  ```
