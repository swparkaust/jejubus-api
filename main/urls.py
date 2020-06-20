from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'routes', views.RouteViewSet, basename='route')
router.register(r'stations', views.StationViewSet, basename='station')
router.register(r'stationroutes', views.StationRouteViewSet,
                basename='stationroute')
router.register(r'times', views.TimeViewSet, basename='time')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
