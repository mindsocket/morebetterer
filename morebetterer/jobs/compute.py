from django_extensions.management.jobs import HourlyJob
import rpvote
import signal
import os
from morebetterer.models import Item, Challenge
from django.core.cache import cache

class Job(HourlyJob):
  help = "Ranked Pairs outcome calculation and caching job."


  def execute(self):
    threshold = 7
    items = Item.objects.values_list('id', flat=True)
    contest = rpvote.Contest([str(item) for item in items])
    challenges = Challenge.objects.values_list('winner','loser')
    for i in challenges:
        contest.addballot([[str(i[0])],[str(i[1])]])

    contest.computemargins()


    def handle_pdb(sig, frame):
        import pdb
        pdb.Pdb().set_trace(frame)

    signal.signal(signal.SIGUSR1, handle_pdb)
    print(os.getpid())

    #import cProfile
    #cProfile.runctx('contest.compute()',globals(),locals())

    outcome = contest.compute()

    res = outcome.result()

    ls = list(outcome.entries)

    def func(key1, key2):
        # Sorting function
        (w1,l1,t1) = res[key1]
        (w2,l2,t2) = res[key2]
        val = cmp((w2,t2), (w1,t1))
        return val

    ls.sort(func)

    cache.set('rpitems'+str(threshold), sorted(Item.objects.all().filter(challengecount__gte=threshold),key=lambda item : ls.index(str(item.id))))

