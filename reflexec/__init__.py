"""Reflexec.
"""

import os

__version__ = "0.2.0"
__author__ = "Ivar Smolin"
__license__ = "MIT"


#: Default name for config file
DEFAULT_CONFIG_FILENAME = "reflexec.ini"
#: Default config file paths
CONFIG_FILES = [
    os.path.join("/etc", DEFAULT_CONFIG_FILENAME),
    os.path.join(
        os.environ.get("XDG_CONFIG_HOME", "~/.config"), DEFAULT_CONFIG_FILENAME
    ),
    os.path.join(".", DEFAULT_CONFIG_FILENAME),
]
#: Environment variable to specify config files
CONFIG_FILES_ENV_VAR = "REFLEXEC_CONFIG"


#: Exit code for keyboard interrupt
EXIT_CODE_KBD_INTERRUPT = 130
#: Exit code for QUIT signal
EXIT_CODE_SIGQUIT = 131
