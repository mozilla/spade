"""
Spade home view
"""

from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
    batches = model.Batch.objects.filter(data_aggregated=True)
    batches = batches.order_by('-finish_time')

    # pagination
    paginator = Paginator(batches, 5)
    page = request.GET.get('page')
    try:
        batches_pag = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        batches_pag = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        batches_pag = paginator.page(paginator.num_pages)
    batches = batches_pag.object_list  # computing only for displayed batches

    batches_data = []
    for batch in batches:

        ua_regressed = 'N/A'
        ua_fixed = 'N/A'

        prev = get_previous_batch(batch)
        if prev and prev.data_aggregated:
            regressions, fixes = get_ua_diffs(prev, batch)
            ua_regressed = '%d' % len(regressions)
            ua_fixed = '%d' % len(fixes)

        batch_data = batch.batchdata
        batches_data.append({
            'id': batch.id,
            'finish_time': batch.finish_time,
            'ua_issues_fixed': ua_fixed,
            'css_issues_fixed': 'N/A',
            'ua_issues_regressed': ua_regressed,
            'css_issues_regressed': 'N/A',
            'ua_issue_percent': batch_data.ua_issues_pctg,
            'css_issue_percent': batch_data.css_issues_pctg,
        })
    context = {'batches_data': batches_data, 'paginator': batches_pag}

    return TemplateResponse(request, "dashboard.html", context)


def batch_report(request, batch_id):
    """ Batch report view """

    # get the current batch
    batch = get_object_or_404(model.Batch, id=batch_id)

    context = {'batch_id': batch_id}

    # check if the batch has been processed
    if not batch.data_aggregated:
        return TemplateResponse(request, "batch_report_pending.html", context)
    batch_data = batch.batchdata

    ua_regressed = 'N/A'
    ua_fixed = 'N/A'

    # find the previous batch and the diff data
    prev = get_previous_batch(batch)
    if prev and prev.data_aggregated:
        regressions, fixes = get_ua_diffs(prev, batch)
        ua_regressed = '%d' % len(regressions)
        ua_fixed = '%d' % len(fixes)

    # find site_scans with UA errors
    ua_issues_sites = model.SiteScan.objects.filter(batch__id=batch.id)
    ua_issues_sites = ua_issues_sites.filter(sitescandata__ua_issues__gt=0)

    # pagination
    paginator = Paginator(ua_issues_sites, 5)
    page = request.GET.get('page_ua')
    try:
        ua_issues_pag = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        ua_issues_pag = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        ua_issues_pag = paginator.page(paginator.num_pages)

    # display the data
    context.update({'scanned_total': batch_data.scanned_pages,
                   'css_issues_pctg': batch_data.css_issues_pctg,
                   'ua_issues_pctg': batch_data.ua_issues_pctg,
                   'ua_issues_fixed': ua_fixed,
                   'css_issues_fixed': 'N/A',
                   'ua_issues_regressed': ua_regressed,
                   'css_issues_regressed': 'N/A',
                   'ua_issues_sites': ua_issues_pag.object_list,
                   'ua_issues_count': len(ua_issues_sites),
                   'ua_issues_paginator': ua_issues_pag})
    return TemplateResponse(request, "batch_report.html", context)


def site_report(request, site_id, user_agent="combined"):
    """ Site report view """
    context = { 'site_id': site_id }
    print user_agent
    return TemplateResponse(request, "site_report.html", context)
