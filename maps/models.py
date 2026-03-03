from django.db import models

# Create your models here.

class Location(models.Model):
    """
    A point on the campus map (classroom, block entrance, lab, etc.)
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=50, unique=True)  # e.g. "BLOCK_A_ENTRANCE", "LIBRARY"
    x = models.FloatField(default=0)   # for map drawing later
    y = models.FloatField(default=0)   # for map drawing later
    floor = models.CharField(max_length=50, blank=True)  # e.g. "Ground", "1st", etc.

    def __str__(self):
        return f"{self.name} ({self.code})"


class Edge(models.Model):
    """
    A walkable connection between two locations.
    """
    from_location = models.ForeignKey(Location, related_name='edges_from', on_delete=models.CASCADE)
    to_location = models.ForeignKey(Location, related_name='edges_to', on_delete=models.CASCADE)
    distance = models.FloatField(help_text="Distance in meters")
    bidirectional = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.from_location} -> {self.to_location} ({self.distance}m)"
