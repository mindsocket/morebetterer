from __future__ import division
from django.db import models
from django.contrib import admin
from datetime import datetime
from django.core.cache import cache
from django.db.models.query import QuerySet
from django.db.models import Avg
import rpvote

class ItemQuerySet(QuerySet):
    def underchallengeditems(self):
        average = cache.get('average',Item.objects.all().aggregate(Avg('challengecount'))['challengecount__avg'])
        cache.add('average', average, 30 * 60)

        return self.filter(challengecount__lte = average)
    
    def topitems(self,threshold):
        #return self.filter(challengecount__gte=threshold).extra(select={'score': 'cast(wincount as real) / challengecount'}).extra(order_by= ['-score','-challengecount']) 
        items = Item.objects.values_list('id', flat=True)
        contest = rpvote.Contest([str(item) for item in items])
        challenges = Challenge.objects.values_list('winner','loser')
        for i in challenges:
            contest.addballot([[str(i[0])],[str(i[1])]])

        contest.computemargins()
        outcome = contest.compute()
        outcome.printresult()

        res = outcome.result()

        ls = list(outcome.entries)

        def func(key1, key2):
            # Sorting function
            (w1,l1,t1) = res[key1]
            (w2,l2,t2) = res[key2]
            val = cmp((w2,t2), (w1,t1))
            return val

        ls.sort(func)

        return sorted(self.filter(challengecount__gte=threshold),key=lambda item : ls.index(str(item.id)))


class ItemManager(models.Manager):
    def get_query_set(self):
        return ItemQuerySet(self.model)

    def underchallengeditems(self):
        return self.get_query_set().underchallengeditems()

    def topitems(self,threshold=5):
        return self.get_query_set().topitems(threshold)

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
    
    def __unicode__(self):
        return self.itemname

class Challenge(models.Model):
    winner = models.ForeignKey(Item, related_name='winner')
    loser = models.ForeignKey(Item, related_name='loser')
    timestamp = models.DateTimeField(default=datetime.now)
    ipaddress = models.IPAddressField()

    def save(self, **kwargs):
        winneritem = Item.objects.get(id=self.winner.id)
        winneritem.wincount += 1
        winneritem.challengecount += 1
        winneritem.save()
        loseritem = Item.objects.get(id=self.loser.id)
        loseritem.challengecount += 1
        loseritem.save()
        super(Challenge, self).save(**kwargs)

    def __unicode__(self):
        return '"' + self.winner.itemname + '" beat "' + self.loser.itemname + '"'
