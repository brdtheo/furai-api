from django.contrib import admin

from .models import Car, CarFeature, CarMedia

admin.site.register([Car, CarFeature, CarMedia])
