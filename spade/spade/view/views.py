"""

Spade home view

"""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.shortcuts import redirect
from django.template.response import TemplateResponse

def home(request):
    """ Home view """
    return TemplateResponse(request, "home.html",{})
