"""
Spade home view
"""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from spade import model


def get_url_scan(url, batch):
    urls = model.URLScan.objects.filter(site_scan__batch__id=batch.id)
    urls = urls.filter(page_url=url.page_url)
    if urls.count():
        return urls[0]
    return None


def get_ua_diffs(previous_batch, current_batch):
    """ Returns a 2-tuple containing a list of regressions
    and a list of fixes """

    # get a list of the urls scanned in the current batch
    urls = []
    for site_scan in current_batch.sitescan_set.all():
        for url in site_scan.urlscan_set.all():
            urls.append(url)

    regressions = []
    fixes = []
    for url in urls:
        prev = get_url_scan(url, previous_batch)
        if not prev:
            continue
        if not prev.urlscandata.ua_issue and url.urlscandata.ua_issue:
            regressions.append(url)
        if prev.urlscandata.ua_issue and not url.urlscandata.ua_issue:
            fixes.append(url)

    return (regressions, fixes)


def get_previous_batch(batch):
    prev_batches = model.Batch.objects.filter(finish_time__lt=batch.finish_time)
    prev = prev_batches.order_by('-finish_time')[:1]
    if prev:
        return prev[0]
    return None


def dashboard(request):
    """ Front page dashboard view """

    batches = model.Batch.objects.order_by('finish_time')

    batch_data = {}
    for batch in batches:
        batch_data[batch.finish_time] = {
            'id': batch.id,
            'ua_issues_fixed':0,
            'css_issues_fixed': 0,
            'ua_issues_regressed':0,
            'css_issues_regressed':0,
            'ua_issue_percent':0,
            'css_issue_percent':0,
        }

    # TODO: Determine UA issue %
    # TODO: Determine CSS issue %
    # TODO: Determine UA issues fixed since last scan
    # TODO: Determine CSS issues fixed since last scan
    # TODO: Determine UA issues regressed
    # TODO: Determine CSS issues regressed

    return TemplateResponse(request, "dashboard.html", batch_data)


def batch_report(request, batch_id):
    """ Batch report view """
    context = { 'batch_id': batch_id }


    return TemplateResponse(request, "batch_report.html", context)


def site_report(request, site_id, user_agent="combined"):
    """ Site report view """
    context = { 'site_id': site_id }
    print user_agent
    return TemplateResponse(request, "site_report.html", context)
