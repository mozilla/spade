"""
Tests for UserAgent model
"""
import MySQLdb
import warnings

from django.db import IntegrityError
from spade.model.models import UserAgent


def test_unicode_human_name():
    """Unicode representation of a user agent is the UA string."""
    ua = UserAgent(ua_string=u"Mozilla/5.0", ua_human_name=u"Moz 5")
    assert unicode(ua) == u"Moz 5"


def test_unicode_ua_string():
    """Unicode representation of a user agent is the UA string."""
    ua = UserAgent(ua_string=u"Mozilla/5.0",)
    assert unicode(ua) == u"Mozilla/5.0"


def test_length_toolong():
    """Strings longer than 250 characters will be truncated, raise warning"""
    super_long_ua = u"a" * 251

    with warnings.catch_warnings():
        warnings.simplefilter('error', MySQLdb.Warning)
        try:
            ua = UserAgent(ua_string=super_long_ua)
            ua.save()
        except:
            True
    False


def test_length_rightlength():
    """Strings 250 chars or less should pass without warning"""
    super_long_ua = u"b" * 250

    with warnings.catch_warnings():
        warnings.simplefilter('error', MySQLdb.Warning)
        try:
            ua = UserAgent(ua_string=super_long_ua)
            ua.save()
        except:
            False
    True


def test_unique_insert():
    """Inserting two of the same useragents will fail duplicate key"""
    first_ua = UserAgent(ua_string=u"Something/5.0")
    first_ua.save()

    try:
        other_ua = UserAgent(ua_string=u"Something/5.0")
        other_ua.save()
    except IntegrityError:
        False

    True

def test_unique_human_name_insert():
    """Inserting two human names that are not unique should fail"""
    first_ua = UserAgent(ua_string=u"Mozilla/5.0", ua_human_name=u"foo")
    first_ua.save()

    try:
        other_ua = UserAgent(ua_string=u"Something/5.0",ua_human_name=u"foo")
        other_ua.save()
    except IntegrityError:
        False
    True

def test_diff_insert():
    """Inserting two different useragents will pass"""
    first_ua = UserAgent(ua_string=u"Something/5.0", ua_human_name=u"foo")
    first_ua.save()
    try:
        other_ua = UserAgent(ua_string=u"SomethingElse/5.0", ua_human_name=u"baz")
        other_ua.save()
    except IntegrityError:
        False
    True
