from spade.model.models import UserAgent


def test_unicode():
    """Unicode representation of a user agent is the UA string."""
    ua = UserAgent(ua_string=u"Mozilla/5.0")

    assert unicode(ua) == u"Mozilla/5.0"
