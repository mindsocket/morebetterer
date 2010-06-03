from morebetterer.models import Item
from mechanize import Browser
from BeautifulSoup import BeautifulSoup
import cgi
import time

def scraperedbubble(pagenum=1):
    mech = Browser()
#    mech.set_proxies({"http":"localhost:3129"})
    user = 'roger'
    url = 'http://www.redbubble.com/people/' + user + '/art?page='
    
    page = mech.open(url + str(pagenum))
     
    html = page.read()
    soup = BeautifulSoup(html)
    """
     <div id="works" class="images"> 
        <ul> 
            <li> 
        <span class="work-cell"> 
            <span class="work-info"> 
                <a href="/people/roger/art/5251040-1-wentworth-park-wandering" title="Wentworth Park Wandering by Roger Barnes"><img alt="Wentworth Park Wandering by Roger Barnes" src="http://ih0.redbubble.net/work.5251040.1.flat,135x135,075,f.jpg" /></a>            <span class="title"><a href="/people/roger/art/5251040-1-wentworth-park-wandering" title="Wentworth Park Wandering">Wentworth Park Wa...</a></span> 
            </span> 
        </span> 
    </li><li> 
        <span class="work-cell"> 
            <span class="work-info"> 
                <a href="/people/roger/art/5237728-1-wentworth-park-wandering" title="Wentworth Park Wandering by Roger Barnes"><img alt="Wentworth Park Wandering by Roger Barnes" src="http://ih1.redbubble.net/work.5237728.1.flat,135x135,075,f.jpg" /></a>            <span class="title"><a href="/people/roger/art/5237728-1-wentworth-park-wandering" title="Wentworth Park Wandering">Wentworth Park Wa...</a></span> 
            </span> 
        </span> 
    </li><li> 
    """

    print soup.prettify()

    entries = soup.findAll("span", attrs={"class" : "work-info"})
    for e in entries:
        print "found an entry"
        imageurl = e.a.img['src'].replace('135x135,075,f','550x550,075,f')
        itemurl = "http://www.redbubble.com" + e.a['href']
        itemname = e.a['title'].replace(" by Roger Barnes","")

        if not Item.objects.filter(itemurl=itemurl).count():
            print "adding an entry"
            i = Item(itemimg = imageurl, itemurl = itemurl, itemname = itemname)
            i.save()

