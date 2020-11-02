"""Reflexec output utilities module.
"""

import datetime
import math


def human_readable_timedelta(duration):
    """Timedelta as a human readable string.

    :param duration: timedelta values from timedelta_to_dict()
    :type duration: dict
    :returns: Human readable string
    """
    if not duration:
        return ""

    assert isinstance(duration, dict)

    # format duration string
    msg = []
    if duration["days"]:
        msg.append(f"{duration['days']:d} days")
    if msg or duration["hours"]:
        msg.append(f"{duration['hours']:d} hr")
    if msg or duration["minutes"]:
        msg.append(f"{duration['minutes']:d} min")
    # output seconds only if duration is shorter than one hour
    if not duration["days"] and not duration["hours"]:
        if duration["minutes"] or duration["seconds"] >= 30:
            msg.append(f"{duration['seconds']} sec")
        elif duration["seconds"] >= 10:
            msg.append(f"{duration['seconds']:.1f} sec")
        elif duration["seconds"] >= 1:
            msg.append(f"{duration['seconds']:.2f} sec")
        else:
            msg.append(f"{duration['seconds']:.3f} sec")
    return str(" ".join(msg))


def timedelta_to_dict(timedelta):
    """Convert timedelta to dictionary.

    :param timedelta: timedelta
    :type timedelta: datetime.timedelta

    :return: dict (days, hours, minutes, seconds).
             Empty dict is duration is None
    """
    if timedelta is None:
        return {}
    assert isinstance(timedelta, datetime.timedelta)

    days = timedelta.days
    duration_seconds = timedelta.seconds
    hours = math.floor(duration_seconds / 3600)
    if hours:
        duration_seconds %= 3600
    minutes = math.floor(duration_seconds / 60)
    if minutes:
        duration_seconds = duration_seconds % 60
    if days + hours + minutes == 0 and duration_seconds < 30:
        duration_seconds += (
            timedelta.microseconds - (timedelta.microseconds % 1000)
        ) / 1000000
        if duration_seconds >= 10:
            duration_seconds = round(duration_seconds, 1)
        elif duration_seconds > 1:
            duration_seconds = round(duration_seconds, 2)
        else:
            duration_seconds = round(duration_seconds, 3)

    return dict(days=days, hours=hours, minutes=minutes, seconds=duration_seconds)
