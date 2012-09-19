import tldextract

# small helper function for finding only the domain of an url
def get_domain(url):
    try:
        data = tldextract.extract(url)
        return '%s.%s' % (data.domain, data.tld)
    except:
        return url
