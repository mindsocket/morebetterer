from morebetterer.models import Item
from BeautifulSoup import BeautifulSoup

user = 'roger'
url = 'http://www.redbubble.com/people/' + user + '/art?page='

page = 1
b = BeautifulSoup


"""for e in d.entries:
    imageurl = ???.replace('zzzxzzz,075,z','550x550,075,f')
    if not Item.objects.filter(itemurl=?xxx?).count():
        i = Item(itemimg = imageurl, itemurl = ?xxx?, itemname = ?yyy?)
        i.save()"""