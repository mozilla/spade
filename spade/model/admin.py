from django.contrib import admin

from . import models


admin.site.register(models.Batch)
admin.site.register(models.SiteScan)
admin.site.register(models.URLScan)
admin.site.register(models.URLContent)
admin.site.register(models.LinkedCSS)
admin.site.register(models.LinkedJS)
admin.site.register(models.UserAgent)
admin.site.register(models.CrawlList)
