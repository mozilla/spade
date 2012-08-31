from django.contrib import admin

from . import models


class URLContentInline(admin.TabularInline):
    model = models.URLContent
    extra = 0



class BatchUserAgentInline(admin.TabularInline):
    model = models.BatchUserAgent
    extra = 0


admin.site.register(models.Batch, inlines=[BatchUserAgentInline])
admin.site.register(models.SiteScan)
admin.site.register(models.URLScan, inlines=[URLContentInline])
admin.site.register(models.URLContent)
admin.site.register(models.LinkedCSS)
admin.site.register(models.LinkedJS)
admin.site.register(models.UserAgent)
admin.site.register(models.CSSRule)
admin.site.register(models.CSSProperty)
