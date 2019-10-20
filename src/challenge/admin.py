from django.contrib import admin
from .models import AdvData, CampaignDim, DatasourceDim

# Register your models here.
admin.site.register(AdvData)
admin.site.register(CampaignDim)
admin.site.register(DatasourceDim)
