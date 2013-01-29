from django import template

register = template.Library()

MINUTES_IN_HOUR = 60

# This is the sub-hour resolution that the user will be exposed to. For example, if this value is 4, then the
# resolution will be MINUTES_IN_HOUR/4 = 15 minutes. This means that 2 hours and 16 minutes will be rounded to
# 2 hours and 15 minutes.
INTERVALS_IN_HOUR = 6
SUB_HOUR_INTERVAL_SIZE = MINUTES_IN_HOUR / INTERVALS_IN_HOUR

@register.filter(is_safe=False)
def humanize_minutes(value):
    """
    Converts a number (in minutes) to a reasonable string consisting of hours and minutes (rounded to 15 minute intervals).
    """
    if not value:
        return None
    hours = int(value / MINUTES_IN_HOUR)
    remaining_minutes = value % MINUTES_IN_HOUR
    sub_hour_intervals_remaining = int(remaining_minutes / SUB_HOUR_INTERVAL_SIZE)
    extra_time = remaining_minutes % SUB_HOUR_INTERVAL_SIZE
    if extra_time > SUB_HOUR_INTERVAL_SIZE/2:
        sub_hour_intervals_remaining += 1
        if sub_hour_intervals_remaining == INTERVALS_IN_HOUR:
            hours += 1
            sub_hour_intervals_remaining = 0
    minutes = sub_hour_intervals_remaining * SUB_HOUR_INTERVAL_SIZE
    if hours and minutes:
        return "{hours} hours, {minutes} minutes".format(hours=hours, minutes=minutes)
    elif hours:
        return "{hours} hours".format(hours=hours)
    elif minutes:
        return "{minutes} minutes".format(minutes=minutes)
    else:
        return "{minutes} minutes".format(minutes=value)