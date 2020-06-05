"""Reflexec watch pattern config module.
"""

import glob
import logging
import shlex
import subprocess

log = logging.getLogger("reflexec")


class WatchPatternCollection:
    """Watch pattern collection.

    :param pattern_type: Watch pattern type
    :type pattern_type: str
    :param patterns: Patterns
    :type patterns: list of str
    """

    pattern_type = None
    patterns = None

    def __init__(self, patterns, pattern_type="default"):
        assert pattern_type in ["default", "command"]
        self.pattern_type = pattern_type
        self.patterns = patterns

    def __repr__(self):
        return "<{} pattern_type={} patterns={}>".format(
            self.__class__.__name__, self.pattern_type, self.patterns
        )

    @property
    def paths(self):
        """List of filepaths that matches to patterns."""
        if self.pattern_type == "default":
            paths = self.solve_shell_patterns()
        else:
            assert self.pattern_type == "command"
            paths = self.solve_command_patterns()
        return list(filter(None, paths))

    def solve_shell_patterns(self):
        """Generate list of filepaths from unix shell patterns."""
        for pattern in self.patterns[:]:
            log.debug('Solving shell pattern "%s"', pattern)
            exclude = pattern.startswith("-")
            if exclude:
                pattern = pattern[1:]
            if not pattern.startswith(("/", "./")):
                pattern = "./{}".format(pattern)
            for path in glob.iglob(pattern, recursive=True):
                yield "-{}".format(path) if exclude else path

    def solve_command_patterns(self):
        """Generate list of filepaths from command patterns."""
        for command in self.patterns:
            log.debug('Executing command "%s" to get file list', command)
            proc = subprocess.run(
                shlex.split(command), stdout=subprocess.PIPE, check=False
            )
            if proc.returncode:
                log.warning(
                    'Watch pattern command "%s" exited with error code', proc.returncode
                )
            for line_no, line in enumerate(proc.stdout.split(b"\n"), start=1):
                try:
                    line = line.decode("UTF-8")
                except UnicodeError:
                    log.error("Can't convert filepath in line %d to unicode", line_no)
                    continue
                if line:
                    yield line if line.startswith(("/", "./")) else "./{}".format(line)
                else:
                    log.debug(
                        "Empty line #%d in watch command output, skipping", line_no
                    )
