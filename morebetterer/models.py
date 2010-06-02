from django.db import models
from django.contrib import admin
from datetime import datetime

class Item(models.Model):
    itemname =  models.CharField(max_length=150)
    itemimg =  models.URLField()
    itemurl =  models.URLField()
    challengecount = models.IntegerField(default=0)
    wincount = models.IntegerField(default=0)
    losscount = models.IntegerField(default=0)

    def __unicode__(self):
        return self.itemname

class Challenge(models.Model):
    winner = models.ForeignKey(Item, related_name='winner')
    loser = models.ForeignKey(Item, related_name='loser')
    timestamp = models.DateTimeField(default=datetime.now)
    ipaddress = models.IPAddressField()

    def save(self, **kwargs):
        winneritem = Item.objects.filter(id=self.winner.id)[0]
        winneritem.wincount += 1
        winneritem.challengecount += 1
        winneritem.save()
        loseritem = Item.objects.filter(id=self.loser.id)[0]
        loseritem.losscount += 1
        loseritem.challengecount += 1
        loseritem.save()
        super(Challenge, self).save(**kwargs)

admin.site.register(Item)
admin.site.register(Challenge)

