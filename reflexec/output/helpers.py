"""Reflexec output helpers.
"""

from . import util


class WatchData:  # pylint: disable=too-few-public-methods
    """Watcher data object for output plugin."""

    patterns = None  #: Watcher patterns
    changed_file = None  #: Changed file name
    error_msg = None  #: Error message

    @property
    def as_dict(self):
        """Data as dictionary."""
        return dict(
            patterns=self.patterns,
            changed_file=self.changed_file,
            error_msg=self.error_msg,
        )


class ExecData:
    """Executing data object for output plugin."""

    start_time = None  #: Execution start time
    finish_time = None  #: Execution finish time
    duration = None  #: Execution duration
    exit_status_msg = None  #: Command exit status message
    exit_status_code = None  #: Command exit status code
    count = 0  #: Execution counter

    @property
    def duration_str(self):
        """Duration as a human readable string."""
        return util.human_readable_timedelta(self.duration_dict)

    @property
    def duration_dict(self):
        """Duration as a dictionary."""
        return util.timedelta_to_dict(self.duration)

    @property
    def as_dict(self):
        """Data as dictionary."""
        return dict(
            start_time=self.start_time,
            finish_time=self.finish_time,
            exit_status_code=self.exit_status_code,
            exit_status_msg=self.exit_status_msg,
            duration=self.duration,
            duration_str=self.duration_str,
        )
