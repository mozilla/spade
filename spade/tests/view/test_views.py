from django.core.urlresolvers import reverse
from spade.tests.model.factories import (BatchFactory,
										 SiteScanFactory,
										 SiteScanDataFactory)


def test_dashboard(client):
	url = reverse('dashboard')
	response = client.get(url)
	assert response.status_code == 200


def test_batch_report(client):
	batch  = BatchFactory.create()
	url = reverse('batch_report', kwargs={'batch_id':batch.id})
	response = client.get(url)
	assert response.status_code == 200

def test_site_css_report(client):
	site  = SiteScanFactory.create()
	sitescan_data = SiteScanDataFactory.create(sitescan=site,
                                               css_issues=3,
                                               ua_issues=4)
	url = reverse('site_css_report', kwargs={'site_id':site.id})
	response = client.get(url)
	assert response.status_code == 200

def test_site_ua_report(client):
	site  = SiteScanFactory.create()
	sitescan_data = SiteScanDataFactory.create(sitescan=site,
                                               css_issues=3,
                                               ua_issues=4)
	url = reverse('site_ua_report', kwargs={'site_id':site.id})
	response = client.get(url)
	assert response.status_code == 200
