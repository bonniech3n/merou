from datetime import datetime

import pytz
from mock import patch
from pytz import UTC

from grouper.fe.template_util import expires_when_str, long_ago_str, print_date


def fake_settings_getitem(key):
    if key == "timezone":
        return pytz.timezone("US/Pacific")
    elif key == "date_format":
        return "%Y-%m-%d %I:%M %p"

    assert "unknown setting"


def test_expires_when_str():
    utcnow_fn = utcnow_fn = lambda: datetime(2015, 8, 11, 12, tzinfo=UTC)

    assert expires_when_str(None) == "Never", "no datetime means no expires"

    for date_, expected, msg in [
        ("2015-08-11 11:00:00.000", "Expired", "long before should expire"),
        ("2015-08-11 12:00:00.000", "Expired", "same time should expire"),
        ("2015-08-11 11:59:59.000", "Expired", "minute after should expire"),
        ("2015-08-11 12:00:00.100", "Expired", "milliseonds before should expire"),
        ("2015-08-11 12:00:01.000", "1 second", "singular second"),
        ("2015-08-11 12:00:02.000", "2 seconds", "pural second"),
        ("2015-08-11 12:01:02.000", "1 minute", "ignore lower periods"),
        ("2016-08-11 12:01:02.000", "1 year", "ignore lower periods"),
        (datetime(2015, 8, 11, 12, 0, 1, 0, tzinfo=UTC), "1 second", "from datetime object"),
        (1439294401.0, "1 second", "from float / unix timestamp"),
    ]:
        assert expires_when_str(date_, utcnow_fn=utcnow_fn) == expected, msg


def test_long_ago_str():
    utcnow_fn = utcnow_fn = lambda: datetime(2015, 8, 11, 12, tzinfo=UTC)

    for date_, expected, msg in [
        ("2015-08-11 11:00:00.000", "1 hour ago", "long before should expire"),
        ("2015-08-11 12:00:00.000", "now", "now"),
        ("2015-08-11 11:59:59.100", "now", "milliseonds before should be now"),
        ("2015-08-11 11:59:00.000", "1 minute ago", "1 minute"),
        ("2015-08-11 11:58:00.000", "2 minutes ago", "pural minutes"),
        ("2015-08-11 12:00:01.000", "in the future", "in the future"),
        (datetime(2015, 8, 11, 11, 0, 0, 0, tzinfo=UTC), "1 hour ago", "from datetime object"),
        (1439290800.0, "1 hour ago", "from float / unix timestamp"),
    ]:
        assert long_ago_str(date_, utcnow_fn=utcnow_fn) == expected, msg


@patch("grouper.fe.template_util.settings")
def test_print_date(mock_settings):
    mock_settings.__getitem__.side_effect = fake_settings_getitem

    for date_, expected, msg in [
        (datetime(2015, 8, 11, 18, tzinfo=UTC), "2015-08-11 06:00 PM", "from datetime object"),
        (datetime(2015, 8, 11, 18, 0, 10, 10, tzinfo=UTC), "2015-08-11 06:00 PM", "ignore sec/ms"),
        ("2015-08-11 18:00:00.000", "2015-08-11 06:00 PM", "from string"),
        (1439316000.0, "2015-08-11 06:00 PM", "from float / unix timestamp"),
    ]:
        assert print_date(date_) == expected, msg
