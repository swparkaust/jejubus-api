from django.contrib import admin

from .models import (Route, Station, StationOtherName, StationRoute, Time)

admin.site.register(Station)
admin.site.register(StationOtherName)
admin.site.register(StationRoute)
admin.site.register(Route)
admin.site.register(Time)
