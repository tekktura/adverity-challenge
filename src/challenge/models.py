from django.db import models

# Create your models here.


class CampaignDim(models.Model):
    """
    The 'campaign' dimension in our data model. Otherwise simply a list
    of campaign names.
    """
    name = models.CharField("Name", max_length=1024)
    
    def __str__(self):
        return self.name


class DatasourceDim(models.Model):
    """
    The 'data source' dimension in our data model. Otherwise simply a list
    of data source names.
    """
    name = models.CharField("Name", max_length=256)
    
    def __str__(self):
        return self.name


class DateDim(models.Model):
    """
    The 'date' dimension is basically only needed to properly aggregate
    data using Django QuerySets.
    """
    date = models.DateField("Date")
    
    def __str__(self):
        return self.date.isoformat()


class AdvData(models.Model):
    """
    Our main data model containing all the Adv data gathered from CSV
    source. Contains three dimensions and two metrics.
    """
    
    date = models.ForeignKey(DateDim, on_delete=models.CASCADE)
    datasource = models.ForeignKey(DatasourceDim,
                                   verbose_name="Data source",
                                   on_delete=models.CASCADE)
    campaign = models.ForeignKey(CampaignDim,
                                 verbose_name="Campaign",
                                 on_delete=models.CASCADE)
    clicks = models.IntegerField("Clicks", default=0)
    impressions = models.IntegerField("Impressions", default=0)
    
    def __str__(self):
        return "{} : {} : {} : {} : {}".format(self.date, self.datasource,
                                       self.campaign, self.clicks,
                                       self.impressions)
