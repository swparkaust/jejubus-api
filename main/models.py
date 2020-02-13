from django.db import models


class Station(models.Model):
	station_id = models.CharField(max_length=30, primary_key=True)
	station_name = models.CharField(max_length=30)
	
	def __str__(self):
		return self.station_id + '|' + self.station_name
        
        
class StationOtherName(models.Model):
    station_id = models.CharField(max_length=30)
    other_station_name = models.CharField(max_length=30)
    
    def __str__(self):
        return self.station_id + '|' + self.other_station_name
													 
													 
class Route(models.Model):
	route_type = models.CharField(max_length=20)
	route_id = models.CharField(max_length=30, primary_key=True)
	route_number = models.CharField(max_length=30)
		
	def __str__(self):
		return self.route_id + '|' + self.route_number
		
		
class Time(models.Model):
	route = models.ForeignKey(Route, on_delete=models.CASCADE)
	station = models.ForeignKey(Station, on_delete=models.CASCADE)
	time = models.TimeField()
	
	def __str__(self):
		return self.time.strftime('%H:%M')
