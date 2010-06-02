from django.db import models
from django.contrib import admin

class Item(models.Model):
    itemname =  models.CharField(max_length=150)
    itemimg =  models.CharField(max_length=150)
    itemurl =  models.CharField(max_length=150)

class Challenge(models.Model):
    winner = models.ForeignKey(Item, related_name='winner')
    loser = models.ForeignKey(Item, related_name='loser')
    timestamp = models.DateTimeField()
    ipaddress = models.IPAddressField()

admin.site.register(Item)
admin.site.register(Challenge)

