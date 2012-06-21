from django.db import models
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage()

class SiteScan(models.Model):
    timestamp       = models.DateTimeField('date scanned')
    batch           = models.ForeignKey('batch.Batch', db_index=True)
    referrer        = models.CharField(max_length=200)
    gz_headers_path = models.CharField(max_length=200)
    gz_body_path    = models.CharField(max_length=200)
    gz_css_path     = models.CharField(max_length=200)
    UA_sniff        = models.BooleanField()
    error           = models.BooleanField()
