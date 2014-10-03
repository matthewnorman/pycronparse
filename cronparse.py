import time
import datetime

CRON_ORDER = ['minute', 'hour', 'dayofmonth', 'month', 'dayofweek']

def str_test(tester):
    if isinstance(tester, str) or isinstance(tester, unicode):
        return True
    return False

class CronParse(object):

    def __init__(self, input_cron=None, timezone=None):
        super(CronParse, self).__init__()
        self.crontab_times = {}
        self.crontab_cycle = {}
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
        time_list = []
        cycle_list = []
        for x in split_crons:
            if x.startswith('*/'):
                time_list.append(None)
                # Then take the value only (we don't care about the rest)
                cycle_list.append(x.split('/')[1])
            else:
                if x is not '*' and not x.isdigit():
                    raise ValueError('Invalid value %s' % x)
                time_list.append(x)
                cycle_list.append(None)

        for name, timemark, cycle in zip(CRON_ORDER, time_list, cycle_list):
            self.crontab_times[name] = timemark
            self.crontab_cycle[name] = cycle

        
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


    def next_run(self):
        """
        How much time until the next time we run? This is the critical
        method, and it has much of its logic parsed out.

        Return the time of the next execution time.
        """
        # First tree opening, do we have to deal with days or just times
        # within today/tomorrow?
        next_run = None

        if self.crontab_times['dayofmonth'] == '*' and\
           self.crontab_times['dayofweek'] == '*' and\
           self.crontab_times['month'] == '*':
            next_run = self.handle_non_day()

        return next_run

    def pick_day(self, now):
        """
        Get the hours from pick_hour and then shove it out the door with
        the correct day chosen.

        """
        hour_dt = self.pick_hour(now=now)
        day_value = self.crontab_times['day']
        day_of_week_value = self.crontab_times['day_of_week']
        if day_value == '*' and day_of_week == '*':
            return hour_dt
        elif day_value is None and day_of_week_value == '*':
            cycle_day = self.crontab_cycles

    def pick_hour(self, now):
        """
        Run the minutes code, pass a datetime back, and then figure out
        what to do about the hours.

        """
        minute_dt = self.pick_minute(now=now)
        if self.crontab_times['hour'] == '*':
            return minute_dt
        elif self.crontab_times['hour'] is None:
            cycle_hour = self.crontab_cycles['hour']
            hour_increment = 0
            for i in xrange(0, cycle_hour):
                if (current_hour + i) % cycle_hour == 0:
                    hour_increment = i
                    break
            new_time = minute_dt + datetime.timedelta(hours=hour_increment)
        else:
            hour = self.crontab_times['hour']
            new_time = datetime.datetime(year=minute_dt.year,
                                         month=minute_dt.month,
                                         day=minute_dt.day,
                                         hour=hour, minute=minute_dt.minute)
            if new_time < minute_dt:
                new_time = new_time + datetime.timedelta(days=1)
        return new_time

    def pick_minute(self, now):
        """
        Run this like we're just doing a minute.

        """
        new_time = None
        if self.crontab_times['minute'] == '*':
            # Return time for next minute
            new_time = now + datetime.timedelta(minutes=1)
        elif self.crontab_times['minute'] is None:
            cycle_minute = self.crontab_times['minute']
            if cycle_minute is None:
                # Then we've got a problem
                raise ValueError('No minute value')
            minute_increment = 0
            for i in xrange(0, cycle_minute):
                if (minute + i) % cycle_minute == 0:
                    minute_increment = i
                    break
            new_time = datetime.datetime(year=now.year,
                                         month=now.month,
                                         day=now.day,
                                         hour=now.hour, minute=now.minute)
            new_time = new_time + datetime.timedelta(minutes=minute_increment)
        else:
            minute = self.crontab_times['minute']
            new_time = datetime.datetime(year=now.year,
                                         month=now.month,
                                         day=now.day,
                                         hour=day.hour,
                                         minute=minute)
            if new_time > now:
                new_time = datetime.datetime(year=now.year,
                                             month=now.month,
                                             day=now.day,
                                             hour=now.hour,
                                             minute=minute)
                new_time = new_time + datetime.timedelta(hours=1)

        return new_time
