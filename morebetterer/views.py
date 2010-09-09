"""Views for morebetterer application"""

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from morebetterer.models import Item, Challenge
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.cache import cache
from base64 import urlsafe_b64encode
from django.http import Http404
import hashlib
import logging
from django.conf import settings
from ratelimitcache import ratelimit_post

class ratelimit_post_morebetterer(ratelimit_post):
    """Extends the POST based rate limiting"""
    def disallowed(self, request):
        """Override to log the issue, and redirect to a proper view"""
        logging.warn('Rate limit exceeded: ' + request.META['REMOTE_ADDR'])
        resp = render_to_response('toofast.html', context_instance=RequestContext(request))
        resp.status_code = 403
        return resp

def top(request):
    """View for top items (paginated) above a threshold of challenges"""
    threshold = 10
    cachemins = 10
    topitems = cache.get('rpitems'+str(threshold), cache.get('topitems'+str(threshold)))
    if not topitems:
        topitems = Item.objects.topitems(threshold)
        cache.add('topitems'+str(threshold), topitems, cachemins * 60)
    paginator = Paginator(topitems, 20)
    
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        items = paginator.page(page)
    except (EmptyPage, InvalidPage):
        items = paginator.page(paginator.num_pages)
        
    return render_to_response('top.html', {'items': items, 'threshold': threshold, 'cachemins': cachemins}, 
        context_instance=RequestContext(request))

@ratelimit_post_morebetterer(minutes = 2, requests = 70)
def challenge(request):
    """Display random challenges and record votes"""
    ipaddress = request.META['REMOTE_ADDR']  
    
    if request.method == 'POST':
        left = request.POST['left']
        right = request.POST['right']
        expectedtoken = sign(left + ":" + right + ":" + ipaddress, settings.SECRET_KEY)
        if not request.POST['token'] == expectedtoken:
            logging.warn('Failed token check: ' + ipaddress)
            raise Http404 

        if cache.get(expectedtoken):
            logging.warn('Repeat submission: ' + ipaddress)
        else:
            cache.set(expectedtoken,"x")

            choice = request.POST['choice']
            winner = left if choice == 'left' else right  
            loser = right if choice == 'left' else left
        
            newchallenge = Challenge(winner = get_object_or_404(Item, id=winner), 
                loser = get_object_or_404(Item, id=loser), ipaddress = ipaddress)
            newchallenge.save()
        
    item1, item2 = Item.objects.candidateitems()
    #if request.user.is_authenticated() and request.method == 'POST':
    #    item2 = get_object_or_404(Item, id=winner)
    token = sign(str(item1.id) + ":" + str(item2.id) + ":" + ipaddress, settings.SECRET_KEY)
    return render_to_response('challenge.html', {'item1': item1, 'item2': item2, 'token': token},
        context_instance=RequestContext(request))
    
def about(request):
    """Vanilla "about" page"""
    return render_to_response('about.html', context_instance=RequestContext(request))
    
def sign(s, key):
    """Return a URL-safe encoded hash"""
    return uri_b64encode(hashlib.sha1(s + ':'  + key).digest())

def uri_b64encode(s):
    """Return a URL-safe b64encoded string without extraneous "=" signs"""
    return urlsafe_b64encode(s).strip('=')


