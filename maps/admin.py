from django.contrib import admin

# Register your models here.
from .models import Location, Edge

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'floor', 'x', 'y')
    search_fields = ('name', 'code', 'floor')

@admin.register(Edge)
class EdgeAdmin(admin.ModelAdmin):
    list_display = ('from_location', 'to_location', 'distance', 'bidirectional')
    list_filter = ('bidirectional',)