"""
This module handles all the ETL work needed by the application 
"""
import csv
import urllib.request

from urllib.error import URLError
from datetime import datetime

from django.db import transaction
from .models import AdvData, DatasourceDim, CampaignDim, DateDim


DATASRC_URL = 'http://adverity-challenge.s3-website-eu-west-1.amazonaws.com/DAMKBAoDBwoDBAkOBAYFCw.csv'


def extract(file):
    "Extracts CSV data from binary file object"
    data = [l.decode('utf-8') for l in file.readlines()]
    data = csv.reader(data, delimiter=',')
    next(data)  # skip CSV header
    return data


def transform(data):
    """
    Transforms CSV data into model objects.
    Returns a generator.
    """
    unique = dict()
    for row in data:
        obj = dict()
        # transform text data to proper types
        try:
            d = datetime.strptime(row[0], '%d.%m.%Y').date()
            obj['clicks'] = int(row[3])
            obj['impressions'] = int(row[4])
        except ValueError:  # capture errors during conversion
            continue  # for simplicity we omit invalid data without reporting
        
        # create dimension objects making sure we don't duplicate
        # for this we use a dictionary key'd by names, values are model objects
        # this way we track objects identity in a simple way
        obj['date'] = unique.setdefault(d, DateDim(date=d))
        obj['datasource'] = unique.setdefault(row[1], DatasourceDim(name=row[1]))
        obj['campaign'] = unique.setdefault(row[2], CampaignDim(name=row[2]))
        
        yield AdvData(**obj)


@transaction.atomic
def load(data):
    "Loads model data into database"
    for obj in data:
        obj.date.save()
        obj.date_id = obj.date.id              # for some reason Django doesn't
        obj.datasource.save()                  # assign sub-object IDs
        obj.datasource_id = obj.datasource.id  # automatically, so we assign
        obj.campaign.save()                    # them here manually
        obj.campaign_id = obj.campaign.id      # probably a Django bug?
        obj.save()


def ETL():
    """
    ETL function for external CSV source. It extracts, transforms and loads
    data into Django model objects, saving in the local database.
    The function also checks if data was already loaded.
    """
    if AdvData.objects.count() > 0:  # we assume records are loaded into db
        return "Data already loaded"
    try:
        # extract data from remote end point
        # the data size is small so we can do it all in memory, for real world
        # cases this would need loading data in chunks
        with urllib.request.urlopen(DATASRC_URL) as f:
            load(transform(extract(f)))
    except URLError as e:
        return "Error: " + e.reason

