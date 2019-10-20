from collections import namedtuple

from django.shortcuts import render
from django.db.models import Sum
from django import forms

from .models import DateDim, DatasourceDim, CampaignDim
from . import etl


class SearchForm(forms.Form):
    """
    The form used for chart data filtering
    """
    datasource = forms.ModelMultipleChoiceField(DatasourceDim.objects.all(),
                    label="Data source",
                    required=False)
    campaign = forms.ModelMultipleChoiceField(CampaignDim.objects.all(),
                    label="Campaign",
                    required=False)


def queryDB(params):
    "Queries db according to parameters given in the view's form"
    result = DateDim.objects.all()
    # if any filters were chosen in the view, add them to the query set
    q = {}
    if 'datasource' in params:
        q['advdata__datasource__in'] = params.getlist('datasource')
    if 'campaign' in params:
        q['advdata__campaign__in'] = params.getlist('campaign')
    result = result.filter(**q)
    # apply aggregates and order set
    result = result.annotate(clicks=Sum('advdata__clicks'),
                             impressions=Sum('advdata__impressions')).order_by('date')
    
    return result


def index(request):
    """
    The main view for the 'adverity' challenge.
    It queries data using supplied GET parameters and loads data from remote
    end point if needed.
    """
    status = etl.ETL()  # load data if not already loaded
    # query the data according to parameters given in the request
    data = queryDB(request.GET)
    # create search form populating parameters
    form = SearchForm(request.GET)
    # prepare data for Google Charts
    DP = namedtuple('DataPoint', 'd,c,i')  # each data point as namedtuple
    chart_data = tuple(DP(r.date, r.clicks, r.impressions) for r in data)
    context = {'form': form, 'chart_data': chart_data,
               'debug': ''}
    return render(request, 'etlv/index.html', context)
