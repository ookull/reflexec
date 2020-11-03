"""Unit tests for Reflexec output utils."""

import datetime
import unittest

from reflexec.output.util import human_readable_timedelta, timedelta_to_dict


class TestOutputUtils(unittest.TestCase):
    """Output utils test."""

    def test_duration_accuracy(self):
        """Duration accuracy test.

        Use smart accuracy to express duration.

        Accuracy of command execution duration depends on duration length.
        - 0...1 second - accuracy in milliseconds
        - up to 10 seconds - accuracy in centiseconds
        - up to 30 seconds - accuracy in deciseconds
        - up to 1 hour - accuracy in seconds
        - more than 1 hour - accuracy in minutes
        """
        durations = {
            "0.421 sec": {"seconds": 0, "milliseconds": 421},
            "1.00 sec": {"seconds": 1},
            "9.87 sec": {"seconds": 9, "milliseconds": 870},
            "11.6 sec": {"seconds": 11, "milliseconds": 604},
            "29.0 sec": {"seconds": 29},
            "30 sec": {"seconds": 30},
            "59 sec": {"seconds": 59},
            "2 min 0 sec": {"minutes": 2},
            "4 min 18 sec": {"minutes": 4, "seconds": 18},
            "59 min 37 sec": {"minutes": 59, "seconds": 37},
            "1 hr 0 min": {"hours": 1},
            "23 hr 59 min": {"hours": 23, "minutes": 59, "seconds": 24},
            "1 days 0 hr 0 min": {"days": 1},
            "14 days 2 hr 47 min": {"days": 14, "hours": 2, "minutes": 47},
            "33 days 0 hr 0 min": {"days": 33},
        }
        for duration_str, timedelta_dict in durations.items():
            timedelta = datetime.timedelta(**timedelta_dict)
            timedelta_dict = timedelta_to_dict(timedelta)
            timedelta_str = human_readable_timedelta(timedelta_dict)
            self.assertEqual(duration_str, timedelta_str)
