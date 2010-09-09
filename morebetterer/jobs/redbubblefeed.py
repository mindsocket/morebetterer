from morebetterer.models import Item
import feedparser
from django_extensions.management.jobs import HourlyJob

class Job(HourlyJob):
  help = "Ranked Pairs outcome calculation and caching job."


  def execute(self):

    user = 'roger'
    feed = 'http://assets.redbubble.com/people/' + user + '/art.atom'
    d = feedparser.parse(feed)
    for e in d.entries:
      itemimg = e.enclosures[0].href.replace('300x300,075,t','550x550,075,f')
      itemurl = e.link.replace("?utm_campaign=feed&utm_medium=feed&utm_source=RB","")
      itemname = e.title
      if not Item.objects.filter(itemurl=itemurl).count():
        print "Adding " + itemname
        i = Item(itemimg = itemimg, itemurl = itemurl, itemname = itemname)
        i.save()


