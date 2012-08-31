"""
Spade home view
"""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from spade import model

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
