from django.contrib import admin

from .models import (Route, Station, StationSynonym, StationRoute, Time)

admin.site.register(Station)
admin.site.register(StationSynonym)
admin.site.register(StationRoute)
admin.site.register(Route)
admin.site.register(Time)
