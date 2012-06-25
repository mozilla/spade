# Models here
from django.db import models

class Batch(models.Model):
    kickoff_time    = models.DateTimeField("When crawl started")
    finish_time     = models.DateTimeField("When crawl ended")

class SiteScan(models.Model):
    # Each batch has multiple sites to scan
    batch       = models.ForeignKey('Batch', db_index=True)
    timestamp   = models.DateTimeField("timestamp")
    site_url    = models.CharField(max_length=200)

class URLScan(models.Model):
    # We scan multiple links per URL given (1-level)
    site_scan   = models.ForeignKey('SiteScan', db_index=True)
    page_url    = models.CharField(max_length=200)

class URLContent(models.Model):
    # On-page content, including html, on-page CSS, on-page JS
    url_scan    = models.ForeignKey('URLScan', db_index=True)
    user_agent  = models.CharField(max_length=250)
    raw_markup  = models.FileField(upload_to='crawls/%Y/%m/%d')
    headers     = models.FileField(upload_to='crawls/%Y/%m/%d')

class LinkedCSS(models.Model):
    # Each url can have multiple stylesheets
    url_scan = models.ForeignKey('URLScan', db_index=True)
    raw_css  = models.FileField(upload_to='crawls/%Y/%m/%d')

class LinkedJS(models.Model):
    # Each url can have multiple javascripts
    url_scan = models.ForeignKey('URLScan', db_index=True)
    raw_js   = models.FileField(upload_to='crawls/%Y/%m/%d')

class UserAgent(models.Model):
    ua_string   = models.CharField(max_length=250, unique=True, db_index=True)

class CrawlList(models.Model):
    # Models a URL to be crawled
    url = models.CharField(max_length=200, db_index=True, unique=True)
