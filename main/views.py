from rest_framework import viewsets

from .serializers import RouteSerializer, StationSerializer, StationRouteSerializer, TimeSerializer
from .models import Route, Station, StationRoute, Time


class RouteViewSet(viewsets.ModelViewSet):
    serializer_class = RouteSerializer
    http_method_names = ['get']

    def get_queryset(self):
        queryset = Route.objects.all()
        route_type = self.request.query_params.get('route_type', None)
        route_number = self.request.query_params.get('route_number', None)
        if route_type is not None:
            queryset = queryset.filter(route_type=route_type)
        if route_number is not None:
            queryset = queryset.filter(route_number=route_number)
        queryset = queryset.order_by('route_number')
        return queryset


class StationViewSet(viewsets.ModelViewSet):
    serializer_class = StationSerializer
    http_method_names = ['get']

    def get_queryset(self):
        queryset = Station.objects.all()
        station_name = self.request.query_params.get('station_name', None)
        if station_name is not None:
            queryset = queryset.filter(station_name=station_name)
        queryset = queryset.order_by('station_name')
        return queryset


class StationRouteViewSet(viewsets.ModelViewSet):
    serializer_class = StationRouteSerializer
    http_method_names = ['get']

    def get_queryset(self):
        queryset = StationRoute.objects.all()
        route_id = self.request.query_params.get('route_id', None)
        station_id = self.request.query_params.get('station_id', None)
        station_order = self.request.query_params.get('station_order', None)
        if route_id is not None:
            queryset = queryset.filter(route__route_id=route_id)
        if station_id is not None:
            queryset = queryset.filter(station__station_id=station_id)
        if station_order is not None:
            queryset = queryset.filter(station_order=station_order)
        queryset = queryset.order_by('station_order')
        return queryset


class TimeViewSet(viewsets.ModelViewSet):
    serializer_class = TimeSerializer
    http_method_names = ['get']

    def get_queryset(self):
        queryset = Time.objects.all()
        route_id = self.request.query_params.get('route_id', None)
        station_id = self.request.query_params.get('station_id', None)
        if route_id is not None:
            queryset = queryset.filter(station_route__route__route_id=route_id)
        if station_id is not None:
            queryset = queryset.filter(
                station_route__station__station_id=station_id)
        queryset = queryset.order_by('time')
        return queryset
