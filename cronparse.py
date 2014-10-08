import time
import datetime

CRON_ORDER = ['minute', 'hour', 'day', 'month', 'dayofweek']

def str_test(tester):
    if isinstance(tester, str) or isinstance(tester, unicode):
        return True
    return False


class CronParseException(Exception):
    """
    Raise this when you're in trouble

    """


class CronParse(object):

    def __init__(self, input_cron=None, timezone=None):
        super(CronParse, self).__init__()
        self.crontab_times = {}
        self.crontab_cycle = {}
        self.ranges = {}
        self.cron_parts = {}
        if input_cron is not None:
            self.set_cron(input_cron=input_cron)

    def set_cron(self, input_cron):
        """
        Given a string format, store it in components, or, if
        of the format */x, in crontab_cycle

        """
        if not str_test(input_cron):
            # We can't handle this
            raise TypeError('Input must be a string object')
        split_crons = input_cron.split()
        if not len(split_crons) == 5:
            msg = 'Must have five different components for cron format.'
            raise ValueError(msg)
        for key, value in zip(CRON_ORDER, split_crons):
            self.cron_parts[key] = value
        
    def get_time(self):
        """
        What time is it? Return a dictionary with the minute, hour,
        dayofmonth, month, and dayofweek as specified in the cron
        format.

        """
        result = {}

        timestamp = time.time()
        date = datetime.datetime.fromtimestamp(timestamp)

        return date

    def get_day_of_week(self, date):

        # Because datetime and cron count their days differently
        day_of_week = date.weekday() + 1
        if day_of_week == 7:
            day_of_week = 0
        return day_of_week

    def validate_dt_part(self, dt, component):
        """
        Validate each component of the dt (besides the day of the week)
        because they all work in more or less the same way.

        """
        time_value = getattr(dt, component)
        if self.cron_parts[component] == '*':
            # Always true
            return True
        for x in self.cron_parts[component].split(','):
            # Split into a list of individual parts
            if x.isdigit():
                # Then it's simple
                if int(x) == time_value:
                    return True
                continue
            if '-' in x:
                # This is a range. Extract the range part and handle it.
                range_min, range_max = x.split('/')[0].split('-')
                
                if time_value < int(range_min) or time_value > int(range_max):
                    continue
            if '/' in x:
                cycle_value = x.split('/')[1]
                if not cycle_value.isdigit():
                    raise ValueError('Invalid timevalue %s' % x)
                if time_value % int(cycle_value) == 0:
                    return True
        return False

    def validate_dow(self, dt):
        """
        Validate the day of the week

        """
        if self.cron_parts['dayofweek'] == '*':
            return True
        else:
            weekday = int(self.cron_parts['dayofweek'])
            if weekday == self.get_day_of_week(date=dt):
                return True
            return False

    def validate_day(self, dt):
        """
        Validate the day as one method. This is because cron uses an OR
        when both day of month and day of week are specified.

        """
        if self.cron_parts['dayofweek'] == '*':
            return self.validate_dt_part(dt=dt, component='day')
        elif self.cron_parts['day'] == '*':
            return self.validate_dow(dt=dt)
        else:
            return (self.validate_dt_part(dt=dt, component='day') or
                    self.validate_dow(dt=dt))


    def brute_next(self, now):
        """
        Brute force this - simply iterate through all possible times.

        """
        dt = now
        while True:
            valid_day = self.validate_day(dt=dt)
            valid_month = self.validate_dt_part(dt=dt, component='month')
            valid_hour = self.validate_dt_part(dt=dt, component='hour')
            valid_minute = self.validate_dt_part(dt=dt, component='minute')
            if not valid_month:
                if dt.month > 11:
                    dt = datetime.datetime(year=dt.year+1, month=1,
                                           day=1, hour=0, minute=0)
                else:
                    dt = datetime.datetime(year=dt.year, month=dt.month+1,
                                           day=1, hour=0, minute=0)
            if not valid_day:
                # Increment by day and try again
                dt = dt + datetime.timedelta(days=1)
                if dt.minute != 0:
                    dt = dt - datetime.timedelta(minutes=dt.minute)
                if dt.hour != 0:
                    dt = dt - datetime.timedelta(hours=dt.hour)
            elif not valid_hour:
                # Increment by an hour and try again
                dt = dt + datetime.timedelta(hours=1)
                if dt.minute != 0:
                    dt = dt - datetime.timedelta(minutes=dt.minute)
            elif not valid_minute:
                # Increment by one minute
                dt = dt + datetime.timedelta(minutes=1)
            elif dt.year - now.year > 100:
                # There are no hundred year cycles
                raise CronParseException('Stuck in infinite loop')
            else:
                break
        # At the end
        return dt
                
        
