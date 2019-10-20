import datetime

from django.test import TestCase
from django.http import QueryDict

from .models import AdvData, DatasourceDim, CampaignDim, DateDim
from .etl import extract, transform, load
from .views import queryDB


class EtlTests(TestCase):

    def test_extract_from_file(self):
        """
        extract() reads the data lines correctly
        """
        with open('challenge/test.csv', 'rb') as f:
            data = extract(f)
        data = list(data)  # materialize the iterator for test
        
        self.assertEqual(len(data), 4)
        self.assertEqual(data[1][3], '10200')
        self.assertEqual(data[3][0], '30.5.2019')

    def test_transform_from_csv(self):
        """
        transform() creates model objects correctly
        """
        with open('challenge/test.csv', 'rb') as f:
            data = transform(extract(f))
        data = list(data)  # materialize the iterator for test

        self.assertIsInstance(data[0], AdvData)
        self.assertEqual(data[0].clicks, 200)
        self.assertEqual(data[2].impressions, 450)
        self.assertIsInstance(data[1].campaign, CampaignDim)
        self.assertIsInstance(data[3].datasource, DatasourceDim)
        self.assertEqual(data[0].datasource.name, "Facebook 1")
        self.assertEqual(data[2].campaign.name, "Campaign 3")
        self.assertIsInstance(data[2].date, DateDim)
        self.assertEqual(data[1].date.date, datetime.date(2019, 1, 1))
        self.assertEqual(data[3].date.date, datetime.date(2019, 5, 30))
        # check the dimension objects are the same (same identity)
        self.assertIs(data[0].date, data[1].date)
        self.assertIs(data[0].datasource, data[1].datasource)

    def test_load_into_db(self):
        """
        load() puts data in tables properly
        """
        with open('challenge/test.csv', 'rb') as f:
            load(transform(extract(f)))
        
        qs1 = AdvData.objects.all()
        qs2 = DatasourceDim.objects.all()
        qs3 = CampaignDim.objects.all()

        self.assertEqual(len(qs1), 4)
        self.assertEqual(len(qs2), 3)
        self.assertEqual(len(qs3), 4)


class ViewTests(TestCase):
    
    def test_query_aggregate(self):
        """
        queryDB() selects and aggregates data properly
        """
        with open('challenge/test.csv', 'rb') as f:
            load(transform(extract(f)))
        qs0 = queryDB(QueryDict('datasource=3&campaign=1'))
        qs1 = queryDB(QueryDict('datasource=2&campaign=3'))
        qs2 = queryDB(QueryDict('datasource=1&campaign=1&campaign=2'))
        qs3 = queryDB(QueryDict(''))
        
        self.assertEqual(len(qs0), 0)  # no records

        self.assertEqual(len(qs1), 1)
        self.assertEqual(qs1[0].clicks, 10)
        self.assertEqual(qs1[0].impressions, 450)

        self.assertEqual(len(qs2), 1)
        self.assertEqual(qs2[0].clicks, 10400)
        self.assertEqual(qs2[0].impressions, 762000)

        self.assertEqual(len(qs3), 3)
        self.assertEqual(qs3[2].clicks, 20)
        self.assertEqual(qs3[2].impressions, 12500)

