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
    assert parser.crontab_cycle['minute'] == '10'


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

