"""
Spade home view
"""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import redirect
from django.template.response import TemplateResponse


def dashboard(request):
    """ Front page dashboard view """
    return TemplateResponse(request, "dashboard.html",{})


def batch_report(request, batch_id):
    """ Batch report view """
    context = { 'batch_id': batch_id }
    return TemplateResponse(request, "batch_report.html", context)


def site_report(request, site_id):
    """ Site report view """
    context = { 'site_id': site_id }
    return TemplateResponse(request, "site_report.html", context)
