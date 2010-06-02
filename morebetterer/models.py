from django.db import models
from django.contrib import admin
from datetime import datetime
from django.db.models.query import QuerySet
from django.db.models import Avg

class ItemQuerySet(QuerySet):
    def underchallengeditems(self):
        average = Item.objects.all().aggregate(Avg('challengecount'))['challengecount__avg']
        return self.filter(challengecount__lte = average) 

class ItemManager(models.Manager):
    def get_query_set(self):
        return ItemQuerySet(self.model)

    def underchallengeditems(self):
        return self.get_query_set().underchallengeditems()

    def candidateitems(self):
        item1 = Item.objects.underchallengeditems().order_by('?')[0]
        item2 = Item.objects.exclude(id=item1.id).order_by('?')[0]
        return (item1, item2)

class Item(models.Model):
    objects = ItemManager()
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

    def __unicode__(self):
        return self.winner.itemname + ' beat ' + self.loser.itemname

