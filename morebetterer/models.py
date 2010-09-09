from __future__ import division
from django.db import models
from django.contrib import admin
from datetime import datetime
from django.core.cache import cache
from django.db.models.query import QuerySet
from django.db.models import Avg, Min
import rpvote
import random
import bisect
import re

def runballot():
    items = Item.objects.values_list('id', flat=True)
    contest = rpvote.Contest([str(item) for item in items])
    challenges = Challenge.objects.values_list('winner', 'loser')
    for i in challenges:
        contest.addballot([[str(i[0])], [str(i[1])]])

    contest.computemargins()
    return contest.compute()

def weighted_choice_bisect_compile(items):
    """Returns a function that makes a weighted random choice from items."""
    added_weights = []
    last_sum = 0
    for item, weight in items:
        last_sum += weight
        added_weights.append(last_sum)
    def choice(rnd=random.random, bis=bisect.bisect):
        return items[bis(added_weights, rnd() * last_sum)][0]
    return choice

class ItemQuerySet(QuerySet):
    def underchallengeditems(self):
        average = cache.get('average')
        if not average:
            import logging
            logging.info('Recalculating average')
            average = Item.objects.all().aggregate(Avg('challengecount'))['challengecount__avg']
            cache.add('average', average, 30 * 60)

        #min = Item.objects.all().aggregate(Min('challengecount'))['challengecount__min']

        #return self.filter(challengecount = min)
        return self.filter(challengecount__lte = average)


    def weightedchoice(self):
        return morebetterer.models.weighted_choice_bisect_compile([(id, float(1) / (c ** 2)) for id, c in Item.objects.values_list('id', 'challengecount')])

    def topitems(self, threshold):
        import logging
        logging.info('Recalculating top items')
        return self.filter(challengecount__gte=threshold).extra(select={'score': 'cast(wincount as real) / challengecount'}).extra(order_by=['-score', '-challengecount']) 
        outcome = runballot()
        #outcome.printresult()

        res = outcome.result()

        ls = list(outcome.entries)

        def func(key1, key2):
            # Sorting function
            (w1, l1, t1) = res[key1]
            (w2, l2, t2) = res[key2]
            val = cmp((w2, t2), (w1, t1))
            return val

        ls.sort(func)

        return sorted(self.filter(challengecount__gte=threshold), key=lambda item : ls.index(str(item.id)))


class ItemManager(models.Manager):
    def get_query_set(self):
        return ItemQuerySet(self.model)

    def underchallengeditems(self):
        return self.get_query_set().underchallengeditems()

    def topitems(self, threshold=5):
        return self.get_query_set().topitems(threshold)

    def recalculateTotals(self):
        for item in self.all():
            item.wincount=item.winner.count()
            item.challengecount=item.winner.count() + item.loser.count()
            item.save()
    
    def candidateitems(self):
        #outcome.printresult()

        #ls = cache.get('candidateslist')
        #if False or not ls or len(ls) == 0:
        #    import logging
        #    logging.info('Recalculating candidateslist')
        #    outcome = runballot()
        #    res = outcome.result()
    
        #    ls = list(outcome.entries)
    
        #    def func(key1, key2):
        #        # Sorting function
        #        (w1, l1,t1) = res[key1]
        #        (w2, l2,t2) = res[key2]
        #        val = cmp((t2, w2), (t1,w1))
        #        return val
    
        #    ls.sort(func)
        #    ls = ls[:int(len(ls)/10)]

        item1 = Item.objects.underchallengeditems().order_by('?')[0]
        #item1 = Item.objects.get(id=int(ls.pop(0)))
        item2 = Item.objects.exclude(id=item1.id).order_by('?')[0]
        #cache.set('candidateslist', ls)
        return (item1, item2)
    
class Item(models.Model):
    objects = ItemManager()
    itemname =  models.CharField(max_length=150)
    itemimg =  models.URLField()
    itemurl =  models.URLField()
    challengecount = models.IntegerField(default=0)
    wincount = models.IntegerField(default=0)

    def mybubbleurl(self):
        return re.sub('people/roger', 'mybubble', self.itemurl)
    
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

class ChallengeCount(models.Model):
    ipaddress = models.IPAddressField(primary_key=True, editable=False)
    count = models.IntegerField(editable=False)

