# adverity-challenge
Advertising Data ETL-V challenge for tigadevs


'adverity-challenge' is a simpe Django app created for tigadevs challenge to demonstrate programming skills. 

Quick start
-----------

1. Add "challenge" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'challenge',
    ]

2. Include the challenge URLconf in your project urls.py like this::

    path('', include('challenge.urls')),

3. Run `python manage.py migrate` to create the models.

4. Start the development server and visit http://127.0.0.1:8000/
   to import CSV remote end point data and see the interactive chart.

5. You can also visit http://127.0.0.1:8000/admin/ to check the models structure and see what was imported.