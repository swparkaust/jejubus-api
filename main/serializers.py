from rest_framework import serializers

from .models import Route, Station, StationRoute, Time


class RouteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Route
        fields = ('route_type', 'route_id', 'route_number')


class StationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Station
        fields = ('local_x', 'local_y', 'station_id', 'station_name')


class StationRouteSerializer(serializers.HyperlinkedModelSerializer):
    route_id = serializers.CharField(source='route.route_id')
    station_id = serializers.CharField(source='station.station_id')

    class Meta:
        model = StationRoute
        fields = ('route_id', 'station_id',
                  'station_order', 'up_down_direction')


class TimeSerializer(serializers.HyperlinkedModelSerializer):
    route_id = serializers.CharField(source='station_route.route.route_id')
    station_id = serializers.CharField(
        source='station_route.station.station_id')
    up_down_direction = serializers.CharField(
        source='station_route.up_down_direction')

    class Meta:
        model = Time
        fields = ('holiday_type', 'route_id', 'station_id',
                  'up_down_direction', 'time')
