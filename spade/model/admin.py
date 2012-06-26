from django.contrib import admin

from . import models


class LinkedCSSInline(admin.TabularInline):
    model = models.LinkedCSS
    extra = 0


class LinkedJSInline(admin.TabularInline):
    model = models.LinkedJS
    extra = 0


class URLContentInline(admin.TabularInline):
    model = models.URLContent
    extra = 0


admin.site.register(models.Batch)
admin.site.register(models.SiteScan)
admin.site.register(models.URLScan, inlines=[URLContentInline])
admin.site.register(
    models.URLContent, inlines=[LinkedCSSInline, LinkedJSInline])
admin.site.register(models.LinkedCSS)
admin.site.register(models.LinkedJS)
admin.site.register(models.UserAgent)
admin.site.register(models.CrawlList)
