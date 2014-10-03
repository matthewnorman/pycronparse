import pytest
import datetime

import cronparse


def test_input_cron():
    """
    Make sure we can send values to cron

    """
    parser = cronparse.CronParse()
    with pytest.raises(TypeError):
        parser.set_cron(input_cron=1)
    with pytest.raises(ValueError):
        parser.set_cron(input_cron='invalid string')
    
    parser.set_cron(input_cron = '* * * * *')
    for x in  parser.crontab_times.values():
        assert x == '*'
    for x in parser.crontab_cycle.values():
        assert x is None

    parser.set_cron(input_cron = '10 * * * *')
    assert parser.crontab_times['minute'] == '10'
    assert parser.crontab_times['hour'] == '*'
    for x in parser.crontab_cycle.values():
        assert x is None

    parser.set_cron(input_cron = '*/10 * * * *')
    assert parser.crontab_times['minute'] is None
    assert parser.crontab_times['hour'] == '*'
    assert parser.crontab_cycle['minute'] == 10


def test_get_time(monkeypatch):
    """
    Test time creation using fixed times.

    """
    def fake_time(*args, **kwargs):
        return 1411410214.388395

    monkeypatch.setattr(cronparse.time, 'time', fake_time)
    parser = cronparse.CronParse()

    result = parser.get_time()
    expected = datetime.datetime(year=2014, month=9, day=22,
                                 hour=11, minute=23, second=34,
                                 microsecond=388395)
    assert result == expected


def test_get_day_of_week(monkeypatch):

    class fake_weekday(object):

        def weekday(self):
            return 6

    parser = cronparse.CronParse()
    result = parser.get_day_of_week(date=fake_weekday())
    assert result == 0

def test_pick_minute(monkeypatch):

    now = datetime.datetime(year=2014, month=8, day=8, hour=8, minute=20)
    parser = cronparse.CronParse()

    # Should return right now
    parser.set_cron(input_cron='* * * * *')
    result = parser.pick_minute(now=now)
    assert result == now

    # Should return now
    parser.set_cron(input_cron = '20 * * * *')
    result = parser.pick_minute(now=now)
    assert result == now

    # Since the tenth minute has already passed, should go to the next hour
    parser.set_cron(input_cron = '10 * * * *')
    result = parser.pick_minute(now=now)
    assert result == datetime.datetime(year=2014, month=8, day=8, hour=9,
                                       minute=10)

    parser.set_cron(input_cron = '*/15 * * * *')
    result = parser.pick_minute(now=now)
    assert result == datetime.datetime(year=2014, month=8, day=8, hour=8,
                                       minute=30)


def test_pick_hour():
    """
    Grab an hour

    """

    now = datetime.datetime(year=2014, month=8, day=8, hour=8, minute=20)
    parser = cronparse.CronParse()

    # Should return right now
    parser.set_cron(input_cron='* * * * *')
    result = parser.pick_hour(now=now)
    assert result == now

    # Should return right now
    parser.set_cron(input_cron='* 8 * * *')
    result = parser.pick_hour(now=now)
    assert result == now

    # Should return sometime tomorrow
    parser.set_cron(input_cron='* 7 * * *')
    result = parser.pick_hour(now=now)
    assert result == datetime.datetime(year=2014, month=8, day=9,
                                       hour=7, minute=0)

    # Should return next hour
    parser.set_cron(input_cron='* */2 * * *')
    result = parser.pick_hour(now=now)
    assert result == datetime.datetime(year=2014, month=8, day=8,
                                       hour=10, minute=0)



