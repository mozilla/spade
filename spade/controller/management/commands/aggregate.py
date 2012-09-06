"""
Just a thin wrapper around data aggregator, so we can run it as a management command.

"""
from __future__ import absolute_import

from django.core.management.base import BaseCommand

from spade.model.models import *
from spade.utils.data_aggregator import DataAggregator

class Command(BaseCommand):
    help = (
        u"  Runs data aggregator on all unaggregated branches,\n"
        u"  Takes no arguments, leaves no prisoners.")

    def handle(self, *args, **options):
        if args and args[0] == u"help":
            self.stdout.write(u"Usage: {0}\n".format(self.args))
            self.stdout.write(self.help)
        else:
            batches = Batch.objects.filter(data_aggregated=False)
            da = DataAggregator()
            for batch in batches:
                da.aggregate_batch(batch)
