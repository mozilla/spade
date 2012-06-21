from django.db import models
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage()

class Batch(models.Model):
    kickoff_time    = models.DateTimeField('date created')
    finish_time     = models.DateTimeField('date created')
