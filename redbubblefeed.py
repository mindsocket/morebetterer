from morebetterer.models import Item
import feedparser

user = 'roger'
feed = 'http://assets.redbubble.com/people/' + user + '/art.atom'
d = feedparser.parse(feed)
for e in d.entries:
    imageurl = e.enclosures[0].href.replace('300x300,075,t','550x550,075,f')
    if not Item.objects.filter(itemurl=e.link).count():
        i = Item(itemimg = imageurl, itemurl = e.link, itemname = e.title)
        i.save()