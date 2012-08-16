"""
Tests for BatchUserAgent model
"""

import MySQLdb
import warnings

from . import factories
from datetime import datetime
from django.db import IntegrityError
from django.utils.timezone import utc
from spade.model.models import BatchUserAgent

MOCK_DATE = datetime(2012, 6, 29, 21, 10, 24, 10848, tzinfo=utc)


def test_instantiation():
    """ UA fields should be as set, and should unicode the UA string """
    batch = factories.BatchFactory.create(kickoff_time=MOCK_DATE,
                                          finish_time=MOCK_DATE)
    ua = factories.BatchUserAgentFactory.create(batch=batch,
                                                ua_string="Mozilla / 5.0",
                                                ua_type=BatchUserAgent.MOBILE)

    assert ua.ua_type == BatchUserAgent.MOBILE
    assert ua.ua_type != BatchUserAgent.DESKTOP
    assert ua.ua_string == 'Mozilla / 5.0'
    assert unicode(ua) == u"Mozilla / 5.0"


def test_length_toolong():
    """ Strings longer than 250 characters will be truncated, raise warning """
    super_long_ua = u"a" * 251

    with warnings.catch_warnings():
        warnings.simplefilter('error', MySQLdb.Warning)
        try:
            batch = factories.BatchFactory.create(kickoff_time=MOCK_DATE,
                                                  finish_time=MOCK_DATE)
            ua = factories.BatchUserAgentFactory.create(
                batch=batch,
                ua_string=super_long_ua,
                ua_type=BatchUserAgent.MOBILE)
        except:
            True
    False


def test_length_rightlength():
    """Strings 250 chars or less should pass without warning"""
    rightlength_ua = u"b" * 250

    with warnings.catch_warnings():
        warnings.simplefilter('error', MySQLdb.Warning)
        try:

            batch = factories.BatchFactory.create(kickoff_time=MOCK_DATE,
                                                  finish_time=MOCK_DATE)
            ua = factories.BatchUserAgentFactory.create(
                batch=batch,
                ua_string=rightlength_ua,
                ua_type=BatchUserAgent.MOBILE)
        except:
            False
    True


def test_unique_insert():
    """Inserting two of the same batchuseragents will fail duplicate key"""
    batch = factories.BatchFactory.create(kickoff_time=MOCK_DATE,
                                          finish_time=MOCK_DATE)
    first_ua = factories.BatchUserAgentFactory.create(
        batch=batch, ua_string="Test", ua_type=BatchUserAgent.MOBILE)

    try:
        ua = factories.BatchUserAgentFactory.create(
            batch=batch, ua_string="Test", ua_type=BatchUserAgent.MOBILE)
    except IntegrityError:
        True
    False


def test_diff_insert():
    """Inserting two diff batchuseragents will pass"""
    batch = factories.BatchFactory.create(kickoff_time=MOCK_DATE,
                                          finish_time=MOCK_DATE)
    first_ua = factories.BatchUserAgentFactory.create(
        batch=batch, ua_string="Test", ua_type=BatchUserAgent.MOBILE)

    try:
        ua = factories.BatchUserAgentFactory.create(
            batch=batch, ua_string="Test2", ua_type=BatchUserAgent.MOBILE)
    except IntegrityError:
        False
    True
